# About

This reward streamer allowes to set a ratio between 1-99% for each receiver.

## ratio is reset on adding or removing receivers

On adding or removing a receiver, all of the active receivers are reset to a more or less equal ratio.

Sum of all ratios always hase to be **100**, if the amount of receivers is not divisable without rest, the rest will be added to the last receiver:

For 3 receivers, the last one has 1% more: 34%, while the others 33%
For 6 receivers, the last one has 4% more: 20%, while the others 16%
For 7 receivers, the last one has 2% more: 16%, while the others 14%
For 8 receivers, the last one has 4% more: 16%, while the others 12%

## set change ratio by ratio manager

After inital ratio is set, ratio can be adjusted anytime by the ratio manager account.

both receiver have to be active receivers and 0 < ratio < 100:

``change_receiver_ratio(_receiver0: address, _ratio0: uint256, _receiver1: address, _ratio1: uint256):
``

## Origin

Based on https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/streamers/RewardStream.vy and with test migrated to ape