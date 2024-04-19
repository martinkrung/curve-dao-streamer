import ape
import pytest

def test_receiver_count_increases(alice, charlie, stream):
    pre_receiver_count = stream.receiver_count()
    stream.add_receiver(charlie, sender=alice)

    assert stream.receiver_count() == pre_receiver_count + 1


def test_receiver_activation(alice, charlie, stream):
    pre_activation = stream.reward_receivers(charlie)
    stream.add_receiver(charlie,  sender=alice)

    assert pre_activation is False
    assert stream.reward_receivers(charlie) is True


def test_receiver_ratio_activation(alice, bob, charlie, dora, stream):
    pre_activation = stream.reward_ratio(bob)
    stream.add_receiver(bob,  sender=alice)

    assert pre_activation == 0
    assert stream.reward_ratio(bob) == 100

    pre_activation = stream.reward_ratio(charlie)
    stream.add_receiver(charlie,  sender=alice)

    assert pre_activation == 0
    assert stream.reward_ratio(charlie) == 50
    assert stream.reward_ratio(bob) == 50

    pre_activation = stream.reward_ratio(dora)
    stream.add_receiver(dora,  sender=alice)

    assert pre_activation == 0
    assert stream.reward_ratio(bob) == 33
    assert stream.reward_ratio(charlie) == 33
    assert stream.reward_ratio(dora) == 34

def test_reverts_for_non_owner(bob, charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.add_receiver(charlie, sender=bob)


def test_reverts_for_active_receiver(alice, charlie, stream):
    stream.add_receiver(charlie, sender=alice)
    with ape.reverts("dev: receiver is active"):
        stream.add_receiver(charlie, sender=alice)