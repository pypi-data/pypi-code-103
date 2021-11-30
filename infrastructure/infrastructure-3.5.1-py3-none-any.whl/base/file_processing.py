# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2021-03-04 19:24:17
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-09-16 11:25:29
import os
import platform
import os.path
import json

class FileProcessing(object):
	def __init__(self):
		self.links = []
		if platform.system() == "Windows":
			self.line = '\\'
		else:
			self.line = '/'

		self.temp = 0 


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

	def __getLinks(self,path,name=''):
		
		for dir in os.listdir(path):
			dirPath = os.path.join(path, dir)
			if os.path.isdir(dirPath):
				if '.' not in dir:
					if name != '':
						self.temp +=1
						# print(name,dir,self.temp)
						self.links.append((name,dir,dirPath,self.temp))
					childNode = self.__getLinks(dirPath,dir)

	def __getRoot(self,path,root):
		
		root_nodes = self.__get_root_dir(path)
		
		for node,path in root_nodes:
			self.temp+= 1
			self.links.append((root, node, path,self.temp))



	def get_directory_tree(self,path,root="AppHellobikeRfAutoTest"):
		"""
		path 主目录地址
		node 主目录的名称
		"""
		temp = []
		self.__getLinks(path)
		self.__getRoot(path,root)
		# print(self.links)
		# import sys
		# sys.exit(1)
		tree = self.__get_nodes(root)
		# print(json.dumps(tree, indent=4))
		temp.append(tree)
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
	f = FileProcessing()
	print(f.get_directory_tree("/Users/yongfanmao/哈啰mycode/AppHellobikeRfAutoTest"))



