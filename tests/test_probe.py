# -*- coding: utf-8 -*-
import json
import sys
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest
import requests_mock

from chaoslib.exceptions import ActivityFailed, InvalidActivity
from chaoslib.activity import ensure_activity_is_valid, run_activity

from fixtures import config, experiments, probes
from test_validation import assert_in_errors


def test_empty_probe_is_invalid():
    errors = ensure_activity_is_valid(probes.EmptyProbe)
    assert_in_errors("empty activity is no activity", errors)


def test_probe_must_have_a_type():
    errors = ensure_activity_is_valid(probes.MissingTypeProbe)
    assert_in_errors("an activity must have a type", errors)


def test_probe_must_have_a_known_type():
    errors = ensure_activity_is_valid(probes.UnknownTypeProbe)
    assert_in_errors("'whatever' is not a supported activity type", errors)


def test_probe_provider_must_have_a_known_type():
    errors = ensure_activity_is_valid(probes.UnknownProviderTypeProbe)
    assert_in_errors("unknown provider type 'pizza'", errors)


def test_python_probe_must_have_a_module_path():
    errors = ensure_activity_is_valid(probes.MissingModuleProbe)
    assert_in_errors("a Python activity must have a module path", errors)


def test_python_probe_must_have_a_function_name():
    errors = ensure_activity_is_valid(probes.MissingFunctionProbe)
    assert_in_errors("a Python activity must have a function name", errors)


def test_python_probe_must_be_importable():
    errors = ensure_activity_is_valid(probes.NotImportableModuleProbe)
    assert_in_errors("could not find Python module 'fake.module'", errors)


def test_python_probe_func_must_have_enough_args():
    errors = ensure_activity_is_valid(probes.MissingFuncArgProbe)
    assert_in_errors("required argument 'path' is missing", errors)


def test_python_probe_func_cannot_have_too_many_args():
    errors = ensure_activity_is_valid(probes.TooManyFuncArgsProbe)
    assert_in_errors(
        "argument 'should_not_be_here' is not part of the function signature",
        errors)


def test_process_probe_have_a_path():
    errors = ensure_activity_is_valid(probes.MissingProcessPathProbe)
    assert_in_errors("a process activity must have a path", errors)


def test_process_probe_path_must_exist():
    errors = ensure_activity_is_valid(probes.ProcessPathDoesNotExistProbe)
    assert_in_errors("path 'somewhere/not/here' cannot be found, in activity", errors)


def test_http_probe_must_have_a_url():
    errors = ensure_activity_is_valid(probes.MissingHTTPUrlProbe)
    assert_in_errors("a HTTP activity must have a URL", errors)


def test_run_python_probe_should_return_raw_value():
    # our probe checks a file exists
    assert run_activity(
        probes.PythonModuleProbe, config.EmptyConfig,
        experiments.Secrets) is True


def test_run_process_probe_should_return_raw_value():
    v = "Python {v}\n".format(v=sys.version.split(" ")[0])

    result = run_activity(
        probes.ProcProbe, config.EmptyConfig, experiments.Secrets)
    assert type(result) is dict
    assert result["status"] == 0
    assert result["stdout"] == v
    assert result["stderr"] == ''


def test_run_process_probe_should_pass_arguments_in_array():
    args = "['-c', '--empty', '--number', '1', '--string', 'with spaces', '--string', 'a second string with the same option']\n"

    result = run_activity(
        probes.ProcEchoArrayProbe, config.EmptyConfig, experiments.Secrets)
    assert type(result) is dict
    assert result["status"] == 0
    assert result["stdout"] == args
    assert result["stderr"] == ''


def test_run_process_probe_can_pass_arguments_as_string():
    args = "['-c', '--empty', '--number', '1', '--string', 'with spaces', '--string', 'a second string with the same option']\n"

    result = run_activity(
        probes.ProcEchoStrProbe, config.EmptyConfig, experiments.Secrets)
    assert type(result) is dict
    assert result["status"] == 0
    assert result["stdout"] == args
    assert result["stderr"] == ''


def test_run_process_probe_can_timeout():
    probe = probes.ProcProbe
    probe["provider"]["timeout"] = 0.0001

    with pytest.raises(ActivityFailed) as exc:
        run_activity(
            probes.ProcProbe, config.EmptyConfig,
            experiments.Secrets).decode("utf-8")
    assert "activity took too long to complete" in str(exc.value)


def test_run_http_probe_should_return_parsed_json_value():
    with requests_mock.mock() as m:
        headers = {"Content-Type": "application/json"}
        m.post(
            'http://example.com', json=['well done'], headers=headers)
        result = run_activity(
            probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert result["body"] == ['well done']


def test_run_http_probe_must_be_serializable_to_json():
    with requests_mock.mock() as m:
        headers = {"Content-Type": "application/json"}
        m.post(
            'http://example.com', json=['well done'], headers=headers)
        result = run_activity(
            probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert json.dumps(result) is not None


def test_run_http_probe_should_return_raw_text_value():
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', text="['well done']")
        result = run_activity(
            probes.HTTPProbe, config.EmptyConfig, experiments.Secrets)
        assert result["body"] == "['well done']"


def test_run_http_probe_can_expect_failure():
    with requests_mock.mock() as m:
        m.post(
            'http://example.com', status_code=404, text="Not found!")

        probe = probes.HTTPProbe.copy()
        probe['provider']["expected_status"] = 404

        try:
            run_activity(probe, config.EmptyConfig, experiments.Secrets)
        except ActivityFailed:
            pytest.fail("activity should not have failed")


def test_run_http_probe_can_retry():
    """
    this test embeds a fake HTTP server to test the retry part
    it can't be easily tested with libraries like requests_mock or responses
    we could mock urllib3 retry mechanism as it is used in the requests library but it implies to
    understand how requests works which is not the idea of this test

    in this test, the first call will lead to a ConnectionAbortedError and the second will work
    """
    class MockServerRequestHandler(BaseHTTPRequestHandler):
        """
        mock of a real HTTP server to simulate the behavior of
        a connection aborted error on first call
        """
        call_count = 0
        def do_GET(self):
            MockServerRequestHandler.call_count += 1
            if MockServerRequestHandler.call_count == 1:
                raise ConnectionAbortedError
            self.send_response(200)
            self.end_headers()
            return

    # get a free port to listen on
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()

    # start the fake HTTP server in a dedicated thread on the selected port
    server = HTTPServer(('localhost', port), MockServerRequestHandler)
    t = Thread(target=server.serve_forever)
    t.setDaemon(True)
    t.start()

    # change probe URL to call the selected port
    probe = probes.PythonModuleProbeWithHTTPMaxRetries.copy()
    probe["provider"]["url"] = "http://localhost:{}".format(port)
    try:
        run_activity(probe, config.EmptyConfig, experiments.Secrets)
    except ActivityFailed:
        pytest.fail("activity should not have failed")
