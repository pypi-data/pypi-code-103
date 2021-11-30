# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2021-03-05 17:54:44
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-07-02 15:09:14

import datetime
from infrastructure.hb.hb_request import HBRequest
from infrastructure.base.con_mysql import UseMysql
from infrastructure.base.parse_xlsx import ParseXlsx
from infrastructure.base.dealTime import getWeek

class ServiceInfoProcessing(object):
	def __init__(self,coverageLog="",isServer=False):
		self.coverageLog = coverageLog
		self.hbRequest = HBRequest()
		self.teamList = []
		self.serviceInfoList = []
		self.business = ""
		self.isServer = isServer

	def getBusinessTeamsInfos(self,business):
		"""
		得到业务线下所有团队的信息
		"""
		teamList = []
		businessInfos = self.hbRequest.getBussiness('','',isServer=self.isServer)
		for loop in businessInfos[0]: #businessInfos[0] 所有业务线
			if business == loop.get('value'):
				break
		else:
			raise Exception("传入的business错误,没有该业务线")

		for teamInfo in businessInfos[1].get(business,[]): #{'两轮出行': [{'value': 'Tank', 'team_desc': '单车研发'},
			
			teamList.append((teamInfo.get('value'),teamInfo.get('team_desc')))
		# print("\n\n")
		self.teamList = teamList
		self.business = business
		return teamList

	def saveTeamServicesInfo(self):
		"""
		调用前，需要调用得到业务线下所有团队的信息接口
		获取团队下所有服务信息，并保存
		"""
		useMysql = UseMysql()
		for teamInfo in self.teamList:
			temp = []
			temp.append(teamInfo[0])
			serviceInfos = self.hbRequest.getBussinessServiceName(temp,'','',isServer=self.isServer)
			#serviceInfos 该团队下所有服务信息 (可能该团队下没有服务信息)
			for serviceInfo in serviceInfos:

				id_num =  useMysql.filterServiceInfo(serviceInfo["service_name"]) 
				if id_num == 0:		

					sql = """
						insert into helloBikeDB.helloBikeTools_serviceInfos
						(business,service_name,service_description,language,level,
						team,team_description,team_leader,team_leader_email,
						ci_case,is_container,system_aliases,system_description,
						call_applist,os_type,add_time,change_time)
						Values
						("{business}","{service_name}","{service_description}","{language}",
						"{level}","{team}","{team_description}","{team_leader}",
						"{team_leader_email}",{ci_case},{is_container},
						"{system_aliases}","{system_description}",
						"{call_applist}","{os_type}",
						"{add_time}","{change_time}")
						""".format(business=self.business,
						service_name=serviceInfo["service_name"],
						service_description=serviceInfo["description"],
						language=serviceInfo["lang"],
						level=serviceInfo["level"],
						team=teamInfo[0],
						team_description=teamInfo[1],
						team_leader=serviceInfo["team_leader"],
						team_leader_email=serviceInfo["team_leader_email"],
						ci_case=serviceInfo["ci_case"],
						is_container=serviceInfo["is_container"],
						system_aliases=serviceInfo["system_aliases"],
						system_description=serviceInfo["system_description"],
						call_applist=serviceInfo["call_applist"],
						os_type=serviceInfo["os_type"],
						add_time=nowTime,
						change_time=nowTime)

					# print(sql)

					useMysql.executeSql(sql)
					
				else:
					nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

					sql = """
						update helloBikeDB.helloBikeTools_serviceInfos
						set business="{business}",service_name="{service_name}",
						service_description="{service_description}",
						language="{language}",level="{level}",
						team="{team}",team_description="{team_description}",
						team_leader="{team_leader}",
						team_leader_email="{team_leader_email}",
						ci_case={ci_case},is_container={is_container},
						system_aliases="{system_aliases}",
						system_description="{system_description}",
						call_applist="{call_applist}",os_type="{os_type}",
						change_time="{change_time}" where id={id_num}
						""".format(business=self.business,
						service_name=serviceInfo["service_name"],
						service_description=serviceInfo["description"],
						language=serviceInfo["lang"],
						level=serviceInfo["level"],
						team=teamInfo[0],
						team_description=teamInfo[1],
						team_leader=serviceInfo["team_leader"],
						team_leader_email=serviceInfo["team_leader_email"],
						ci_case=serviceInfo["ci_case"],
						is_container=serviceInfo["is_container"],
						system_aliases=serviceInfo["system_aliases"],
						system_description=serviceInfo["system_description"],
						call_applist=serviceInfo["call_applist"],
						os_type=serviceInfo["os_type"],
						change_time=nowTime,
						id_num=id_num)

					# print(sql)
					useMysql.executeSql(sql)

					# break



			# if serviceInfos:
			# 	break

	def statisticalCoverageServices(self):
		"""
		分析级别1，2的服务覆盖率接入量
		只要曾有status为1的就会算接入
		"""
		useMysql = UseMysql()
		nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql = """
		select 
			distinct(b.service_name)
		from
			helloBikeDB.helloBikeJavaCoverage_record AS a
		JOIN
			helloBikeDB.helloBikeTools_service12Infos AS b ON a.service_name = b.service_name
		WHERE
			a.status = 1
		"""
		serviceInfos = useMysql.searchSingleSql(sql)
		for service_name in serviceInfos:
			sql = """
				update helloBikeDB.helloBikeTools_service12Infos
				set coverage={coverage},
				change_time="{change_time}" where service_name="{service_name}"
				""".format(coverage=True,
				change_time=nowTime,
				service_name=service_name[0])

			print(sql)
			useMysql.executeSql(sql)

	def statisticalBusinnes(self):
		"""
		统计各业务线S1,S2已覆盖服务的占比
		"""
		useMysql = UseMysql()
		totalNum = useMysql.searchSingleSql("select count(*) from helloBikeDB.helloBikeTools_service12Infos")
		coveraegNum = useMysql.searchSingleSql("select count(*) from helloBikeDB.helloBikeTools_service12Infos where coverage=True")			
		totalCov = '{:.2f}%'.format(coveraegNum[0][0]/totalNum[0][0]*100)
		print("服务总数:", totalNum[0][0], "服务覆盖总接入数:", coveraegNum[0][0], "接入总覆盖率:",totalCov)
		tempList = []
		businessInfos = useMysql.searchSingleSql("select distinct(business) from helloBikeDB.helloBikeTools_service12Infos")
		for business in businessInfos:
			level1TNum = useMysql.searchSingleSql('select count(*) from helloBikeDB.helloBikeTools_service12Infos where business="{business}" and \
				level=1'.format(business=business[0]))
			level1CNum = useMysql.searchSingleSql('select count(*) from helloBikeDB.helloBikeTools_service12Infos where business="{business}" and \
				level=1 and coverage=True'.format(business=business[0]))
			if level1TNum[0][0] == 0:
				continue
			else:
				level1Cov = '{:.2f}%'.format(level1CNum[0][0]/level1TNum[0][0]*100)

			print(business[0], "S1服务总数:",level1TNum[0][0] , "S1服务接入数:",level1CNum[0][0] , "接入覆盖率:", level1Cov)
			tempList.append([business[0],level1CNum[0][0],level1TNum[0][0],level1Cov])

			# level2TNum = useMysql.searchSingleSql('select count(*) from helloBikeDB.helloBikeTools_service12Infos where business="{business}" and \
			# 	level=2'.format(business=business[0]))
			# level2CNum = useMysql.searchSingleSql('select count(*) from helloBikeDB.helloBikeTools_service12Infos where business="{business}" and \
			# 	level=2 and coverage=True'.format(business=business[0]))
			# if level2TNum[0][0] == 0:
			# 	continue
			# else:
			# 	level2Cov = '{:.2f}%'.format(level2CNum[0][0]/level2TNum[0][0]*100)

			# print(business[0], "S2服务总数:",level2TNum[0][0] , "S2服务接入数:",level2CNum[0][0] , "接入覆盖率:", level2Cov)
			# tempList.append([business[0],level2CNum[0][0],level2TNum[0][0],level2Cov])

		a = ParseXlsx(parsePath="/Users/yongfanmao/Desktop/a.xlsx")
		a.insertXlsx(tempList)

	def statisticalBusinessIncrementCov(self):
		"""
		统计每周各业务线增量覆盖率
		"""
		week_num = getWeek(onlyWeek=True)

		useMysql = UseMysql()
		sql = """select distinct(c.business) from (select 
			b.business,
			b.level,
			a.service_name,
			a.service_desc,
			a.branch,
			a.totalCoverage,
			a.incrementCoverage,
			a.total_lines,
			a.total_coverage_lines,
			a.increment_lines,
			a.increment_coverage_lines
			FROM
			helloBikeDB.helloBikeJavaCoverage_mergeRecord as a join
			helloBikeDB.helloBikeTools_service12Infos AS b ON a.service_name = b.service_name
			WHERE
			a.change_time between '2021-06-28' and '2021-07-03'
			    AND a.increment_lines IS NOT NULL
			ORDER BY b.business , b.level,a.incrementCoverage DESC) as c"""
		businessInfos = useMysql.searchSingleSql(sql)
		tempList = []
		for businessInfo in businessInfos:
			servicesNum_sql = """select count(d.service_name) from (select distinct(c.service_name) from (select 
			b.business,
			b.level,
			a.service_name,
			a.service_desc,
			a.branch,
			a.totalCoverage,
			a.incrementCoverage,
			a.total_lines,
			a.total_coverage_lines,
			a.increment_lines,
			a.increment_coverage_lines
			FROM
			helloBikeDB.helloBikeJavaCoverage_mergeRecord as a join
			helloBikeDB.helloBikeTools_service12Infos AS b ON a.service_name = b.service_name
			WHERE
			a.change_time between '2021-06-28' and '2021-07-03'
			    AND a.increment_lines IS NOT NULL
			ORDER BY b.business , b.level,a.incrementCoverage DESC) as c where c.business="{business}") as d""".format(
				business=businessInfo[0])

			serviceNum=useMysql.searchSingleSql(servicesNum_sql)
			if businessInfo[0]=="交易平台":
				print("交易平台")
			print(serviceNum[0][0])
			
			increment_sql = """select c.increment_lines,c.increment_coverage_lines from (select 
			b.business,
			b.level,
			a.service_name,
			a.service_desc,
			a.branch,
			a.totalCoverage,
			a.incrementCoverage,
			a.total_lines,
			a.total_coverage_lines,
			a.increment_lines,
			a.increment_coverage_lines
			FROM
			helloBikeDB.helloBikeJavaCoverage_mergeRecord as a join
			helloBikeDB.helloBikeTools_service12Infos AS b ON a.service_name = b.service_name
			WHERE
			a.change_time between '2021-06-28' and '2021-07-03'
			    AND a.increment_lines IS NOT NULL
			    
			ORDER BY b.business , b.level,a.incrementCoverage DESC) as c where c.business="{business}";""".format(
				business=businessInfo[0])
			#AND a.incrementCoverage != '0%'
			increments=useMysql.searchSingleSql(increment_sql)
			incrementT = 0
			incrementC = 0
			for increment in increments:
				incrementT += int(increment[0])
				incrementC += int(increment[1])

			incrementCov = '{:.2f}%'.format(incrementC/incrementT*100)
			tempList.append([businessInfo[0],serviceNum[0][0],incrementC,incrementT,incrementCov])
	
		a = ParseXlsx(parsePath="/Users/yongfanmao/Desktop/a.xlsx")
		a.insertXlsx(tempList)	
			

if __name__ == '__main__':
	p = ServiceInfoProcessing()
	# p.getBusinessTeamsInfos("两轮出行")
	# p.saveTeamServicesInfo()
	
	# p.statisticalCoverageServices()
	# p.statisticalBusinnes()
	p.statisticalBusinessIncrementCov()

