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


def test_reverts_for_non_owner(bob, charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.add_receiver(charlie, sender=bob)


def test_reverts_for_active_receiver(alice, charlie, stream):
    stream.add_receiver(charlie, sender=alice)
    with ape.reverts("dev: receiver is active"):
        stream.add_receiver(charlie, sender=alice)