# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-05-29 19:01:35
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-04-29 10:15:04
from infrastructure.base.dealTime import getWeek

JAVA_COV = {
	"refreshUrl": "http://uat-admin.hellobike.com:40001/systemUser/getLoginUserInfo",
	"jacocoDir": "/home/mario/jc/lib",
	"repoDir": '/home/mario/jc/repo',
	"serviceRepoDir": '/home/mario/jc/repo/{service_name}',
	"jarDir": "/home/mario/jc/{week}/{service_name}/{recordID}",
	"destfile": "/home/mario/jc/{week}/{service_name}/destfile/{recordID}",
	"destfileBack": '/home/mario/jc/back/{service_name}/jacoco-it-back.exec',
	"jacocoIt" : "/home/mario/jc/{week}/{service_name}/destfile/{recordID}/{index}.exec",
	# "mergeFile": "/home/mario/jc/{week}/mergeFile/{service_name}/{recordID}",
	# "mdestfile": "/home/mario/jc/{week}/mdestfile/{service_name}/{recordID}",
	"branchMergeFile": "/home/mario/jc/branch/mergeFile/{recordID}", #分支待合并目录
	"branchJacocoIt": "/home/mario/jc/branch/destfile/{recordID}",
	"serviceMergeFile": "/home/mario/jc/service/mergeFile/{recordID}",
	"serviceJacocoIt": "/home/mario/jc/service/destfile/{recordID}",
	"reportDir": "/home/mario/jc/report/{week}/{service_name}/{recordID}",
	"mergeBranchReportDir": "/home/mario/jc/branch/mergeReport/{recordID}",
	"copySourceDir": "/home/mario/jc/{week}/{service_name}/source",	
	"restJacoco": "cd {jacocoDir}&&java -jar jacococli.jar dump --address {ip} --port {port} --reset --retry 1 --destfile ",
	"dumpJacoco": "cd {jacocoDir};java -jar jacococli.jar dump --address {ip} --port {port} --retry 1 --destfile ",
	"diskSizeCommand": "cd /home/mario/jc/{week}/{service_name}/destfile&&du -h --max-depth=1 "
}

def getQueue(business,team,mode):
	if business == "两轮出行":
		if team in ("Cattle","Sharp","Lion"):
			if mode == "manualEnd":
				return "twoRoundsMan"
			elif mode == "continue":
				return "conTwoRounds"
			elif mode == "branchMerge":
				return "twoRoundsBranch"
			else:
				return ""
		else:
			if mode == "manualEnd":
				return "twoRoundsManOther"
			elif mode == "continue":
				return "conTwoRoundsOther"
			elif mode == "branchMerge":
				return "twoRoundsBranchOther"
			else:
				return ""
	elif business == "共享业务":
		if team in ("Ceres","ClearingPlatform","Hermes","Hotel","Marvel","Plaza","Starwar"): #产能 清结算平台 大交通平台 酒店 履约&业财平台 社区 供应链
			if mode == "manualEnd":
				return "shardedBusinessMan"
			elif mode == "continue":
				return "conShardedBusiness"
			elif mode == "branchMerge":
				return "shardedBusinessBranch"
			else:
				return ""
		else:
			if mode == "manualEnd":
				return "shardedBusinessManOther"
			elif mode == "continue":
				return "conShardedBusinessOther"
			elif mode == "branchMerge":
				return "shardedBusinessBranchOther"
			else:
				return ""
	elif business in ["电动车","顺风车"]:
		if mode == "manualEnd":
			return "thirdMan"
		elif mode == "continue":
			return "conThird"
		elif mode == "branchMerge":
				return "thirdBranch"
		else:
			return ""
	else:
		if mode == "manualEnd":
			return "otherMan"
		elif mode == "continue":
			return "conOther"
		elif mode == "branchMerge":
				return "otherBranch"
		else:
			return ""

