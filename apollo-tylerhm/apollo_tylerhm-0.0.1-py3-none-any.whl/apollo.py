import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.absolute()))
import arguments, diff_checker, token_checker, epsilon_checker

args = arguments.parse()

with open(args.user_output) as user_out, open(args.judge_output) as judge_out:
    if args.tok:
        res = token_checker.check(user_out, judge_out)
    elif args.eps:
        res = epsilon_checker.check(user_out, judge_out, args.eps)
    else:
        res = diff_checker.check(user_out, judge_out)

    if (args.verbose):
        print(res.to_string())

    sys.exit(res.verdict.return_code)

