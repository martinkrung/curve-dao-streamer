import ape
import pytest

from itertools import product


@pytest.mark.parametrize("commit,accept", product([0, 1], repeat=2))
def test_change_ownership(alice, charlie, commit, accept, stream):
    if commit:
        stream.commit_transfer_ownership(charlie, sender = alice )

        if accept:
            stream.accept_transfer_ownership(sender = charlie )

    assert stream.owner() == charlie if commit and accept else alice


def test_commit_only_owner(charlie, stream):
    with ape.reverts("dev: only owner"):
        stream.commit_transfer_ownership(charlie, sender = charlie )


def test_accept_only_owner(alice, bob, stream):
    stream.commit_transfer_ownership(bob, sender = alice )

    with ape.reverts("dev: only new owner"):
        stream.accept_transfer_ownership(sender = alice )
