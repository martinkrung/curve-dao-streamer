import ape


def test_updates_reward_duration(alice, stream):
    pre_update = stream.reward_duration()
    stream.set_reward_duration(86400 * 365, sender = alice)

    assert pre_update == 86400 * 10
    assert stream.reward_duration() == 86400 * 365


def test_only_owner(charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.set_reward_duration(10, sender = charlie)


def test_mid_reward_distribution_period(alice, bob, stream):
    stream.notify_reward_amount(10 ** 18, sender = bob)

    with ape.reverts("dev: reward period currently active"):
        stream.set_reward_duration(10, sender = alice)
