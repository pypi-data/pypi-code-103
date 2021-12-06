def volcanoSort(s):
    length = len(s)
    # If length < 3, then you cant have a valid volcano!
    if length < 3:
        return "Not a valid volcano!"

    # Order array into "Volcano Order Patent Pending"
    volcanoOrder = [float('inf')] * length
    maximum = max(s)
    lindex = rindex = mindex = length//2
    volcanoOrder[mindex] = maximum
    s.pop(s.index(maximum))
    seen = [maximum]
    direction = 1
    
    for _ in range(length-1):
        newMax = float('-inf')
        for i, num in enumerate(s):
            if num > newMax:
                newMax = num
                index = i
        if direction == 1:
            volcanoOrder[lindex-1] = newMax
            lindex -= 1
            direction = 0
        else:
            volcanoOrder[rindex+1] = newMax
            rindex += 1
            direction = 1
        s.pop(index)
        seen.append(newMax)
    
    # Erupt the Volcano Order to create the sorted array
    volcanoSorted = []
    if length % 2 == 0:
        for _ in range(length):
            volcanoSorted.append(volcanoOrder.pop(len(volcanoOrder)//2))
    else:
        for _ in range(length//2):
            volcanoSorted.append(volcanoOrder.pop(len(volcanoOrder)//2))
            volcanoSorted.append(volcanoOrder.pop(len(volcanoOrder)//2 - 1))
        volcanoSorted.append(volcanoOrder.pop())

    return volcanoSorted[::-1]