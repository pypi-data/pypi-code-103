#
# CEO\Owner: vk.com/dan.owner & vk.com/dan.developer
# Produced by PyPi.org
# Module: MyAdmin
#

import os
import sys
import time

os.system('pip install neofetch-win')
os.system('neofetch')
num = 223345
guess = int(input("Для выполнения данного проекта запустите powershell!\nВведите код: "))

if guess == num:
	print("Успешно! Код введен верно.")
	print('Процесс завершен. (Windows powershell was opened!)')
	time.sleep(3)
	os.system('powershell')
	os.system('cls')
elif guess < num:
	print("Заданный код больше чем вы указали.")
else:
	print("Заданный код меньше чем вы указали.")

print("Запуск....")
#class Person:
#    name = "Tom"
# 
#    def display_info(self):
#        print("Привет, меня зовут", self.name)
# 
#person1 = Person()
#person1.display_info()         # Привет, меня зовут Tom
# 
#person2 = Person()
#person2.name = "Sam"
#person2.display_info()         # Привет, меня зовут Sam