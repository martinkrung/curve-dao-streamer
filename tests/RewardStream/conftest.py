import ape
import pytest

@pytest.fixture(scope="module")
def reward_token(project, alice):
    return alice.deploy(project.TestToken)

@pytest.fixture(scope="function")
def stream(project, alice, bob, reward_token):
    contract = alice.deploy(project.RewardStream, alice, bob, reward_token, 86400 * 10)
    #reward_token.mint(bob, 10 ** 19, sender=bob)

    #reward_token.approve(contract, 2 ** 256 - 1, sender=bob )
    return contract

'''from brownie_tokens import ERC20
@pytest.fixture(scope="module")
def reward_token(bob):
    token = ERC20()
    token._mint_for_testing(bob, 10 ** 19)
    return token

'''
