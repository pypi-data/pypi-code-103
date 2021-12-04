def kellyCriterion(_return_including_wager, _porbality_of_win):
    if _return_including_wager <= 1.0:
        return 0
    top = _return_including_wager *_porbality_of_win -1
    bottom = _return_including_wager - 1
    return top / bottom