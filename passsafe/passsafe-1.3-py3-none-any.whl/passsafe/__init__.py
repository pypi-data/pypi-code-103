from time import *
import random
from tkinter import *
root=Tk()
all=[]
a=Label(root,text='Please enter your password(in small case only): ')
a.grid(row=0,column=0)
password=Entry(root,show='*')
password.grid(row=0,column=1)
def make_password_safe():
    for i in password.get():
        if i=='s':
            Label(root,text=f'You can remove {i} for $ or ( or )').grid()
            choices=['$','(',')']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='n':
            Label(root,text=f"You can remove {i} for |\|").grid()
            all.append('|\|')
            sleep(1)
        elif i=='m':
            Label(root,text=f"You can remove {i} for |\/|").grid()
            all.append('|\/|')
            sleep(1)
        elif i=='a':
            Label(root,text=f"You can remove {i} for ^ or @").grid()
            choices=['^','@']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='h':
            Label(root,text=f"You can remove {i} for # or |-|").grid()
            choices=['|-|', '#']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='i':
            Label(root,text=f"You can remove {i} for | or !").grid()
            choices=['|', '!']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
        elif i=='l':
            Label(root,text=f"You can remove {i} for |_").grid()
            all.append('|_')
            sleep(1)
        elif i=='o':
            Label(root,text=f"You can remove {i} for 0").grid()
            all.append('0')
            sleep(1)
        elif i=='p':
            Label(root,text=f"You can remove {i} for |>").grid()
            all.append('|>')
            sleep(1)
        elif i=='q':
            Label(root,text=f"You can remove {i} for <|").grid()
            all.append('<|')
            sleep(1)
        elif i=='e':
            Label(root,text=f"You can remove {i} for *").grid()
            all.append('*')
            sleep(1)
        elif i=='d':
            Label(root,text=f"You can remove {i} for @|").grid()
            all.append('@|')
            sleep(1)
        elif i=='b':
            Label(root,text=f"You can remove {i} for |@").grid()
            all.append('|@')
            sleep(1)
        elif i=='r':
            Label(root,text=f"You can remove {i} for |^").grid()
            all.append('|^')
            sleep(1)
        elif i=='c':
            Label(root,text=f"You can remove {i} for ( or )").grid()
            choices=['(', ')']
            choose=random.choice(choices)
            all.append(choose)
            sleep(1)
def see_chosen_password():
    Label(root,text='See chosen password: ').grid(row=7,column=0)
    Label(root,text=all).grid(row=7,column=1)
    Label(root,text='Simply just combine the everything in the above output but remember not to overcomplicate the password!',fg='red').grid(row=2,column=5)
b=Button(root,text='Make password safe',command=make_password_safe).grid()
b1=Button(root,text='See chosen password',command=see_chosen_password).grid()
all_letters='snamilopqehdbrck'
root.mainloop()