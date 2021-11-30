#!/usr/bin/python3 

import os
from argparse import ArgumentParser
import requests


parser = ArgumentParser(description='A very simple OpenContest command line client written in Python')
parser.add_argument('command', choices=['save', 'about', 'contests', 'info', 'problem', 'solves', 'history', 'register', 'submit', 'status', 'submissions', 'code'], type=str)
parser.add_argument('-C', '--config', help='Config file path', default='~/.config/occ/config', type=str)
parser.add_argument('-U', '--username', help='Your username', type=str)
parser.add_argument('-H', '--homeserver', help='URL of your registration server', type=str)
parser.add_argument('-P', '--password', help='Your username', type=str)
parser.add_argument('-N', '--name', help='Your name for registering an account', type=str)
parser.add_argument('-E', '--email', help='Your email for registering an account', type=str)
parser.add_argument('-s', '--server', help='URL of the server you are connecting to', type=str)
parser.add_argument('-c', '--contest', help='Contest to query', type=str)
parser.add_argument('-p', '--problem', help='Problem to query', type=str)
parser.add_argument('-f', '--file', help='File for code submission', type=str)
parser.add_argument('-n', '--number', help='Submission number to query', type=str)

args = parser.parse_args()

# Process config file
args.config = os.path.expanduser(args.config)
if os.path.exists(args.config):
    # Read in values from file
    with open(args.config, 'r') as f:
        lines = f.readlines()
        if args.username == None:
            args.username = lines[0][:-1]
        if args.homeserver == None:
            args.homeserver = lines[1][:-1]
        if args.password == None:
            args.password = lines[2][:-1]

# Authenticate user with their homeserver
def authenticate():
    return requests.post(args.server, json={
        'type': 'authenticate',
        'username': args.username,
        'homeserver': args.homeserver,
        'password': args.password
    }).text

if not args.server == None:
    args.server = 'https://' + args.server # Use HTTPS protocol

# Process commands
if args.command == 'save':
    os.makedirs(os.path.dirname(args.config), exist_ok=True)
    with open(args.config, 'w') as f:
        f.write(args.username + '\n')
        f.write(args.homeserver + '\n')
        f.write(args.password + '\n')
    exit()
elif args.command == 'about':
    r = requests.post(args.server, json={
        'type': 'about'
    })
elif args.command == 'contests':
    r = requests.post(args.server, json={
        'type': 'contests'
    })
elif args.command == 'info':
    r = requests.post(args.server, json={
        'type': 'info',
        'contest': args.contest
    })
elif args.command == 'problem':
    r = requests.post(args.server, json={
        'type': 'problem',
        'contest': args.contest,
        'problem': args.problem
    })
    print(r.reason)
    os.makedirs(args.contest, exist_ok=True)
    with open(os.path.join(args.contest, args.problem + '.pdf'), 'wb') as f:
        f.write(r.content) # Save problems to file
    exit()
elif args.command == 'solves':
    r = requests.post(args.server, json={
        'type': 'solves',
        'contest': args.contest
    })
elif args.command == 'history':
    r = requests.post(args.server, json={
        'type': 'history',
        'contest': args.contest
    })
elif args.command == 'register':
    r = requests.post(args.server, json={
        'type': 'register',
        'name': args.name,
        'email': args.email,
        'username': args.username,
        'password': args.password
    })
elif args.command == 'submit':
    r = requests.post(args.server, json={
        'type': 'submit',
        'username': args.username,
        'homeserver': args.homeserver,
        'token': authenticate(),
        'contest': args.contest,
        'problem': args.problem,
        'language': os.path.splitext(args.file)[1][1:],
        'code': open(args.file, 'r').read(),
    })
elif args.command == 'status':
    r = requests.post(args.server, json={
        'type': 'status',
        'username': args.username,
        'homeserver': args.homeserver,
        'token': authenticate(),
        'contest': args.contest
    })
elif args.command == 'submissions':
    r = requests.post(args.server, json={
        'type': 'submissions',
        'username': args.username,
        'homeserver': args.homeserver,
        'token': authenticate(),
        'contest': args.contest
    })
elif args.command == 'code':
    r = requests.post(args.server, json={
        'type': 'code',
        'username': args.username,
        'homeserver': args.homeserver,
        'token': authenticate(),
        'contest': args.contest,
        'problem': args.problem,
        'number': args.number
    })
print(r.reason)
print(r.text)
