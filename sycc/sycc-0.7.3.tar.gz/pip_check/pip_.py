def pip_check_test():
	def pip_check_Exist():
		try:
		 	import pip
		except ImportError:
			return False
		else:
			return True
	if pip_check_Exist()==False:
		print('\033[1;1mpip不存在\033[0m')
	else:
		pass
	def pip_check_use():
		import os
		try:
			pip_check_use_global=str(os.popen('pip -V').read().splitlines(False)[0]).split(' ')[0]
			if 'pip' == pip_check_use_global:
				return True
			else:
				return False
		except:
			pass
	#print(pip_check_use())
	if (pip_check_use()==True and pip_check_Exist()==True):
		return 2
if pip_check_test()!=1:
	from get_pip import *
	print('请等待……')
	import time 
	time.sleep(1)
	main()