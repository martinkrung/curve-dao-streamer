import ape
import pytest

@pytest.fixture(scope="session")
def alice(accounts):
    return accounts[0]

@pytest.fixture(scope="session")
def bob(accounts):
    return accounts[2]

@pytest.fixture(scope="session")
def charlie(accounts):
    return accounts[3]