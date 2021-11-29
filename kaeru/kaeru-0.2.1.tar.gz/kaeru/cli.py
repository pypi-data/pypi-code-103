import argparse
import asyncio
from datetime import date
from kaeru.api import submit_answers, get_answers, add_user, delete_user, get_users, delete_answer

parser = argparse.ArgumentParser(description='Cheats for fireflies.')
subparsers = parser.add_subparsers(dest="subcommand")

def subcommand(args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator

def argument(*name_or_flags, **kwargs):
    return ([*name_or_flags], kwargs)

@subcommand([argument("--date", default=date.today(), help="specify an assignment to answer"), argument("--reset", action="store_true")])
def submit(args):
    if args.reset:
       asyncio.run(delete_answer(args.date)) 
    answer_data = asyncio.run(get_answers(args.date))
    answer = input("Continue?").lower()
    if answer == "y":
        users = asyncio.run(get_users())
        for user in users:
            asyncio.run(submit_answers(**user, answer_data=answer_data))

@subcommand([argument("email", help="Email"), argument("password", help="Password")])
def adduser(args):
    asyncio.run(add_user(args.email, args.password))

@subcommand([argument("email", help="Email")])
def deluser(args):
    asyncio.run(delete_user(args.email))


def run():
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)
