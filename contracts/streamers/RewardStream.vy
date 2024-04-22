# @version 0.3.10
"""
@title RewardStream
@author Curve.Fi
@license MIT
@notice Evenly streams a reward token to one or more
        recipients over a predefined period
"""

from vyper.interfaces import ERC20

owner: public(address)
future_owner: public(address)
distributor: public(address)
ratio_manager: public(address)

reward_token: public(address)
period_finish: public(uint256)
reward_rate: public(uint256)
reward_duration: public(uint256)
last_update_time: public(uint256)
reward_per_receiver_total: public(uint256)

receiver_count: public(uint256)

reward_receivers: public(HashMap[address, bool])
reward_ratio: public(HashMap[address, uint256])
reward_per_receiver_total_ratio: public(HashMap[address, uint256])

reward_paid: public(HashMap[address, uint256])

receivers: public(DynArray[address, 8])

@external
def __init__(_owner: address, _distributor: address, _ratio_manager: address, _token: address, _duration: uint256):
    self.owner = _owner
    self.distributor = _distributor
    self.ratio_manager = _ratio_manager
    self.reward_token = _token
    self.reward_duration = _duration


@internal
def _update_per_receiver_total() -> uint256:
    # update the total reward amount paid per receiver
    total: uint256 = self.reward_per_receiver_total
    # future count of receivers
    count: uint256 = self.receiver_count
    if count == 0:
        return total

    last_time: uint256 = min(block.timestamp, self.period_finish)
    total += (last_time - self.last_update_time) * self.reward_rate / count
    self.reward_per_receiver_total = total
    self.last_update_time = last_time

    return total

@internal
def _update_per_receiver_total_ratio(_receiver: address) -> uint256:
    # Todo: 
    # update the total reward amount paid per receiver according to the ratio
    # Make sure ratio is change befor this function is called
    # return value now makes no sense
    """
    @dev Only callable by the ratio_manager. Reward tokens are distributed
         according to the ratio between receivers, over `reward_duration` seconds.
    """
    total: uint256 = self.reward_per_receiver_total_ratio[_receiver]
    count: uint256 = self.receiver_count
    
    if count == 0:
        return total
    
    ratio: uint256  = 0
    last_time: uint256 = min(block.timestamp, self.period_finish)

    for receiver_address in self.receivers:
        total = self.reward_per_receiver_total_ratio[receiver_address]
        ratio = self.reward_ratio[receiver_address]
        # what is happening if ratio changes, is total wrong?
        total += (last_time - self.last_update_time) * self.reward_rate * ratio / 100
        self.reward_per_receiver_total_ratio[receiver_address] = total

    self.last_update_time = last_time

    return self.reward_per_receiver_total_ratio[_receiver]


@internal
def _set_even_reward_ratio():
    for i in self.receivers:
        self.reward_ratio[i] = 100 / self.receiver_count

    if (100 % self.receiver_count) > 0:
        self.reward_ratio[self.receivers[self.receiver_count-1]] = self.reward_ratio[self.receivers[self.receiver_count-1]] + (100 % self.receiver_count)

@view
@external
def ratio_test():
    ratio_total: uint256 = 0
    for i in self.receivers:
        ratio_total += self.reward_ratio[i]

    assert ratio_total == 100,  "dev: ratio total is not 100"

@internal
def _ratio_test():
    ratio_total: uint256 = 0
    for i in self.receivers:
        ratio_total += self.reward_ratio[i]

    assert ratio_total == 100,  "dev: ratio total is not 100"

@external
def add_receiver(_receiver: address):
    """
    @notice Add a new reward receiver
    @dev Rewards are distributed evenly between the receivers. Adding a new
         receiver does not affect the available amount of unclaimed rewards
         for other receivers.
    @param _receiver Address of the new reward receiver
    """
    assert msg.sender == self.owner,  "dev: only owner"
    assert not self.reward_receivers[_receiver],  "dev: receiver is active"

    self.receivers.append(_receiver)
    self.receiver_count += 1
    self._set_even_reward_ratio()

    total: uint256 = self._update_per_receiver_total_ratio(_receiver)

    self.reward_receivers[_receiver] = True
    self.reward_paid[_receiver] = total

@external
def add_receiver_old(_receiver: address):
    """
    @notice Add a new reward receiver
    @dev Rewards are distributed evenly between the receivers. Adding a new
         receiver does not affect the available amount of unclaimed rewards
         for other receivers.
    @param _receiver Address of the new reward receiver
    """
    assert msg.sender == self.owner,  "dev: only owner"
    assert not self.reward_receivers[_receiver],  "dev: receiver is active"
    total: uint256 = self._update_per_receiver_total()

    self.reward_receivers[_receiver] = True
    self.receiver_count += 1
    self.reward_paid[_receiver] = total
    self.receivers.append(_receiver)
    self._set_even_reward_ratio()


@external
def change_receiver_ratio(_receiver0: address, _ratio0: uint256, _receiver1: address, _ratio1: uint256):
        """
        @notice change receiver status
        @dev if existing receiver is active, deactivate it and pay out the remaining rewards
             if existing receiver is inactive, activate it
        """
        # todo, if deactivate, ratio cant be changed!
        assert msg.sender == self.ratio_manager, "dev: only ratio manager"

        assert self.reward_receivers[_receiver0], "dev: receiver is inactive"
        assert self.reward_receivers[_receiver1], "dev: receiver is inactive"
        assert _ratio0 < 100 , "dev: ratio must be < 100"
        assert _ratio0 > 0 , "dev: ratio must be > 0"
        assert _ratio1 < 100 , "dev: ratio must be < 100"
        assert _ratio1 > 0 , "dev: ratio must be > 0"

        self.reward_ratio[_receiver0] = _ratio0
        self.reward_ratio[_receiver1] = _ratio1
                    
        self._ratio_test()

@external
def add_multiple_receivers(_receiver: address, ratio: uint256):
    """
    @notice Add a new reward receiver
    @dev Rewards are distributed evenly between the receivers. Adding a new
         receiver does not affect the available amount of unclaimed rewards
         for other receivers.
    @param _receiver Address of the new reward receiver
    """
    assert msg.sender == self.owner,  "dev: only owner"
    assert not self.reward_receivers[_receiver],  "dev: receiver is active"

    self.receivers.append(_receiver)
    self.reward_ratio[_receiver] = ratio
    self.reward_receivers[_receiver] = True
    self.receiver_count += 1


@external
def remove_receiver(_receiver: address):
    """
    @notice Remove an existing reward receiver
    @dev Removing a receiver distributes any unclaimed rewards to that receiver.
    @param _receiver Address of the reward receiver being removed
    """
    assert msg.sender == self.owner, "dev: only owner"
    assert self.reward_receivers[_receiver], "dev: receiver is inactive"
    # with current self.receiver_count 
    total: uint256 = self._update_per_receiver_total_ratio(_receiver)

    self.reward_receivers[_receiver] = False
    self.receiver_count -= 1
    amount: uint256 = total - self.reward_paid[_receiver]
    if amount > 0:
        assert ERC20(self.reward_token).transfer(_receiver, amount), "dev: invalid response"
    self.reward_paid[_receiver] = 0
    
    
    index: uint256 = 0
    # loop through the array to find the index of the receiver to delete
    for receiver_address in self.receivers:
        if _receiver == receiver_address:
            break
        index += 1

    assert self.receivers[index] == _receiver, "dev: invalid removal"

    # Move the last element to the position of the element to be removed
    # then remove the last element
    self.receivers[index] = self.receivers[len(self.receivers) - 1]
    self.receivers.pop()
    
    self._set_even_reward_ratio()


@external
def remove_receiver_old(_receiver: address):
    """
    @notice Remove an existing reward receiver
    @dev Removing a receiver distributes any unclaimed rewards to that receiver.
    @param _receiver Address of the reward receiver being removed
    """
    assert msg.sender == self.owner, "dev: only owner"
    assert self.reward_receivers[_receiver], "dev: receiver is inactive"
    total: uint256 = self._update_per_receiver_total()

    self.reward_receivers[_receiver] = False
    self.receiver_count -= 1
    amount: uint256 = total - self.reward_paid[_receiver]
    if amount > 0:
        assert ERC20(self.reward_token).transfer(_receiver, amount), "dev: invalid response"
    self.reward_paid[_receiver] = 0
    
    
    index: uint256 = 0
    # loop through the array to find the index of the receiver to delete
    for receiver_address in self.receivers:
        if _receiver == receiver_address:
            break
        index += 1

    assert self.receivers[index] == _receiver, "dev: invalid removal"

    # Move the last element to the position of the element to be removed
    # then remove the last element
    self.receivers[index] = self.receivers[len(self.receivers) - 1]
    self.receivers.pop()
    
    self._set_even_reward_ratio()


@external
def get_reward(_receiver: address = msg.sender):
    """
    @notice Claim pending rewards
    """
    assert self.reward_receivers[_receiver],  "dev: caller is not receiver"
    total: uint256 = self._update_per_receiver_total_ratio(_receiver)

    #  total: uint256 = self._update_per_receiver_total()
    amount: uint256 = total - self.reward_paid[_receiver]
    if amount > 0:
        assert ERC20(self.reward_token).transfer(_receiver, amount), "dev: invalid response"
        self.reward_paid[_receiver] = total


@external
def notify_reward_amount(_amount: uint256):
    """
    @notice Transfer new reward tokens into the contract
    @dev Only callable by the distributor. Reward tokens are distributed
         evenly between receivers, over `reward_duration` seconds.
    @param _amount Amount of reward tokens to add
    """
    assert msg.sender == self.distributor, "dev: only distributor"
    self._update_per_receiver_total()
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount), "dev: invalid response"
    duration: uint256 = self.reward_duration
    if block.timestamp >= self.period_finish:
        self.reward_rate = _amount / duration
    else:
        remaining: uint256 = self.period_finish - block.timestamp
        leftover: uint256 = remaining * self.reward_rate
        self.reward_rate = (_amount + leftover) / duration

    self.last_update_time = block.timestamp
    self.period_finish = block.timestamp + duration


@external
def set_reward_duration(_duration: uint256):
    """
    @notice Modify the duration that rewards are distributed over
    @dev Only callable when there is not an active reward period
    @param _duration Number of seconds to distribute rewards over
    """
    assert msg.sender == self.owner, "dev: only owner"
    assert block.timestamp > self.period_finish, "dev: reward period currently active"
    self.reward_duration = _duration


@external
def set_reward_distributor(_distributor: address):
    """
    @notice Modify the reward distributor
    @param _distributor Reward distributor
    """
    assert msg.sender == self.owner, "dev: only owner"
    self.distributor = _distributor

@external
def set_ratio_manager(_ratio_manager: address):
    """
    @notice Modify the ratio manager
    @param _ratio_manager ratio manager
    """
    assert msg.sender == self.owner, "dev: only owner"
    self.ratio_manager = _ratio_manager


@external
def commit_transfer_ownership(_owner: address):
    """
    @notice Initiate ownership tansfer of the contract
    @param _owner Address to have ownership transferred to
    """
    assert msg.sender == self.owner, "dev: only owner"

    self.future_owner = _owner


@external
def accept_transfer_ownership():
    """
    @notice Accept a pending ownership transfer
    """
    owner: address = self.future_owner
    assert msg.sender == owner, "dev: only new owner"

    self.owner = owner
