from random import randint


def get_unit():
	return randint(-10000, 10000) / 10000


def get_normal():
	return randint(0, 10000) / 10000


def clamp_value(value, min, max):
	if value > max:
		return max

	if value < min:
		return min

	return value


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
