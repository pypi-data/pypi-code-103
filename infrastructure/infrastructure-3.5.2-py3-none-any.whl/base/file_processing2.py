# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2021-09-13 17:54:53
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-11-30 20:37:26
import os
import platform
import os.path
import json
import django
from AppCooltestHotWheelsService.fox.models.rf_directory_structure import RFDirectoryStructure
from AppCooltestHotWheelsService.application.models.rf_writter import RFWritter
from AppCooltestHotWheelsService.robot.models.rf_case_modify import RFModify
from AppCooltestHotWheelsService.robot.models.rf_case_service import RFService
from AppCooltestHotWheelsService.robot.models.rf_case_interface import RFInterface
from AppCooltestHotWheelsService.robot.models.rf_case_customTag import RFCustomTag
from django.db.models import Q
from django.db import close_old_connections
import time

class FileProcessing(object):
	def __init__(self,rf_project,project_path,env):
		"""
		rf_project : AppHellobikeRfAutoTest
		"""
		self.links = []
		if platform.system() == "Windows":
			self.line = '\\'
		else:
			self.line = '/'

		self.rf_project = rf_project

		self.project_path = project_path

		self.env = env

		# self.rfDirectOB = rfDirectOB

		# self.Q = Q

		# self.close_old_connections = close_old_connections

		self.directStructureList = list(RFDirectoryStructure.objects.filter(~Q(name__icontains='.'),script_name__isnull=True,env=env,valid=True).values_list('structure',flat=True))

		self.scriptStructureList = list(RFDirectoryStructure.objects.filter(script_name__isnull=True,env=env,name__icontains='.',valid=True).values_list('structure',flat=True))

		self.caseNameStructureList = list(RFDirectoryStructure.objects.filter(script_name__isnull=False,env=env,valid=True).values_list('name','structure'))
		# print(self.caseNameStructureList)
		searchOB = RFDirectoryStructure.objects.filter(env=env).order_by('-id')

		if searchOB:
			self.temp = searchOB[0].node_key
		else:
			self.temp = 1



	def __get_root_dir(self,path):
		temp = list()  
		for root, dirs, files in os.walk(path):
			# print(root) #当前目录路径  
			# print(dirs) #当前路径下所有子目录
			# print(files) #当前路径下所有非目录子文件
			for dir in dirs:
				if '.' not in dir:
					temp.append((dir,root + self.line + dir))
			break
			
		return temp

	def __parse_tags(self,line,searchOB,force_tag=[],structure='',env=''):
		#tagContent = [loop.strip() for loop in line.split(' ')[2:] if loop.strip().isalnum()]
		tempList = []
		splitList = [loop.strip() for loop in line.split(' ')[2:] if loop.strip()]
		if structure:
			tempStructure = ''
			for loop in structure.split('/'):
				if tempStructure == '':
					searchStructure = loop + '/__init__.robot'
					tempStructure = loop
				else:
					tempStructure += loop
					searchStructure = tempStructure + '/__init__.robot'
				structureOb = RFDirectoryStructure.objects.filter(structure=searchStructure,env=env,valid=True).order_by('-id')
				if structureOb:
					for structurePeople in  structureOb[0].people.values_list('name',flat=True):
						tempPeople = 'cr_' + structurePeople
						if tempPeople not in splitList:
							splitList.append(tempPeople)
					for structureModify in  structureOb[0].modify_people.values_list('name',flat=True):
						tempModify = 'mo_' + structureModify
						if tempModify not in splitList:
							splitList.append(tempModify)
					for structureService in  structureOb[0].rf_service.values_list('name',flat=True):
						tempService = 'se_' + structureService
						if tempService not in splitList:
							splitList.append(tempService)
					for structureInterface in  structureOb[0].rf_interface.values_list('name',flat=True):
						tempInterface = 'in_' + structureInterface
						if tempInterface not in splitList:
							splitList.append(tempInterface)
					for structureCustomTag in  structureOb[0].rf_customTag.values_list('name',flat=True):
						if structureCustomTag not in splitList:
							splitList.append(structureCustomTag)
					if structureOb[0].single == True:
						if "single" not in splitList:
							splitList.append("single")
				tempStructure += '/'
		if force_tag:
			tempList =  list(set(splitList + force_tag))
		else:
			tempList = splitList
		for tag in tempList:
			if tag:
				if 'cr_' in tag:
					people = tag.split('cr_')[1]
					wrOb = RFWritter.objects.filter(name=people)
					if wrOb:
						user = wrOb.first()
					else:
						user = RFWritter.objects.create(name=people)
					searchOB.people.clear()
					searchOB.people.add(user)
					del wrOb
				elif 'se_' in tag:
					service = tag.split('se_')[1]
					rfSeOb = RFService.objects.filter(name=service)
					if rfSeOb:
						serviceInfo = rfSeOb.first()
					else:
						serviceInfo = RFService.objects.create(name=service)
					searchOB.rf_service.clear()
					searchOB.rf_service.add(serviceInfo)
					del rfSeOb
				elif 'mo_' in tag:
					modify = tag.split('mo_')[1]
					rfMoOb = RFModify.objects.filter(name=modify)
					if rfMoOb:
						modify_people = rfMoOb.first()
					else:
						modify_people = RFModify.objects.create(name=modify)
					searchOB.modify_people.clear()
					searchOB.modify_people.add(modify_people)
					del rfMoOb
				elif 'in_' in tag:
					interface = tag.split('in_')[1]
					rfInOb = RFInterface.objects.filter(name=interface)
					if rfInOb:
						rf_interface = rfMoOb.first()
					else:
						rf_interface = RFInterface.objects.create(name=interface)
					searchOB.rf_interface.clear()
					searchOB.rf_interface.add(rf_interface)
					del rfInOb
				elif 'single' == tag:
					searchOB.single = True
					searchOB.save()
				elif '[tags]' == tag.lower():
					continue
				else:
					rfCuOb = RFCustomTag.objects.filter(name=tag)
					if rfCuOb:
						rf_customTag = rfCuOb.first()
					else:
						rf_customTag = RFCustomTag.objects.create(name=tag)
					searchOB.rf_customTag.clear()
					searchOB.rf_customTag.add(rf_customTag)




	def __parse_forceTags(self,dirPath,searchOB):
		'''
		name 为__init__.robot 上一级目录
		'''
		with open(dirPath,'r') as f:
			while True:
				line=f.readline()

				if not line:
					break

				if line.startswith('Force Tags'):
					self.__parse_tags(line,searchOB)




	def __save_directOrScriptName(self,dirName,dirPath,is_script=False,name=''):
		temp = dirPath.split(self.line)
		structure = '/'.join(temp[temp.index(self.rf_project) + 1 :])

		if is_script:
			searchOB = RFDirectoryStructure.objects.filter(script_name__isnull=True,name__icontains='.',env=self.env,structure=structure,valid=True)
		else:
			searchOB = RFDirectoryStructure.objects.filter(~Q(name__icontains='.'),script_name__isnull=True,env=self.env,structure=structure,valid=True)
		if not searchOB:
			self.temp += 1
			ob = RFDirectoryStructure(name=dirName,env=self.env,structure=structure,node_key=self.temp)
			ob.save()
			if is_script:
				if dirName.strip() == "__init__.robot":
					self.__parse_forceTags(dirPath,ob)
			return self.temp
		else:
			if is_script:
				self.scriptStructureList.remove(structure)
				if dirName.strip() == "__init__.robot":
					self.__parse_forceTags(dirPath,searchOB[0])		
			else:
				self.directStructureList.remove(structure)
			return searchOB[0].node_key

	def __save_caseName(self,dirName,dirPath):
		tempStatus = False
		force_tag = []
		hava_tag = False
		# '/Users/yongfanmao/哈啰mycode/AppHellobikeRfAutoTest/两轮业务C端测试/单车/UAT回归测试收入/单车卡达上限.robot'
		temp = dirPath.split(self.line)
		caseNameSplitRootList = temp[-1].split('.')
		if len(caseNameSplitRootList) == 2:
			temp[-1] = caseNameSplitRootList[0]
		else:
			temp[-1] = '.'.join(caseNameSplitRootList[:-1])
		structure = '/'.join(temp[temp.index(self.rf_project) + 1 :])
		if 'robot' in dirName:
			with open(dirPath,'r') as f:
				while True:
					line=f.readline()

					if not line:
						break

					if not hava_tag:
						if line.startswith('Force Tags'):
							force_tag =[loop.strip() for loop in line.split(' ')[2:] if loop.strip()]
							hava_tag = True
					if line.startswith('*** Test Cases ***'):
						tempStatus = True
					elif line.startswith('*** Keywords ***'):
						tempStatus = False
					elif line.startswith('*** Variables ***'):
						tempStatus = False
					else:
						pass
					if tempStatus:
						if line.startswith('*** Test Cases ***'):
							continue
						if not line.startswith((' ','\n','#','>>','==','<<')): #过滤冲突
							# print(dirName,line,structure)
							searchOB = RFDirectoryStructure.objects.filter(name=line.strip(),env=self.env,structure=structure,valid=True)

							# 	django.db.connections.close_all()

							if not searchOB:
								self.temp += 1
								ob = RFDirectoryStructure(script_name=dirName,name=line.strip(),env=self.env,structure=structure,node_key=self.temp,new_case=True)
								ob.save()
								self.links.append((dirName,line.strip(),structure,self.temp))
							else:
								# print((line.strip(),structure))
								self.caseNameStructureList.remove((line.strip(),structure))
								self.links.append((dirName,line.strip(),structure,searchOB[0].node_key))
							del searchOB
						if '[tags]' in line.lower() and not line.startswith(('#')): # [Tags] [tags] 都算
							searchOB = RFDirectoryStructure.objects.filter(name=prevLine.strip(),env=self.env,structure=structure,valid=True)
							# print(line,prevLine,structure,searchOB)
							if searchOB:
								#line,searchOB,force_tag=[],structure='',env=''):
								self.__parse_tags(line,searchOB[0],force_tag=force_tag,structure=structure,env=self.env)

							del searchOB

						if not '#' in line:
							prevLine = line
						# close_old_connections()
						
						# time.sleep(1)
						# django.db.connections.close_all()




	def __getLinks(self,path,name=''):
		
		for dir in os.listdir(path):
			dirPath = os.path.join(path, dir)
			if os.path.isdir(dirPath):
				if '.' not in dir:
					if name != '':
						count = self.__save_directOrScriptName(dir,dirPath)
						# print(name,dir,self.temp)
						self.links.append((name,dir,dirPath,count))
					childNode = self.__getLinks(dirPath,dir)
			else:
				if name != '' and not dir.startswith('.'):
					count = self.__save_directOrScriptName(dir,dirPath,is_script=True,name=name)
					self.links.append((name,dir,dirPath,count))
					self.__save_caseName(dir,dirPath)
					# self.temp +=1
					# self.links.append((name,dir,dirPath,self.temp))


	def __getRoot(self,path,root):
		
		root_nodes = self.__get_root_dir(path)
		
		for node,path in root_nodes:
			# ('AppHellobikeRfAutoTest', '附件资源', '/Users/yongfanmao/哈啰mycode/AppHellobikeRfAutoTest/附件资源', 65)
			count = self.__save_directOrScriptName(node,path)
			self.links.append((root, node, path, count))


	def __updateValid(self):
		if self.directStructureList:
			RFDirectoryStructure.objects.filter(~Q(name__icontains='.'),script_name__isnull=True,env=self.env,structure__in=self.directStructureList).update(valid=False)
		if self.scriptStructureList:
			RFDirectoryStructure.objects.filter(name__icontains='.',script_name__isnull=True,env=self.env,structure__in=self.scriptStructureList).update(valid=False)
		if self.caseNameStructureList:
			for loop in self.caseNameStructureList:
				RFDirectoryStructure.objects.filter(name=loop[0],env=self.env,structure=loop[1]).update(valid=False)

	def get_directory_tree(self):
		"""
		path 主目录地址
		node 主目录的名称
		"""
		temp = []
		self.__getLinks(self.project_path)
		# print(self.links)
		# import sys
		# sys.exit(1)
		self.__getRoot(self.project_path,self.rf_project)

		tree = self.__get_nodes(self.rf_project)
		# print(json.dumps(tree, indent=4))
		temp.append(tree)

		# print(self.directStructureList,self.scriptStructureList,self.caseNameStructureList)
		self.__updateValid()
		return temp

	def __get_nodes(self,node,path="",id=1):
		d = {}
		if path:
			d['label'] = node
			d['path'] = path
			d['id'] = id
		else:
			d['id'] = 1
			d['label'] = node

		children = self.__get_children(node)
		if children:
			d['children'] = [self.__get_nodes(child[0],child[1],child[2]) for child in children]
		return d

	def __get_children(self,node):
		return [(x[1],x[2],x[3]) for x in self.links if x[0] == node]
					
if __name__ == '__main__':
	f=FileProcessing('AppHellobikeRfAutoTest',"/Users/yongfanmao/哈啰mycode/AppHellobikeRfAutoTest",'uat')
	print(f.get_directory_tree())



