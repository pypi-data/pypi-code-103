import requests
import pandas as pd
import json

# session = requests.Session()
# req = session.get(url)
# print(req.text)
#       print("session status : {}".format(req.status_code))
#         print("ok? : {}".format(req.ok))

def ticker_auth(**param):
    global auth
    global api_key

    # 변수 확인
    if "auth_key" in param.keys(): 
        # print("완료")
        url = "https://www.koreapds.com/api/kpds_ticker_auth.php?auth_key="+param.get("auth_key")
        print(url)
        output = requests.get(url)
        print(output.text)

        auth=1
        api_key = param.get("auth_key")

        return auth, api_key
    else:
        print("입력 값이 잘못되었습니다.")

        auth=0
        api_key=""
        return auth, api_key


def ticker_find(**param):
    # 변수 확인
    if (param.get("auth_key") == "" and auth == 0) or auth == 0:
        param["auth_key"] = ""
    elif (param.get("auth_key") == "" and auth == 1) or auth == 1:
        param["auth_key"] = api_key
        
    if param.get("find_data") == "":
        param["find_data"] = ""    
    elif param.get("find_data") == None:
        print("Error : find_data를 입력해주세요")
        exit()

    auth_key="?auth_key=" + param.get("auth_key")
    find_data="&find_data=" + param.get("find_data")

    url_param = auth_key + find_data

    url = "https://www.koreapds.com/api/kpds_ticker_find.php" + url_param
    print(url)
    output = requests.get(url)
    print(output.text)


def ticker_info(**param):
    # 변수 확인
    if (param.get("auth_key") == "" and auth == 0) or auth == 0:
        param["auth_key"] = ""
    elif (param.get("auth_key") == "" and auth == 1) or auth == 1:
        param["auth_key"] = api_key

    if param.get("ticker") == "":
        param["ticker"] = ""    
    elif param.get("ticker") == None:
        print("Error : ticker 를 입력해주세요")
        exit()
        
    auth_key="?auth_key="+param.get("auth_key")
    ticker="&ticker="+param.get("ticker")

    url_param = auth_key + ticker

    url =  "https://www.koreapds.com/api/kpds_ticker_info.php" + url_param
    print(url)
    output = requests.get(url)
    print(output.text)


def kpds_ticker_raw_data(**param):
    if (param.get("auth_key") == "" and auth == 0) or auth == 0:
        param["auth_key"] = ""
    elif (param.get("auth_key") == "" and auth == 1) or auth == 1:
        param["auth_key"] = api_key

    if param.get("ticker") == "":
        param["ticker"] = ""    
    elif param.get("ticker") == None:
        print("Error : ticker 를 입력해주세요")
        exit()

    

    if param.get("row") == None:
        param["row"] = ""
    if param.get("start_date") == None:
        param["start_date"] = ""       
    if param.get("end_date") == None:
        param["end_date"] = ""       
    if param.get("avg") == None:
        param["avg"] = ""       
    if param.get("sort") == None:
        param["sort"] = ""       
    if param.get("fx") == None:
        param["fx"] = ""       

    auth_key = "?auth_key="+param.get("auth_key")
    ticker = "&ticker="+param.get("ticker")        
    row = "&row="+param.get("row")     
    start_date = "&start_date="+param.get("start_date") 
    end_date = "&end_date="+param.get("end_date") 
    avg = "&avg="+param.get("avg") 
    sort = "&sort="+param.get("sort") 
    fx = "&fx="+param.get("fx") 

    url_param = auth_key + ticker + row + start_date + end_date + avg + sort + sort + fx
    
    url =  "https://www.koreapds.com/api/kpds_ticker_raw_data.php" + url_param
    print(url)
    output = requests.get(url)
    
    # output.text UTF-8로 인코딩된 문자열
    # ////////////////////////////////////////////////////////////
    # STRING -> JSON
    data = json.loads(output.text)
    # print(data)

    # JSON -> series
    # df_header = pd.Series([data['TICKER'], data['TYPE'], data['NAME']])
    # print(df_header)
    
    #JSON -> DATAFRAME
    df = pd.json_normalize(data['DATA'])
    print(df)


def kpds_ticker_raw_data_merge(**param):
    if (param.get("auth_key") == "" and auth == 0) or auth == 0:
        param["auth_key"] = ""
    elif (param.get("auth_key") == "" and auth == 1) or auth == 1:
        param["auth_key"] = api_key

    if param.get("ticker") == "":
        param["ticker"] = ""    
    elif param.get("ticker") == None:
        print("Error : ticker 를 입력해주세요")
        exit()

    if param.get("row") == None:
        param["row"] = ""
    if param.get("start_date") == None:
        param["start_date"] = ""       
    if param.get("end_date") == None:
        param["end_date"] = ""       
    if param.get("avg") == None:
        param["avg"] = ""       
    if param.get("sort") == None:
        param["sort"] = ""       
    if param.get("merge_type ") == None:
        param["merge_type "] = ""       

    auth_key = "?auth_key="+param.get("auth_key")
    ticker = "&ticker="+param.get("ticker")        
    row = "&row="+param.get("row")     
    start_date = "&start_date="+param.get("start_date") 
    end_date = "&end_date="+param.get("end_date") 
    avg = "&avg="+param.get("avg") 
    sort = "&sort="+param.get("sort") 
    merge_type = "&merge_type="+param.get("merge_type") 


    url_param = auth_key + ticker + row + start_date + end_date + avg + sort + sort + merge_type

    url =  "https://www.koreapds.com/api/kpds_ticker_raw_data_merge.php" + url_param
    print(url)
    output = requests.get(url)

    if( (param.get("merge_type")).lower() == "none"):
        # DATA SPLIT
        replace_data = output.text.replace('}{','}  {')
        split_data = replace_data.split('  ')
        
        # STRING -> JSON
        for i in range(len(split_data)):
            data = json.loads(split_data[i])
            df = pd.json_normalize(data['DATA'])
            print(df)
    else:
        # STRING -> JSON
        data = json.loads(output.text)
        
        #JSON -> DATAFRAME
        df = pd.json_normalize(data['DATA'])
        print(df)

    
    