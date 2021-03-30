# -*- coding: utf-8 -*-
import os

from hvac.exceptions import InvalidRequest
import pytest
from chaoslib.exceptions import InvalidExperiment
from chaoslib.secret import load_secrets, load_secrets_from_vault, \
    create_vault_client
from fixtures import config
from unittest.mock import ANY, MagicMock, patch, mock_open

@patch.dict(os.environ, {"KUBE_API_URL": "http://1.2.3.4"})
def test_should_load_environment():
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": {
                "type": "env",
                "key": "KUBE_API_URL"
            }
        }
    }, config.EmptyConfig)
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


def test_should_load_inline():
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": "http://1.2.3.4"
        }
    }, config.EmptyConfig)
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"

@patch.dict(os.environ, {"KUBE_API_URL": "http://1.2.3.4"})
def test_should_merge_properly():
    secrets = load_secrets({
        "kubernetes": {
            "username": "jane",
            "address": {"host": "whatever", "port": 8090},
            "api_server_url": {
                "type": "env",
                "key": "KUBE_API_URL"
            }
        }
    }, config.EmptyConfig)
    assert secrets["kubernetes"]["username"] == "jane"
    assert secrets["kubernetes"]["address"]["host"] == "whatever"
    assert secrets["kubernetes"]["address"]["port"] == 8090
    assert secrets["kubernetes"]["api_server_url"] == "http://1.2.3.4"


@patch('chaoslib.secret.hvac')
def test_should_auth_with_approle(hvac):
    config = {
        'vault_addr' : 'http://someaddr.com',
        'vault_role_id' : 'mighty_id',
        'vault_role_secret' : 'secret_secret'
    }

    fake_auth_object = {
        'auth' : {
            'client_token' : 'awesome_token'
        }
    }

    fake_client = MagicMock()
    fake_client.auth_approle.return_value = fake_auth_object
    hvac.Client.return_value = fake_client

    vault_client = create_vault_client(config)

    assert vault_client.token == fake_auth_object['auth']['client_token']
    fake_client.auth_approle.assert_called_with(config['vault_role_id'], config['vault_role_secret'])


@patch('chaoslib.secret.hvac')
def test_should_catch_approle_invalid_secret_id_abort_the_run(hvac):
    config = {
        'vault_addr' : 'http://someaddr.com',
        'vault_role_id' : 'mighty_id',
        'vault_role_secret' : 'expired'
    }

    fake_client = MagicMock()
    fake_client.auth_approle.side_effect = InvalidRequest()
    hvac.Client.return_value = fake_client

    with pytest.raises(InvalidExperiment):
        create_vault_client(config)


@patch('chaoslib.secret.hvac')
def test_should_auth_with_token(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_token': 'not_awesome_token',
        'vault_kv_version': '1'
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client

    vault_client = create_vault_client(config)

    assert vault_client.token == config['vault_token']
    fake_client.auth_approle.assert_not_called()


@patch('chaoslib.secret.hvac', autospec=True)
def test_should_auth_with_service_account(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_sa_role': 'some_role',
        'vault_k8s_mount_point': 'not_kubernetes',
        'vault_kv_version': '1'
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client


    with patch('chaoslib.secret.open', mock_open(read_data="fake_sa_token")):
        vault_client = create_vault_client(config)
        vault_client.auth_approle.assert_not_called()
        vault_client.auth_kubernetes.assert_called_with(
            role=config['vault_sa_role'], jwt='fake_sa_token', use_token=True,
            mount_point=config['vault_k8s_mount_point'])


@patch('chaoslib.secret.hvac')
def test_should_catch_service_account_invalid_abort_the_run(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_sa_role': 'invalid',
        'vault_kv_version': '1'
    }

    fake_client = MagicMock()
    fake_client.auth_kubernetes.side_effect = InvalidRequest()
    hvac.Client.return_value = fake_client

    with pytest.raises(InvalidExperiment):
        create_vault_client(config)


@patch('chaoslib.secret.hvac')
def test_read_secrets_from_vault_with_kv_version_1(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_token': 'not_awesome_token',
        'vault_kv_version': '1'
    }

    secrets_info = {
        "k8s": {
            "a-secret": {
                "type": "vault",
                "path": "foo/stuff"
            }
        }
    }

    # secret at secret/foo
    vault_secret_payload = {
        "auth": None,
        "data": {
            "my-important-secret": "bar",
            "my-less-important-secret": "baz"
        },
        "lease_duration": 2764800,
        "lease_id": "",
        "renewable": False
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client
    fake_client.secrets.kv.v1.read_secret.return_value = vault_secret_payload

    secrets = load_secrets_from_vault(secrets_info, config)
    assert secrets["k8s"]["a-secret"] == {
        "my-important-secret": "bar",
        "my-less-important-secret": "baz"
    }

    secrets_info = {
        "k8s": {
            "a-secret": {
                "type": "vault",
                "path": "foo/stuff",
                "key": "my-important-secret"
            }
        }
    }

    secrets = load_secrets_from_vault(secrets_info, config)
    assert secrets["k8s"]["a-secret"] == "bar"


@patch('chaoslib.secret.hvac')
def test_read_secrets_from_vault_with_kv_version_2(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_token': 'not_awesome_token',
        'vault_kv_version': '2'
    }

    secrets_info = {
        "k8s": {
            "a-secret": {
                "type": "vault",
                "path": "foo/stuff"
            }
        }
    }

    # secret at secret/foo
    vault_secret_payload = {
        "data": {
            "data": {
                "my-important-secret": "bar",
                "my-less-important-secret": "baz"
            },
            "metadata": {
                "auth": None,
                "lease_duration": 2764800,
                "lease_id": "",
                "renewable": False
            }
        }
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client
    fake_client.secrets.kv.v2.read_secret_version.return_value = vault_secret_payload

    secrets = load_secrets_from_vault(secrets_info, config)
    assert secrets["k8s"]["a-secret"] == {
        "my-important-secret": "bar",
        "my-less-important-secret": "baz"
    }

    secrets_info = {
        "k8s": {
            "a-secret": {
                "type": "vault",
                "path": "foo/stuff",
                "key": "my-important-secret"
            }
        }
    }

    secrets = load_secrets_from_vault(secrets_info, config)
    assert secrets["k8s"]["a-secret"] == "bar"

@patch.dict(os.environ, {"KUBE_API_URL": "http://1.2.3.4"})
def test_override_load_environmen_with_var():
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": {
                "type": "env",
                "key": "KUBE_API_URL"
            }
        }
    }, config.EmptyConfig, 
    {
        "kubernetes": {
            "api_server_url": "http://elsewhere"
        }
    })
    assert secrets["kubernetes"]["api_server_url"] == "http://elsewhere"


def test_should_override_load_inline_with_var():
    secrets = load_secrets({
        "kubernetes": {
            "api_server_url": "http://1.2.3.4"
        }
    }, config.EmptyConfig,
    {
        "kubernetes": {
            "api_server_url": "http://elsewhere"
        }
    })
    assert secrets["kubernetes"]["api_server_url"] == "http://elsewhere"


@patch('chaoslib.secret.hvac')
def test_vault_add_subkeys(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_token': 'not_awesome_token',
        'vault_kv_version': '2'
    }

    vault_secret_payload = {
        "data": {
            "data": {
                "foo": "bar",
                "baz": "hello"
            },
            "metadata": {
                "auth": None,
                "lease_duration": 2764800,
                "lease_id": "",
                "renewable": False
            }
        }
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client
    fake_client.secrets.kv.v2.read_secret_version.return_value = vault_secret_payload

    secrets = load_secrets({
        "myapp": {
            "token": {
                "type": "vault",
                "path": "secrets/something"
            }
        }
    }, config)
    assert secrets["myapp"]["token"]["foo"] == "bar"
    assert secrets["myapp"]["token"]["baz"] == "hello"

@patch('chaoslib.secret.hvac')
def test_vault_replace_entire_declare(hvac):
    config = {
        'vault_addr': 'http://someaddr.com',
        'vault_token': 'not_awesome_token',
        'vault_kv_version': '2'
    }

    vault_secret_payload = {
        "data": {
            "data": {
                "foo": "bar",
                "baz": "hello"
            },
            "metadata": {
                "auth": None,
                "lease_duration": 2764800,
                "lease_id": "",
                "renewable": False
            }
        }
    }

    fake_client = MagicMock()
    hvac.Client.return_value = fake_client
    fake_client.secrets.kv.v2.read_secret_version.return_value = vault_secret_payload

    secrets = load_secrets({
        "myapp": {
            "token": {
                "type": "vault",
                "path": "secrets/something",
                "key": "foo"
            }
        }
    }, config)
    assert secrets["myapp"]["token"] == "bar"

