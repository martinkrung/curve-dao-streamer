import ape


def test_successful_change(alice, charlie, stream):
    stream.set_ratio_manager(charlie, sender = alice)

    assert stream.ratio_manager() == charlie


def test_only_owner(bob, charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.set_ratio_manager(charlie, sender = bob)