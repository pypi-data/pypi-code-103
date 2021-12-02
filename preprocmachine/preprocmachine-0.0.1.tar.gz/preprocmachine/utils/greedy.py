import random


def epsilon(choices, q_vals, e):
    """
    choices is an array of possible actions and q_vals contains their corresponding q values
    this function chooses one and returns it
    """

    #     e = 0.8 #80% of the time function should choose highest quality
    num = random.randrange(0, 100) / 100
    if e >= num:  # choose based on highest quality
        #         print("Epsilon chose quality")
        max_q = max(q_vals)
        # accounts for potentially multiple choices with highest Q
        max_indices = [i for i, val, in enumerate(q_vals) if val == max_q]
        #         if multiple, randomly pick
        if len(max_indices) > 1:
            choice = random.randrange(0, len(max_indices))
            index = max_indices[choice]
        else:  # if just one, then return
            index = max_indices[0]
        return choices[index]
    else:  # choose randomly
        #         print("Epsilon chose random")
        index = random.randrange(0, len(choices))
        return choices[index]
