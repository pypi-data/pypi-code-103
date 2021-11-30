# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2021-09-16 20:04:50
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-11-30 20:46:08
from infrastructure.http_agent.http_request import HttpRequest
from AppCooltestHotWheelsService.fox.models.rf_directory_structure import RFDirectoryStructure
from AppCooltestHotWheelsService.log.serializers.logPushCasesToHtpFBSerializers import LogPushCasesToHtpFBSerializer

class ThirdInteration(object):
	def __init__(self):
		pass

	def pushCaseToFox(self,url='http://10.111.30.234:8088/fox/partner/interface/PushPartnerCases',full=False,env='uat'):
		temp = []
		if full:
			
			for loop in RFDirectoryStructure.objects.filter(script_name__isnull=False,valid=True).values_list('id','name','env','business'):
				temp.append({'partner_id':str(loop[0]),
							 'name':loop[1],
							 'env':loop[2],
							 'business':loop[3]})

			for loop in RFDirectoryStructure.objects.filter(script_name__isnull=False,valid=True,env="uat").values_list('id','name','env','business'):
				temp.append({'partner_id':str(loop[0]),
							 'name':loop[1],
							 'env':'fat',
							 'business':loop[3]})
		else:
			#新增
			for loop in RFDirectoryStructure.objects.filter(script_name__isnull=False,valid=True,env=env,new_case=True).values_list('id','name','env','business'):
				temp.append({'partner_id':str(loop[0]),
							 'name':loop[1],
							 'env':loop[2],
							 'business':loop[3]})
				if env == "uat":
					temp.append({'partner_id':str(loop[0]),
							 'name':loop[1],
							 'env':'fat',
							 'business':loop[3]})

		

		headers = {'content-type': "application/json;charset=UTF-8"}
		data = {
			"type": "1",
			"data": temp
		}
		# print(data)
		response = HttpRequest.post(url,headers=headers,data=data)
		print(response)
		logHtpFB = LogPushCasesToHtpFBSerializer(data={"message":str(response)})
		logHtpFB.is_valid(raise_exception=True)
		logHtpFB.save()


		RFDirectoryStructure.objects.filter(env=env,valid=True,script_name__isnull=False,new_case=True).update(new_case=False)

		return response


