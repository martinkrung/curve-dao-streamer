import ape
from ape import chain
import pytest


def test_add_multiple_receivers(alice, charlie, bob, dora,  stream):

    pre_receiver_count = stream.receiver_count()
    
    stream.add_multiple_receivers(charlie, 25, sender=alice)
    stream.add_multiple_receivers(bob, 25, sender=alice)
    stream.add_multiple_receivers(dora, 50, sender=alice)

    assert stream.receiver_count() == pre_receiver_count + 3

    stream.ratio_test(sender=alice)


def test_revert_add_multiple_receivers(alice, charlie, bob,  stream):
    
    stream.add_multiple_receivers(charlie, 25, sender=alice)
    stream.add_multiple_receivers(bob, 25, sender=alice)

    with ape.reverts("dev: ratio total is not 100"):
        stream.ratio_test(sender=alice)

def test_revert_add_multiple_receivers_add_same(alice, charlie, bob,  stream):
    
    stream.add_multiple_receivers(charlie, 25, sender=alice) 

    with ape.reverts("dev: receiver is active"):
        stream.add_multiple_receivers(charlie, 25, sender=alice)


def test_change_receiver_ratio(alice, charlie, bob,  stream):
    
    stream.add_multiple_receivers(charlie, 50, sender=alice)
    stream.add_multiple_receivers(bob, 50, sender=alice)
    
    stream.ratio_test(sender=alice)

    stream.change_receiver_ratio(charlie, 30, bob, 70, sender=alice)

    stream.ratio_test(sender=alice)
   

def test_change_receiver_ratio_revert(alice, charlie, bob,  stream):
    
    stream.add_multiple_receivers(charlie, 50, sender=alice)
    stream.add_multiple_receivers(bob, 50, sender=alice)
    
    stream.ratio_test(sender=alice)

    with ape.reverts("dev: ratio total is not 100"):
        stream.change_receiver_ratio(charlie, 30, bob, 71, sender=alice)
