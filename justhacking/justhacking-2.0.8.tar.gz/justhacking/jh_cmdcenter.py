#!/usr/bin/python3

# pip installs
import time, random, string, os, re, sys, subprocess
from os import walk
from rich.console import RenderGroup, Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.progress import Progress,track
from rich.tree import Tree
from rich.prompt import Confirm
from rich.columns import Columns
from rich.console import Group
from rich.live import Live
from rich.table import Table
from rich import print

# MyFunctions
import justhacking.jh_matrix  


# configuration
con = Console()


def banner():
  tool_banner = '''
  ░░█ █░█ █▀ ▀█▀   █░█ █░█ █▀▀ █▄▀ ▄█ █▄░█ █▀▀
  █▄█ █▄█ ▄█ ░█░   █▀█ ▀▀█ █▄▄ █░█ ░█ █░▀█ █▄█
  '''
  dev_credits =  "\n\t\t\tA Divinemonk creation!"
  con.print(tool_banner,dev_credits,style="bold green")



#===========================================================
# OTHER FUNCTIONS
#===========================================================
def mr():
  try:
    justhacking.jh_matrix.matrixrain()
  except KeyboardInterrupt:
    exit()

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def isValidURL(str):
 
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")
    
    p = re.compile(regex)

    if (str == None):
        return False

    if(re.search(p, str)):
        return True
    else:
        return False


def clean_screen():
  try:
   subprocess.run('clear')
  except:
   subprocess.run('cls')

def exiting():

  print('\n\n')
  print(Panel.fit(f"[bright_yellow]A Divinemonk creation!"))
  print(Panel.fit(f"[bold red]Twitter: @HrDivinemonk"))

  for x in track(range(25),"[bright_red]Exiting..."):
    time.sleep(0.1)
  print()

#===========================================================



#===========================================================
# Menu Functions
#===========================================================

def social_media():
  con.print(Panel("Social Media Hacking"),style="bold green")

  username = str(Prompt.ask("\n[bright_green]Enter @username to crack"))
  print()


  for x in track(range(25),"[bright_red]Initializing..."):
    time.sleep(0.1) 

  print()
  tree = Tree("Social Media Links")

  tree.add("[deep_pink1]Instagram").add("https://www.instagram.com/" + username)

  tree.add("[dodger_blue1]Facebook").add("https://www.facebook.com/" + username)

  tree.add("[bright_cyan]Twitter").add("https://www.twitter.com/" + username)

  tree.add("[gold1]Snapchat").add("https://www.snapchat.com/" + username)

  tree.add("[red3]Pinterest").add("https://www.pinterest.com/" + username)
  print(tree,'\n')

  time.sleep(1)

  for x in track(range(20),"[bright_cyan]Hacking into database..."):
    time.sleep(0.1) 

  print()

  with Progress(transient=True) as prog :
    exploiting = prog.add_task("Exploiting the websites",total=200) 

    decoding = prog.add_task("Cracking the passwords hashes",total=300) 

    dumping = prog.add_task("Dumping plain text passwords",total=400)

    while not prog.finished:
      prog.update(exploiting,advance=1)
      prog.update(decoding,advance=1)
      prog.update(dumping,advance=1)
      time.sleep(0.1)

  time_str = "[bright_yellow]Account Hacked in " + str(random.uniform(7.5324, 15.5254)) + 's'

  pwd = str(get_random_string(random.randint(5,10)))

  grp = Group(
      Panel(time_str , style='on red1'),
      Panel("[bright_yellow]Username: " + username, style='red1'),
      Panel("[bright_yellow]Password: " + pwd, style='red1')
  )
  print(Panel(grp))

  time.sleep(7)
  print('\n\n')
  goback= Prompt.ask("[bright_green]Enter 'm' to goto Main Menu & 'e' to Exit ", choices=['m', 'e'])
  if goback == 'm':
    return False
  elif goback == 'e':
    return True
    
  



#
def web_hacking():
  con.print(Panel("Web App Hacking"),style="bold green")  


  for x in track(range(25),"[bright_red]Initializing..."):
    time.sleep(0.1) 

  print('\n')
  while True:
    url = Prompt.ask("\nEnter Web App's url")

    if(isValidURL(url) == True):
        break
    
    print("[bold red]Invaild URL Dectected[/bold red]")


  
  for i in track(range(100),f"\n[bright_yellow]Gathering information on {url}"):
        time.sleep(0.1)

  print('\n')
  for i in track(range(50),f"[red1]Launching XSS Attack on {url}"):
        time.sleep(0.1)

  for i in track(range(40),f"[red1]Launching MITM Attack on {url}"):
        time.sleep(0.1)

  for i in track(range(60),f"[red1]Launching DDOS Attack on {url}"):
        time.sleep(0.1)

  for i in track(range(50),f"[red1]Launching SQL Injection on {url}"):
        time.sleep(0.1)

  print('\n\n')
  with Progress(transient=True) as prog :
    xss = prog.add_task("Excuting XSS Attack",total=200) 

    mitm = prog.add_task("Excuting Man In The Middle",total=300) 

    ddos = prog.add_task("Excuting DDOS Attack",total=250)

    sql = prog.add_task("SQL Injection progress",total=280)

    while not prog.finished:
      prog.update(xss,advance=0.7)
      prog.update(mitm,advance=1)
      prog.update(ddos,advance=0.9)
      prog.update(sql,advance=1)
      time.sleep(0.1) 

  
  for i in track(range(100),f"[yellow1]Downloading Hacked DataBase from {url}"):
        time.sleep(0.1)

  print('\n')
  for i in track(range(100),f"[yellow1]Decrypting Downloaded Data..."):
        time.sleep(0.1)

  time.sleep(2)

  start_time = time.time()
  seconds = 2

  for x in walk("/"):
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time > seconds:
      break 
        
    con.print(x,style="bold green")


  con.print(Panel("Decryption Successfull"),style="bold green")

  owner_list = ['AC71ON', 'D15HACK3R', 'D0N\'7CR4P', 'S0M30N3', 'D4RK', 'W3BBER']
  
  ran_val = random.randint(0, 5)
  pwd = str(get_random_string(random.randint(5,10)))

  grp = Group(
      Panel("Web App Details" , style='on red1'),
      Panel("[bright_yellow]Website: " + url, style='red1'),
      Panel("[bright_yellow]Owner Username: " + owner_list[ran_val], style='red1'),
      Panel("[bright_yellow]DataBase Passphrase " + pwd, style='red1')
  )
  print(Panel(grp))

  time.sleep(7)
  print('\n\n')
  goback= Prompt.ask("[bright_green]Enter 'm' to goto Main Menu & 'e' to Exit ", choices=['m', 'e'])
  if goback == 'm':
    return False
  elif goback == 'e':
    return True


  

  

# 
def rev_shell():
  con.print(Panel("Reverse Shell"),style="bold green")

  for x in track(range(25),"[bright_red]Initiating Connection..."):
    time.sleep(0.1)

  time.sleep(1)
  print()
  table = Table()
  table.add_column("ID")
  table.add_column("Connection")
  table.add_column("Port")

  
  with Live(table, refresh_per_second=4): 
      for row in range(11):
          ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
          time.sleep(0.4)
          port = random.randint(1000, 9999)
          table.add_row(f"{row}", f"[bright_red]{ip}", f"[bright_green]{port}")

  tgt = Prompt.ask("\nEnter ID of the ip address", choices=['0','1','2','3','4','5','6','7','8','9','10'])  

  time.sleep(1)
  print('\n\n[bold red]IP Proxy Detected')
  time.sleep(0.5)
  for x in track(range(10),"[bright_red]Retriving Original IP Address..."):
    time.sleep(0.1)

  print()
  ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
  print(Panel.fit(f"[bright_yellow]IP FOUND: {ip}"))

  print()
  for x in track(range(10),"[bright_cyan]Cracking Firewall..."):
    time.sleep(0.1)

  for x in track(range(10),"[bright_cyan]Disabling Security..."):
    time.sleep(0.1)

  for x in track(range(10),"[bright_cyan]Decrypting Passwords..."):
    time.sleep(0.1)

  print()
  time.sleep(1)
  for x in track(range(100),"[bright_green]Getting Reverse Shell..."):
    time.sleep(0.1)

  print()
  print(Panel.fit(f"[bright_blue]Successfully Accessed System"))

  time.sleep(1)
  print()
  for x in track(range(10),"[bright_cyan]Injecting Malware..."):
    time.sleep(0.1)

  for x in track(range(10),"[bright_cyan]Injecting Trojan..."):
    time.sleep(0.1)

  for x in track(range(10),"[bright_cyan]Injecting Backdoors..."):
    time.sleep(0.1)
  time.sleep(1)
  print()

  os = ['Windows 7', 'Windows 10', 'Ubuntu', 'MacOS X', 'Arch Linux', 'Red Hat Linux']
  users = ['AC71ON', 'D15HACK3R', 'D0N\'7CR4P', 'S0M30N3', 'D4RK', 'W3BBER']
  pwd = str(get_random_string(random.randint(5,10))) 
  bit = ['x64_bit', 'x32_bit']

  grp = Group(
      Panel("System Details" , style='on red1'),
      Panel("[bright_yellow]Operating System: "+ os[random.randint(0,5)], style='red1'),
      Panel("[bright_yellow]System Type: " + bit[random.randint(0,1)], style='red1'),
      Panel("[bright_yellow]Login Username: "+ users[random.randint(0, 5)] , style='red1'),
      Panel("[bright_yellow]Login Password "+ pwd , style='red1')
  )
  print(Panel(grp))

  time.sleep(7)
  print('\n\n')
  goback= Prompt.ask("[bright_green]Enter 'm' to goto Main Menu & 'e' to Exit ", choices=['m', 'e'])
  if goback == 'm':
    return False
  elif goback == 'e':
    return True



#
def pwd_crack():
  con.print(Panel("Password Cracker"),style="bold green")

  print()
  for x in track(range(25),"[bright_red]Loading crypto modules"):
    time.sleep(0.1)

  time.sleep(1)
  print()
  for x in track(range(20),"[bright_cyan]Loading breached passwords"):
    time.sleep(0.1)

  for x in track(range(30),"[bright_cyan]Reading comman passwords"):
    time.sleep(0.1)

  for x in track(range(40),"[bright_cyan]AI vulnerable passwords scan"):
    time.sleep(0.1)
  time.sleep(1)
  print()

  suggest = Prompt.ask("Guess the hash type", choices=['md5','sha1','ntml'])  

  print(f"\n[bold green]Using {suggest} algorithm to crack:")

  
  for x in track(range(40),"[bright_red] Cracking..."):
    time.sleep(0.1)

  time.sleep(1)
  print()
  print(Panel.fit(f"[bright_cyan]Successfully Cracked Password Hashes"))

  time.sleep(1)
  print()
  for x in track(range(25),"[bright_red]Decrypting cracked data"):
    time.sleep(0.1)
  
  print('\n\n')
  pwd = str(get_random_string(random.randint(10, 20))) 

  grp = Group(
      Panel("Decrypted Password" , style='on red1'),
      Panel("[bright_yellow]Passphrase: "+ pwd, style='red1'),
  )
  print(Panel(grp))

  time.sleep(7)
  print('\n\n')
  goback= Prompt.ask("[bright_green]Enter 'm' to goto Main Menu & 'e' to Exit ", choices=['m', 'e'])
  if goback == 'm':
    return False
  elif goback == 'e':
    return True



#
def mat_rix():
  con.print(Panel("Clearing Tracks"),style="bold green")

  print()
  print(Panel.fit(f"[bright_cyan]Press any key to stop"))
  time.sleep(2)

  print()
  for x in track(range(25),"[bright_red]Matrix Loading"):
    time.sleep(0.1)
  time.sleep(1)

  mr()

#===========================================================



#===========================================================
# Menu
#===========================================================
def menu():
  try:
    while True:

      stuff = RenderGroup(    
      Panel("1] Social Media Hacking"),    
      Panel("2] Web App Hacking"),    
      Panel("3] Revserse Shell"),    
      Panel("4] Password Cracker"),   
      Panel("5] System Hacked Matrix"),)
      
      
      con.print(Panel(stuff),style="bold green")

      answer = IntPrompt.ask("What you want to do? ",choices=['1','2','3','4','5'])

      print('\n')

      for x in track(range(10),"[bright_green]Extracting exploits..."):
        time.sleep(0.1)

      print('\n\n')

      if answer == 1:
        if social_media():
          exiting()
          exit()
      
      elif answer == 2:
        if web_hacking():
          exiting()
          exit()
      
      elif answer == 3:
        if rev_shell():
          exiting()
          exit()

      elif answer == 4:
        if pwd_crack():
          exiting()
          exit()

      elif answer == 5:
        if mat_rix():
          exiting()
          exit()

      clean_screen()
    
  except KeyboardInterrupt:
    exiting()
    exit()
#===========================================================



#===========================================================
def cmdcenter():

  banner()
  menu()
#===========================================================