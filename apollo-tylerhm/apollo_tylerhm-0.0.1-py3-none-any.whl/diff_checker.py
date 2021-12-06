from verdict import Response, Correct, WrongAnswer, PresentationError

# File references to user_out and judge_out
def check(user_out, judge_out):
    user_lines = [s.strip() for s in user_out.readlines()]
    judge_lines = [s.strip() for s in judge_out.readlines()]

    while (user_lines[-1] == ''):
        user_lines.pop()
    while (judge_lines[-1] == ''):
        judge_lines.pop()

    user_line_count = len(user_lines)
    judge_line_count = len(judge_lines)
    min_lines = min(user_line_count, judge_line_count)

    # Give wrong answer for missing output
    if (user_line_count < judge_line_count):
        return Response(WrongAnswer, 'Not enough output')

    # Check input line by line
    for user, judge, line in zip(user_lines, judge_lines, range(min_lines)):
        if user != judge:
            return Response(WrongAnswer, (
                f'Line {line} does not match.\n\n'
                f'Expected: {judge}\n\n'
                f'Recieved: {user}'
            ))

    # Give presentation error for too much output
    if (user_line_count > judge_line_count):
        return Response(PresentationError, 'Too much output')

    return Response(Correct)
