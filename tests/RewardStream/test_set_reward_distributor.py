import ape


def test_successful_change(alice, charlie, stream):
    stream.set_reward_distributor(charlie, sender = alice)

    assert stream.distributor() == charlie


def test_only_owner(bob, charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.set_reward_distributor(charlie, sender = bob)
