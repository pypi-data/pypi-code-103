from verdict import Response, Correct, WrongAnswer, PresentationError

def compare_eps(user, judge, eps):
    try:
        user = float(user)
        judge = float(judge)

        absolute = abs(judge - user) <= eps + 1e-10

        if (judge == 0):
            return absolute

        relative = abs((judge - user) / judge) <= eps + 1e-10

        return absolute or relative

    except ValueError:
        return user == judge

# File references to user_out and judge_out
def check(user_out, judge_out, eps):
    user_lines = [s.strip().split() for s in user_out.readlines()]
    judge_lines = [s.strip().split() for s in judge_out.readlines()]

    user_tokens = [tok for line in user_lines for tok in line]
    judge_tokens = [tok for line in judge_lines for tok in line]

    user_token_count = len(user_tokens)
    judge_token_count = len(judge_tokens)
    min_tokens = min(user_token_count, judge_token_count)

    # Give wrong answer for missing output
    if (user_token_count < judge_token_count):
        return Response(WrongAnswer, 'Not enough output')

    # Check input line by line
    for user, judge, tok in zip(user_tokens, judge_tokens, range(min_tokens)):
        if not compare_eps(user, judge, eps):
            return Response(WrongAnswer, (
                f'Token {tok} does not match.\n\n'
                f'Expected: {judge}\n\n'
                f'Recieved: {user}'
            ))

    # Give presentation error for too much output
    if (user_token_count > judge_token_count):
        return Response(PresentationError, 'Too much output')

    return Response(Correct)
