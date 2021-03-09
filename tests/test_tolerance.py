# -*- coding: utf-8 -*-
import pytest
import sys

from chaoslib.exceptions import InvalidActivity
from chaoslib.hypothesis import ensure_hypothesis_tolerance_is_valid, \
    within_tolerance


def test_tolerance_int():
    assert within_tolerance(6, value=6) is True


def test_tolerance_int_returns_false_when_different():
    assert within_tolerance(6, value=7) is False


def test_tolerance_int_from_process_status():
    assert within_tolerance(6, value={"status": 6}) is True


def test_tolerance_int_from_process_status_returns_false_when_different():
    assert within_tolerance(6, value={"status": 7}) is False


def test_tolerance_int_from_http_status():
    assert within_tolerance(6, value={"status": 6}) is True


def test_tolerance_int_from_http_status_returns_false_when_different():
    assert within_tolerance(6, value={"status": 7}) is False


def test_tolerance_list_int_from_process_status():
    assert within_tolerance([5, 6], value={"status": 6}) is True


def test_tolerance_list_int_from_process_status_returns_false_when_different():
    assert within_tolerance([5, 7], value={"status": 6}) is False


def test_tolerance_list_int_from_http_status():
    assert within_tolerance([5, 6], value={"status": 6}) is True


def test_tolerance_list_int_from_http_status_returns_false_when_different():
    assert within_tolerance([5, 7], value={"status": 6}) is False


def test_tolerance_bool():
    assert within_tolerance(True, value=True) is True


def test_tolerance_bool_returns_false_when_different():
    assert within_tolerance(True, value=False) is False


def test_tolerance_string():
    assert within_tolerance("hello", value="hello") is True


def test_tolerance_string_returns_false_when_different():
    assert within_tolerance("hello", value="not hello") is False


def test_tolerance_string():
    assert within_tolerance("hello", value="hello") is True


def test_tolerance_string_returns_false_when_different():
    assert within_tolerance("hello", value="not hello") is False


def test_tolerance_regex():
    assert within_tolerance(
        {
            "type": "regex",
            "pattern": "[0-9]{2}"
        },
        value="you are number 87"
    ) is True


def test_tolerance_regex():
    t = {
        "type": "regex",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value="you are number 8") is False


def test_tolerance_jsonpath_from_dict():
    t = {
        "type": "jsonpath",
        "path": "$.foo.*[?(@.baz)]"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is True


def test_tolerance_jsonpath_must_find_items_to_succeed():
    t = {
        "type": "jsonpath",
        "path": "$.notsofoo.*[?(@.baz)].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is False


def test_tolerance_jsonpath_must_match_expected_value():
    t = {
        "type": "jsonpath",
        "path": "$.foo[?(@.baz)].baz",
        "expect": "hello"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": "hello"}
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo[?(@.baz)].baz",
        "expect": [["hello", "bonjour"]]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": ["hello", "bonjour"]}
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo[?(@.baz)].baz",
        "expect": [["hello", "bonjour"]],
        "expect_one_of": [["hello", "joe"]]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": ["hello", "joe"]}
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo[?(@.baz)].baz",
        "expect": [[["hello"], ["bonjour"]]]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": [["hello"], ["bonjour"]]}
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo[?(@.baz)].baz",
        "expect": [[["hello"], ["bonjour"]]],
        "expect_one_of": [[["hello"], ["joe"]]]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": [["hello"], ["joe"]]}
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo[?(@.baz)].baz",
        "expect": []
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"jon": "boom"}
        }
    ) is True


def test_tolerance_jsonpath_can_be_filter_by_value():
    t = {
        "type": "jsonpath",
        "path": '$.foo[?(@.baz="hello")]',
        "count": 1
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": "hello"}
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": '$.foo[?(@.baz="bonjour")]',
        "count": 1
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": "hello"}
        }
    ) is False


def test_tolerance_jsonpath_must_match_expected_values():
    t = {
        "type": "jsonpath",
        "path": "$.foo.*[?(@.baz)].baz",
        "expect": ["hello", "bonjour"]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{"baz": "hello"}, {"baz": "bonjour"}]
        },
    ) is True


def test_tolerance_jsonpath_must_find_items_with_a_given_value_to_succeed():
    t = {
        "type": "jsonpath",
        "path": '$.foo.*[?(@.baz=2)]',
        "count": 1
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo.*[?(@.baz)]",
        "count": 2
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 1}, {'baz': 2}]
        }) is True

    t = {
        "type": "jsonpath",
        "path": "$.foo.*[?(@.baz=4)]",
        "count": 2
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': [{'baz': 4}, {'baz': 4}]
        }) is True


def test_tolerance_jsonpath_from_jsonstring():
    t = {
        "type": "jsonpath",
        "path": "$.foo[*].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value='{"foo": [{"baz": 1}, {"baz": 2}]}') is True


def test_tolerance_jsonpath_from_bytes():
    t = {
        "type": "jsonpath",
        "path": "$.foo[*].baz"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value=b'{"foo": [{"baz": 1}, {"baz": 2}]}') is True


def test_tolerance_jsonpath_cannot_be_empty():
    t = {
        "type": "jsonpath",
        "path": ""
    }

    with pytest.raises(InvalidActivity):
        ensure_hypothesis_tolerance_is_valid(t)


def test_tolerance_regex_stdout_process():
    t = {
        "type": "regex",
        "target": "stdout",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "you are number 87",
            "stderr": ""
        }
    ) is True


def test_tolerance_regex_stdout_process_needs_to_match():
    t = {
        "type": "regex",
        "target": "stdout",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "you are number 8",
            "stderr": ""
        }
    ) is False


def test_tolerance_regex_stderr_process():
    t = {
        "type": "regex",
        "target": "stderr",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "",
            "stderr": "you are number 87"
        }
    ) is True


def test_tolerance_regex_stdout_process_needs_to_match():
    t = {
        "type": "regex",
        "target": "stderr",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "",
            "stderr": "you are number 8"
        }
    ) is False


def test_tolerance_regex_process_only_match_stdout_or_stderr():
    t = {
        "type": "regex",
        "target": "stdout",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 0,
            "stdout": "you are number 87",
            "stderr": "you are number 8"
        }
    ) is True


def test_tolerance_regex_body_http():
    t = {
        "type": "regex",
        "target": "body",
        "pattern": "[0-9]{2}"
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t,
        value={
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "you are number 87"
        }
    ) is True


def test_tolerance_regex_must_have_a_pattern():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "regex",
            "target": "stdout"
        })
    assert "tolerance must have a `pattern` key" in str(e.value)


def test_tolerance_regex_must_have_a_valid_pattern_type():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "regex",
            "target": "stdout",
            "pattern": None
        })
    assert "tolerance pattern None has an invalid type" in str(e.value)


def test_tolerance_regex_must_have_a_valid_pattern():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "regex",
            "target": "stdout",
            "pattern": "[0-9"
        })
    assert "pattern [0-9 seems invalid" in str(e.value)


def test_tolerance_unsupported_type():
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "boom"
        })
    assert "tolerance type 'boom' is unsupported" in str(e.value)


def test_tolerance_missing_jsonpath_backend():
    from chaoslib import hypothesis
    hypothesis.HAS_JSONPATH = False
    with pytest.raises(InvalidActivity) as e:
        ensure_hypothesis_tolerance_is_valid({
            "type": "jsonpath",
            "path": "whatever"
        })
    hypothesis.HAS_JSONPATH = True
    assert "Install the `jsonpath2` package to use a JSON path" in str(e.value)


def test_tolerance_range_integer():
    t = {
        "type": "range",
        "target": "body",
        "range": [10, 800]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "580"
    }) is True

    t = {
        "type": "range",
        "target": "body",
        "range": [10, 800]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "1230"
    }) is False


def test_tolerance_range_float():
    t = {
        "type": "range",
        "target": "body",
        "range": [10.5, 800.89]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "580.5"
    }) is True

    t = {
        "type": "range",
        "target": "body",
        "range": [10.5, 800.89]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "1230.7"
    }) is False


def test_tolerance_range_mix_integer_and_float():
    t = {
        "type": "range",
        "target": "body",
        "range": [10, 800.8]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "580.4"
    }) is True

    t = {
        "type": "range",
        "target": "body",
        "range": [10.5, 800]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "1230"
    }) is False


def test_tolerance_range_lower_boundary_must_be_a_number():
    t = {
        "type": "range",
        "target": "body",
        "range": ["a", 6]
    }
    with pytest.raises(InvalidActivity):
        ensure_hypothesis_tolerance_is_valid(t)


def test_tolerance_range_upper_boundary_must_be_a_number():
    t = {
        "type": "range",
        "target": "body",
        "range": [6, "b"]
    }
    with pytest.raises(InvalidActivity):
        ensure_hypothesis_tolerance_is_valid(t)


def test_tolerance_range_checked_value_must_be_a_number():
    t = {
        "type": "range",
        "target": "body",
        "range": [6, 8]
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "bad"
    }) is False


def test_tolerance_with_a_probe():
    t = {
        "type": "probe",
        "name": "must-be-in-range",
        "provider": {
            "type": "python",
            "module": "fixtures.probes",
            "func": "must_be_in_range",
            "arguments": {
                "a": 6,
                "b": 8
            }
        }
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "9"
    }) is False

    assert within_tolerance(t, value={
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "7"
    }) is True


def test_tolerance_jsonpath_can_contain_variable_to_be_substituted():
    t = {
        "type": "jsonpath",
        "path": '$.foo[?(@.baz="${msg}")]',
        "count": 1
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": "hello"}
        }, configuration={
            "msg": "hello"
        }
    ) is True

    t = {
        "type": "jsonpath",
        "path": '$.foo[?(@.baz="${msg}")]',
        "count": 1
    }
    ensure_hypothesis_tolerance_is_valid(t)
    assert within_tolerance(
        t, value={
            'foo': {"baz": "hello"}
        }, configuration={
            "msg": "bonjour"
        }
    ) is False


def test_tolerance_regex_can_contain_variable_to_be_substituted():
    assert within_tolerance(
        {
            "type": "regex",
            "pattern": "${msg}"
        },
        value="jane said hello at sunrise",
        configuration={
            "msg": "hello"
        }
    ) is True

    assert within_tolerance(
        {
            "type": "regex",
            "pattern": "${msg}"
        },
        value="jane said hello at sunrise",
        configuration={
            "msg": "bonjour"
        }
    ) is False


def test_tolerance_complex_regex_can_contain_variable_to_be_substituted():
    assert within_tolerance(
        {
            "type": "regex",
            "pattern": "^[0-9] \$\{level\} ${msg} - done$"
        },
        value="1 ${level} hello - done",
        configuration={
            "msg": "hello"
        }
    ) is True
