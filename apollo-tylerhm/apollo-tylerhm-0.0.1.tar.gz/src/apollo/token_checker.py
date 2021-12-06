from verdict import Response, Correct, WrongAnswer, PresentationError

# File references to user_out and judge_out
def check(user_out, judge_out):
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

    # Check input token by token
    for user, judge, tok in zip(user_tokens, judge_tokens, range(min_tokens)):
        if user != judge:
            return Response(WrongAnswer, (
                f'Token {tok} does not match.\n\n'
                f'Expected: {judge}\n\n'
                f'Recieved: {user}'
            ))

    # Give presentation error for too much output
    if (user_token_count > judge_token_count):
        return Response(PresentationError, 'Too much output')

    return Response(Correct)
