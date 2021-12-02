__version__ = '0.1.2'


import functoins

commands = functoins.commands

def get_command():
	found = False
	comand = input(">> ")
	for com in commands:
		if comand == com:
			run = "functoins."+str(com)+"()"
			exec(run)
			found = True
			get_command()
	if found == False:
		get_command()

def start():
	again = True
	while again == True:
		x = input("Type 1 to sign in and 2 to create an acount or 3 to sign in as a guest- ")
		if x == "1":
			us = functoins.sign_in()
			again = False
			return us
		elif x == "2":
			ig = functoins.sign_up()
			again = False
			return ig
		elif x =="3":
			ii = "guest"
			print("signed in as a gest (some features might not work)")
			return ii
		else:
			print("please type either 1 or 2")
			

user = start()
# functoins.give_rank("user", "rank")
get_command(user)