import ape
from ape import chain
import pytest


@pytest.fixture(autouse=True)
def module_setup(alice, bob, charlie, stream, reward_token):
    stream.add_receiver(charlie, sender = alice)
    stream.notify_reward_amount(10 ** 18, sender = bob)
    chain.pending_timestamp += 86400 * 10


def test_receiver_deactivates(alice, charlie, stream):
    pre_remove = stream.reward_receivers(charlie)
    
    assert stream.reward_ratio(charlie) == 100
    
    stream.remove_receiver(charlie, sender = alice)
    
    receivers = stream.receivers()

    assert pre_remove is True
    assert stream.reward_receivers(charlie) is False


def test_receiver_ratio_decreases(alice, charlie, dora, stream):
    stream.add_receiver(dora, sender = alice)

    assert stream.reward_ratio(charlie) == 50
    assert stream.reward_ratio(dora) == 50

    pre_remove = stream.reward_receivers(charlie)
    stream.remove_receiver(charlie, sender = alice)
    
    assert pre_remove is True
    assert stream.reward_receivers(charlie) is False

    assert stream.reward_ratio(dora) == 100

def test_receiver_ratio_decreases_reverse(alice, charlie, dora, stream):
    stream.add_receiver(dora, sender = alice)

    assert stream.reward_ratio(charlie) == 50
    assert stream.reward_ratio(dora) == 50

    pre_remove = stream.reward_receivers(dora)
    stream.remove_receiver(dora, sender = alice)

    assert pre_remove is True
    assert stream.reward_receivers(dora) is False

    assert stream.reward_ratio(charlie) == 100

def test_receiver_count_decreases(alice, charlie, stream):
    pre_remove = stream.receiver_count()
    stream.remove_receiver(charlie, sender = alice)
    post_remove = stream.receiver_count()

    assert post_remove == pre_remove - 1


def test_updatest_last_update_time(alice, charlie, stream):
    pre_remove = stream.last_update_time()
    tx = stream.remove_receiver(charlie, sender = alice)
    post_remove = stream.last_update_time()

    assert pre_remove < post_remove
    # handle network jitter
    assert abs(post_remove - tx.timestamp) <= 1


def test_updatest_reward_per_receiver_total(alice, charlie, stream):
    pre_remove = stream.reward_per_receiver_total()
    stream.remove_receiver(charlie, sender = alice)
    post_remove = stream.reward_per_receiver_total()

    assert pre_remove < post_remove
    assert 0.9999 < post_remove / 10 ** 18 <= 1


def test_reverts_for_non_owner(bob, charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.remove_receiver(charlie, sender = bob)


def test_reverts_for_inactive_receiver(alice, bob, stream):
    with ape.reverts("dev: receiver is inactive"):
        stream.remove_receiver(bob, sender = alice)
