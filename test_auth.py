import os
import pytest
import argparse
from shelly_ota.auth import AuthProvider
from shelly_ota.shelly import ShellyDevice

@pytest.fixture
def empty_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auth_env')
    parser.add_argument('--auth_file')
    args = parser.parse_args()
    return args

@pytest.fixture
def simple_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auth_env', default=None)
    parser.add_argument('--auth_file', default=None)
    os.environ["TEST_AUTH"] = "user:pass"
    args = parser.parse_args(args=["--auth_env", "TEST_AUTH"])
    return args

@pytest.fixture
def no_auth_provider(empty_args):
    return AuthProvider(empty_args)

@pytest.fixture
def simple_auth_provider(simple_args):
    return AuthProvider(simple_args)

@pytest.fixture
def dummy_device():
    return ShellyDevice('00:00:00:00:00:00', {})

def test_no_auth(no_auth_provider):
    assert no_auth_provider is not None
    assert no_auth_provider.get_auth_for(None) == None

def test_simple_auth(simple_auth_provider, dummy_device):
    print(dummy_device)
    assert simple_auth_provider.get_auth_for(dummy_device) == ('user', 'pass')
