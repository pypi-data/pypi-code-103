def TestMoneyLine(inputs, outputs, model):
    stats = {"correct": 0, "total": len(inputs), "accuracy": 0, "taken": 0}
    for i in range(len(inputs)):
        take_bet, guess = model(inputs[i])
        if take_bet:
            stats["taken"] += 1
            if guess is outputs[i]:
                stats["correct"] += 1

    stats["accuracy"] = stats["correct"]/stats["taken"]
    return stats

def SimulateMoneyLine(account_size=1000, bet_size=0.1, inputs=[], outputs=[], model=None, static_roi=0.8):
    balance = account_size
    bet_history = []
    bet_history.append(1000)
    for i in range(len(inputs)):
        take_bet, guess = model(inputs[i])
        if take_bet:
            if guess is outputs[i]:
                balance += (balance * bet_size) * static_roi
            else:
                balance -= (balance * bet_size)
            bet_history.append(balance)
    return bet_history