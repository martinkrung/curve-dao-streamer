import ape
from ape import chain

import math

def test_only_distributor_allowed(alice, stream):
    with ape.reverts("dev: only distributor"):
        stream.notify_reward_amount(10 ** 18, sender = alice)


def test_retrieves_reward_token(bob, stream, reward_token):
    stream.notify_reward_amount(10 ** 18, sender = bob)
    post_notify = reward_token.balanceOf(stream)

    assert post_notify == 10 ** 18


def test_reward_rate_updates(bob, stream):
    stream.notify_reward_amount(10 ** 18, sender = bob)
    post_notify = stream.reward_rate()

    assert post_notify > 0
    assert post_notify == 10 ** 18 // (86400 * 10)


def test_reward_rate_updates_mid_duration(bob, stream):
    stream.notify_reward_amount(10 ** 18, sender = bob)
    chain.pending_timestamp += 86400 * 5  # half of the duration

    # top up the balance to be 10 ** 18 again
    stream.notify_reward_amount(10 ** 18 // 2, sender = bob)
    post_notify = stream.reward_rate()

    # should relatively close .00001 seems about good of a heuristic
    assert math.isclose(post_notify, 10 ** 18 // (86400 * 10), rel_tol=0.00001)


def test_period_finish_updates(bob, stream):
    tx = stream.notify_reward_amount(10 ** 18, sender = bob)

    assert stream.period_finish() == tx.timestamp + 86400 * 10


def test_update_last_update_time(bob, stream):
    tx = stream.notify_reward_amount(10 ** 18, sender = bob)

    assert stream.last_update_time() == tx.timestamp
