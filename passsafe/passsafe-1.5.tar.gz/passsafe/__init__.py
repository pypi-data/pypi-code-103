from time import *
import random
from tkinter import *
from tkinter import messagebox
root=Tk()
root.title('Make your passwords safe and secure or generate a safe password!')
all=[]
a=Label(root,text='Please enter your password(in small case only): ')
a.grid(row=0,column=0)
password=Entry(root,show='*')
password.grid(row=0,column=1)
def generate_safe_password():
    if (num.get()==1 and special.get()==1):
        passwords=['@|^123','my&&a','gh%$s2']
        chosen_password=random.choice(passwords)
        Label(root,text='Your password is: '+chosen_password).grid()
    elif (num.get()==0 and special.get()==1):
        passwords=['@|^$$','&_&','|_|-|']
        chosen_password=random.choice(passwords)
        Label(root,text='Your password is: '+chosen_password).grid()
    elif (num.get()==1 and special.get()==0):
        passwords=['qwe123','a3m4d376','qwe333rty555']
        chosen_password=random.choice(passwords)
        Label(root,text='Your password is: '+chosen_password).grid()
    else:
        passwords = ['amdintel', 'opencvlalala', 'mycvkokokann']
        chosen_password = random.choice(passwords)
        Label(root, text='Your password is: ' + chosen_password).grid()
def see_your_given_password():
    ask=messagebox.askyesno('Continue', 'Are you sure you want to continue? You can not redo this action!')
    if ask==False:
        messagebox.showinfo('Ok','Ok, we understood!')
    if ask==True:
        messagebox.showinfo('Showed','We showed the password!')
        your_pass=Label(root,text='Your password is: '+password.get(),fg='green').grid(row=0,column=2)
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
b2=Button(root,text='See your given password',command=see_your_given_password).grid()
Label(root,text='-'*50).grid()
Label(root,text='For generating passwords only use this field!').grid()
num=IntVar()
numbers=Checkbutton(root,text='Add numbers',variable=num).grid(sticky=W)
special=IntVar()
special_char=Checkbutton(root,text='Add special characters',variable=special).grid(sticky=W)
b3=Button(root,text='Generate password',command=generate_safe_password).grid()
all_letters='snamilopqehdbrck'
root.mainloop()