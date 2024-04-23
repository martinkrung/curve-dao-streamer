import ape
import pytest
import sys

def test_change_receiver_ratio(alice, charlie, bob,  stream):
    
    stream.add_receiver(charlie, sender=alice)
    stream.add_receiver(bob, sender=alice)

    data = stream.get_receiver_data(charlie)
    print(data)
    data = stream.get_receiver_data(bob)
    print(data)
    
    stream.change_receiver_ratio(charlie, 30, bob, 70, sender=alice)

    data = stream.get_receiver_data(charlie)
    print(data)
    data = stream.get_receiver_data(bob)
    print(data)
    

def test_revert_change_receiver_ratio(alice, charlie, bob,  stream):
    
    stream.add_receiver(charlie, sender=alice)
    stream.add_receiver(bob, sender=alice)
    
    data = stream.get_receiver_data(charlie)
    print(data)
    data = stream.get_receiver_data(bob)
    print(data)

    with ape.reverts("dev: ratio total is not 100"):
        stream.change_receiver_ratio(charlie, 30, bob, 71, sender=alice)


def test_revert_change_receiver_ratio_invalid_range(alice, charlie, bob, stream):
    
    stream.add_receiver(charlie, sender=alice)
    stream.add_receiver(bob, sender=alice)

    data = stream.get_receiver_data(charlie)
    print(data)
    data = stream.get_receiver_data(bob)
    print(data)

    with ape.reverts("dev: ratio must be < 100"):
        stream.change_receiver_ratio(charlie, 130, bob, 13, sender=alice)

    with ape.reverts("dev: ratio must be > 0"):
        stream.change_receiver_ratio(charlie, 0, bob, 13, sender=alice)

    with ape.reverts("dev: ratio must be < 100"):
        stream.change_receiver_ratio(charlie, 13, bob, 130, sender=alice)

    with ape.reverts("dev: ratio must be > 0"):
        stream.change_receiver_ratio(charlie, 20, bob, 0, sender=alice)
