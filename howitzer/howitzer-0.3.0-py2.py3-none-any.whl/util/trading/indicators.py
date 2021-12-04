import math
from decimal import Decimal


class Aroon():
    def __init__(self, candles):
        length = len(candles) - 1
        self.up = (100 * (length - indexOfHighest(candles=candles))) / length
        self.down = (100 * (length - indexOfLowest(candles=candles))) / length
        self.oscillator = self.up - self.down


def highest(candles, lhoc="high"):
    points = map(lambda c: _parseLHOC(c, lhoc), candles)
    return max(points)


def indexOfHighest(candles, lhoc="high"):
    points = list(map(lambda c: _parseLHOC(c, lhoc), candles))
    indexOfMax = -1
    maxValue = max(points)
    for p in points:
        indexOfMax = indexOfMax + 1
        if p == maxValue:
            break

    return indexOfMax


def indexOfLowest(candles, lhoc="low"):
    points = list(map(lambda c: _parseLHOC(c, lhoc), candles))
    indexOfMin = -1
    minValue = min(points)
    for p in points:
        indexOfMin = indexOfMin + 1
        if p == minValue:
            break

    return indexOfMin


def ema(candles, length, lookback=math.inf, lhoc="close"):
    if len(candles) > length and lookback > 0:
        N = length
        k = 2 / (N + 1)
        price = _parseLHOC(candles[0], lhoc)
        prime = ema(candles[1:], length, lookback-1, lhoc)
        return k * (price - prime) + prime
    else:
        return sma(candles[0:length], lhoc)


def sma(candles, lhoc="close"):
    sum = 0
    for candle in candles:
        sum = sum + _parseLHOC(candle, lhoc)
    return sum / len(candles)


###############################################
def _parseLHOC(candle, lhoc="close"):
    if lhoc == "low":
        return candle.low
    elif lhoc == "high":
        return candle.high
    elif lhoc == "open":
        return candle.open
    elif lhoc == "volume":
        return candle.volume
    else:
        return candle.close
