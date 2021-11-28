from time import *
import random
all=[]
def make_password_safe():
    password=input('Please enter your password(in small case only): ')
    for i in password:
        if i=='s':
            print(f'You can remove {i} for $ or ( or )')
            choices=['$','(',')']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='n':
            print(f"You can remove {i} for |\|")
            all.append('|\|')
            sleep(1)
        elif i=='m':
            print(f"You can remove {i} for |\/|")
            all.append('|\/|')
            sleep(1)
        elif i=='a':
            print(f"You can remove {i} for ^ or @")
            choices=['^','@']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='h':
            print(f"You can remove {i} for # or |-|")
            choices=['|-|', '#']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='i':
            print(f"You can remove {i} for | or !")
            choices=['|', '!']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='l':
            print(f"You can remove {i} for |_")
            all.append('|_')
            sleep(1)
        elif i=='o':
            print(f"You can remove {i} for 0")
            all.append('0')
            sleep(1)
        elif i=='p':
            print(f"You can remove {i} for |>")
            all.append('|>')
            sleep(1)
        elif i=='q':
            print(f"You can remove {i} for <|")
            all.append('<|')
            sleep(1)
        elif i=='e':
            print(f"You can remove {i} for *")
            all.append('*')
            sleep(1)
        elif i=='d':
            print(f"You can remove {i} for @|")
            all.append('@|')
            sleep(1)
        elif i=='b':
            print(f"You can remove {i} for |@")
            all.append('|@')
            sleep(1)
        elif i=='r':
            print(f"You can remove {i} for |^")
            all.append('|^')
            sleep(1)
        elif i=='c':
            print(f"You can remove {i} for ( or )")
            choices=['(', ')']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
def see_chosen_password():
    print(all)
all_letters='snamilopqehdbrc'