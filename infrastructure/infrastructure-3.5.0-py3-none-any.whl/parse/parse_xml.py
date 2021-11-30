# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-05-27 14:21:02
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-04-27 20:51:16

from xml.dom.minidom import parse

class ParseXml(object):
	def __init__(self,file_path):
		self.file_path = file_path
		self.domTree = parse(file_path)
		self.root = self.domTree.documentElement

	def get_designation_node(self,tagName,match):
		"""
			得到指定的tag对应节点内容
			match 为父节点tagName
		"""
		domList = self.root.getElementsByTagName(tagName)
		if not domList:
			return False
		for dom in domList:
			if dom.parentNode.tagName == match:
				content = dom.childNodes[0].data
				if "parent" not in content:
					return content

		return False

	def get_node_data(self,tagName):
		domList = self.root.getElementsByTagName(tagName)
		tempList = []
		for dom in domList:
			tempList.append(dom.childNodes[0].data)
		return tempList

	def append_unit_jacoco(self):
		"""
		向仓库根目录pom文件添加jacoco相关配置
		"""

		with open(self.file_path) as fp:
			content = fp.read()

		if "jacoco" not in content:
			print("jacoco 不在pom中")
			plugins_node = self.root.getElementsByTagName("plugins")[0]

			plugin_node = self.domTree.createElement("plugin")

			groupId_node = self.domTree.createElement("groupId")
			groupId_value = self.domTree.createTextNode("org.jacoco")
			groupId_node.appendChild(groupId_value) # 把文本节点挂到name_node节点
			plugin_node.appendChild(groupId_node)

			artifactId_node = self.domTree.createElement("artifactId")
			artifactId_value = self.domTree.createTextNode("jacoco-maven-plugin")
			artifactId_node.appendChild(artifactId_value) # 把文本节点挂到name_node节点
			plugin_node.appendChild(artifactId_node)

			version_node = self.domTree.createElement("version")
			version_value = self.domTree.createTextNode("0.8.6")
			version_node.appendChild(version_value) # 把文本节点挂到name_node节点
			plugin_node.appendChild(version_node)

			executions_node = self.domTree.createElement("executions")

			execution_node = self.domTree.createElement("execution")

			goals_node = self.domTree.createElement("goals")

			goal_node = self.domTree.createElement("goal")
			goal_value = self.domTree.createTextNode("prepare-agent")
			goal_node.appendChild(goal_value) # 把文本节点挂到name_node节点
			goals_node.appendChild(goal_node)
			execution_node.appendChild(goals_node)
			executions_node.appendChild(execution_node)

			execution_node2 = self.domTree.createElement("execution")

			id_node = self.domTree.createElement("id")
			id_value = self.domTree.createTextNode("report")
			id_node.appendChild(id_value)
			execution_node2.appendChild(id_node)

			phase_node = self.domTree.createElement("phase")
			phase_value = self.domTree.createTextNode("test")
			phase_node.appendChild(phase_value)
			execution_node2.appendChild(phase_node)

			goals_node2 = self.domTree.createElement("goals")
			goal_node2 = self.domTree.createElement("goal")
			goal_value2 = self.domTree.createTextNode("report")
			goal_node2.appendChild(goal_value2)
			goals_node2.appendChild(goal_node2)
			execution_node2.appendChild(goals_node2)
			executions_node.appendChild(execution_node2)

			plugin_node.appendChild(executions_node)
			plugins_node.appendChild(plugin_node)

			with open(self.file_path, 'w') as f:

				# 缩进 - 换行 - 编码

				self.domTree.writexml(f, addindent=' ', encoding='utf-8')

		



		

if __name__ == '__main__':
	#"/Users/yongfanmao/哈啰mycode/jc/AppHelloAnunnakiDSPService/service/pom.xml"
	px = ParseXml("/Users/yongfanmao/helloCode/AppHellobikeRevenueConfigService/pom.xml")
	
	# print(px.get_designation_node("artifactId","project"))
	print(px.get_node_data("module"))




