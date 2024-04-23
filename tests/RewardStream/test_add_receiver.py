import ape
import pytest
import sys


def test_receiver_count_increases(alice, charlie, stream):
    pre_receiver_count = stream.receiver_count()
    stream.add_receiver(charlie, sender=alice)
    
    data = stream.get_receiver_data(charlie)
    print(data)

    assert stream.receiver_count() == pre_receiver_count + 1


def test_receiver_activation(alice, charlie, stream):
    pre_activation = stream.reward_receivers(charlie)['active']
    stream.add_receiver(charlie,  sender=alice)

    data = stream.get_receiver_data(charlie)
    print(data)

    assert pre_activation is False
    assert stream.reward_receivers(charlie)['active'] is True


def test_receiver_ratio_activation(alice, bob, charlie, dora, stream):
    pre_activation = stream.reward_receivers(bob)['active']
    stream.add_receiver(bob,  sender=alice)

    stream.reward_receivers(bob)['paid'] == 0

    assert pre_activation == 0
    assert stream.reward_receivers(bob)['ratio'] == 100

    pre_activation = stream.reward_receivers(charlie)['active']
    stream.add_receiver(charlie,  sender=alice)

    assert pre_activation == 0
    assert stream.reward_receivers(charlie)['ratio'] == 50
    assert stream.reward_receivers(bob)['ratio'] == 50

    pre_activation = stream.reward_receivers(dora)['active']
    stream.add_receiver(dora,  sender=alice)

    assert pre_activation == 0
    assert stream.reward_receivers(bob)['ratio'] == 33
    assert stream.reward_receivers(charlie)['ratio'] == 33
    assert stream.reward_receivers(dora)['ratio'] == 34

    data = stream.get_receiver_data(bob)
    print(data)
    data = stream.get_receiver_data(charlie)
    print(data)
    data = stream.get_receiver_data(dora)
    print(data)


def test_reverts_for_non_owner(bob, charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.add_receiver(charlie, sender=bob)


def test_reverts_for_active_receiver(alice, charlie, stream):
    stream.add_receiver(charlie, sender=alice)
    with ape.reverts("dev: receiver is active"):
        stream.add_receiver(charlie, sender=alice)