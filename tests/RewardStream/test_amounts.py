from ape import chain


def test_single_receiver(stream, alice, bob, charlie, reward_token):
    stream.add_receiver(charlie, sender=alice)
    stream.notify_reward_amount(10 ** 18, sender=bob)
    chain.pending_timestamp += 86400 * 10

    stream.get_reward(sender=charlie)

    assert 0.9999 <= reward_token.balanceOf(charlie) / 10 ** 18 <= 1


def test_single_receiver_partial_duration(stream, alice, bob, charlie, reward_token):
    stream.add_receiver(charlie, sender=alice)
    tx = stream.notify_reward_amount(10 ** 18, sender=bob)
    start = tx.timestamp - 1

    for i in range(1, 10):
        chain.mine(timestamp=start + 86400 * i)
        stream.get_reward(sender=charlie)
        assert 0.9999 <= reward_token.balanceOf(charlie) / (i * 10 ** 17) <= 1


def test_multiple_receivers(stream, alice, bob, accounts, reward_token):
    for i in range(2, 6):
        stream.add_receiver(accounts[i], sender=alice)
    tx = stream.notify_reward_amount(10 ** 18, sender=bob)
    # offset by a few seconds to avoid rounding errors
    start = tx.timestamp - 3

    for i in range(1, 10):
        chain.mine(timestamp=start + 86400 * i)
        for x in range(2, 6):
            stream.get_reward(sender=accounts[x])

        balances = [reward_token.balanceOf(i) for i in accounts[2:6]]
        assert 0.9999 < min(balances) / max(balances) <= 1
        assert 0.9999 <= sum(balances) / (i * 10 ** 17) <= 1

def test_add_receiver_during_period(stream, alice, bob, charlie, reward_token):
    stream.add_receiver(charlie, sender=alice)
    stream.notify_reward_amount(10 ** 18, sender=bob)
    chain.pending_timestamp += 86400 * 5
    stream.add_receiver(alice, sender=alice)
    chain.pending_timestamp += 86400 * 5

    stream.get_reward(sender=alice)
    stream.get_reward(sender=charlie)
    alice_balance = reward_token.balanceOf(alice)
    charlie_balance = reward_token.balanceOf(charlie)

    assert 0.9999 <= alice_balance * 3 / charlie_balance <= 1
    assert 0.9999 <= (alice_balance + charlie_balance) / 10 ** 18 <= 1
    

def test_remove_receiver_during_period(stream, alice, bob, charlie, reward_token):
    stream.add_receiver(alice, sender=alice)
    stream.add_receiver(charlie, sender=alice)
    stream.notify_reward_amount(10 ** 18, sender=bob)
    chain.mine(deltatime=86400 * 5)
    stream.remove_receiver(alice, sender=alice)
    chain.mine(deltatime=86400 * 5)

    stream.get_reward(sender=charlie)
    alice_balance = reward_token.balanceOf(alice)
    charlie_balance = reward_token.balanceOf(charlie)

    assert 0.9999 <= alice_balance * 3 / charlie_balance <= 1.0001
    assert 0.9999 <= (alice_balance + charlie_balance) / 10 ** 18 <= 1.0001
