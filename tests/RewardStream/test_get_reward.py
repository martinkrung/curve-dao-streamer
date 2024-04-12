import ape


def test_only_active_receiver_can_call(charlie, stream):
    with ape.reverts("dev: caller is not receiver"):
        stream.get_reward( sender=charlie )
