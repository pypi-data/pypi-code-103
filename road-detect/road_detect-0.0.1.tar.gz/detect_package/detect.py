from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import frozen_dir
from flask import Flask
from flask import render_template
from flask import request
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
import pickle
import json
import pymysql
import os
app = Flask(__name__)

key = '9999999999999999'.encode('utf-8')
mode = AES.MODE_CBC
iv = b'qqqqqqqqqqqqqqqq'
# 解密函数
def Decrypt(byte_string):
    cryptos = AES.new(key, mode, iv)
    plain_text = cryptos.decrypt(a2b_hex(byte_string))
    return plain_text.rstrip(b'\0')

def score_transform(x, max_pos, min_pos, min_neg, max_neg):
    if x > 0:
        return (100 - 60) * ((x - min_pos) / (max_pos - min_pos))
    elif x < 0:
        return (60 - 0) * ((x - min_neg) / (max_neg-min_neg))
    else:
        return 0

def risk_level(x):
    if x >= 0.507:
        return '高风险'
    elif (x >= 0.2) and (x < 0.507):
        return '中风险'
    else:
        return '低风险'

def risk_level_allroad(x):
    if x >= 39.111888:
        return '高风险'
    elif (x >= 35.300699) and (x < 39.111888):
        return '中风险'
    else:
        return '低风险'

# http://127.0.0.1:5000/detect?path=connect_sql.json
# http://192.168.100.181:5000/detect?path=connect_sql.json

# 定义获取函数
def get_df_from_db(sql,connect_sql):
    db = pymysql.connect(host=connect_sql['host'], user=connect_sql['user'], passwd=connect_sql['passwd'], db=connect_sql['db'])
    cursor = db.cursor()  # 使用cursor()方法获取用于执行SQL语句的游标
    cursor.execute(sql)  # 执行SQL语句
    data = cursor.fetchall()
    # 下面为将获取的数据转化为dataframe格式
    columnDes = cursor.description  # 获取连接对象的描述信息
    #columnNames = [columnDes[0][0],columnDes[1][0]]  # 获取列名
    columnNames = [columnDes[i][0] for i in range(len(columnDes))]  # 获取列名
    df = pd.DataFrame([list(i) for i in data], columns=columnNames)  # 得到的data为二维元组，逐行取出，转化为列表，再转化为df	
    cursor.close()
    db.close()
    return df	
#模型解密，road解密
with open('model-decrypted','wb') as f:
     content=open('model-encrypted','rb').read()
     f.write(Decrypt(content))
with open('road-decrypted','wb') as f:
     content=open('road-encrypted','rb').read()
     f.write(Decrypt(content))

loaded_model = pickle.load(open(frozen_dir.app_path()+"/model-decrypted", "rb"))     # 读取训练后的模型文件
road_id = pd.read_csv(frozen_dir.app_path()+"/road-decrypted")  #读取道路信息

@app.route('/detect')
def detect():
    #get_输入json_path
    json_path= request.args.get("path","")
    #json_path=frozen_dir.app_path()+'/'+json_path
    with open(json_path,'r') as f:
        connect_sql = json.load(f)
    ##连接sql,通过json获取sqlconnect信息
    #sql = "SELECT * FROM data_input" # SQL语句
    sql = connect_sql['sql_ask'] # 根据json_get SQL语句
    # 读取数据
    data = get_df_from_db(sql,connect_sql)
    # 数据预处理
    data['zcs'] = data[['hpdhc', 'xjc', 'xnydc', 'xxxny', 'gc', 'jnc', 'jc', 'wjc', 'mtc', 'qtc']].sum(axis=1)
    data['sdbyxs'] = data['gdsdbzc'] / data['gdsdpjz']
    data['hcbl'] = ((data['hpdhc'] + data['xnydc'] + data['gc']) / data['zcs']).round(2)
    data['hcbl'] = data['hcbl'].fillna(0)
    data['mtcbl'] = (data['mtc'] / data['zcs']).round(2)
    data['mtcbl'] = data['mtcbl'].fillna(0)

    # 获取特征
    features = data[['gdsdpjz','sdbyxs','gdydzs','zcs','hcbl','zbd','ybd','jijiasu','jijiansu','mtcbl','qing','yu','xue','wu','jdcds','jcksl','jcklx','ywlchl','zyfgdkksl','ldfjdcds','ywjck','jckjkcds']]

    # 风险值与shap_value输出
    pre = loaded_model.predict(features)

    explainer = shap.TreeExplainer(loaded_model)
    shap_values = explainer.shap_values(features)
    y_base = explainer.expected_value
    shap.initjs()
    shap_values_output = pd.DataFrame(shap_values)
    shap_values_output.columns = features.columns
    shap_values_output['time'] = data['time']
    shap_values_output['road_id'] = data['road_id']
    predict_prob = loaded_model.predict_proba(features)[:,1]
    shap_values_output['事故概率'] = predict_prob

    # shap_value规整，保存系统文件
    data = shap_values_output.copy()

    # 道路+行为+违法+天气+流量+波动+货车比例
    # 多项整合
    data['道路条件SHAP'] = data['jdcds'] + data['jcksl'] + data['jcklx'] + data['ywlchl'] + data['zyfgdkksl'] + data['ldfjdcds'] + data['ywjck'] + data['jckjkcds']
    data['驾驶行为SHAP'] = data['zbd'] + data['ybd'] + data['jijiasu'] + data['jijiansu']
    data['违法行为SHAP'] = 0
    data['天气条件SHAP'] = data['qing'] + data['yu'] + data['xue'] + data['wu']
    data['流量状况SHAP'] = data['zcs']
    data['速度波动SHAP'] = data['sdbyxs']
    data['货车比例SHAP'] = data['hcbl']

    # 七项分数SHAP转化风险数值
    shap_list = ['道路条件SHAP', '驾驶行为SHAP', '违法行为SHAP', '天气条件SHAP', '流量状况SHAP', '速度波动SHAP', '货车比例SHAP']

    for i in range(len(shap_list)):
        max_pos = max(np.array(data[shap_list[i]]))
        max_neg = min(np.array(data[shap_list[i]]))
        min_pos = data[shap_list[i]].loc[data[shap_list[i]] > 0].min()
        min_neg = data[shap_list[i]].loc[data[shap_list[i]] < 0].max()

        data[shap_list[i]] = data[shap_list[i]].apply(lambda x: score_transform(x, max_pos=max_pos, min_pos=min_pos, min_neg=min_neg, max_neg=max_neg)).astype(int)

    # 读取道路信息，merge道路基础属性
    data = pd.merge(left=data, right=road_id, on=['road_id'], how='left')

    data['Fx'] = 0
    data['xh'] = 0
    data['ldbh'] = data['ldbh'].str[0:14] + str('0')
    data['ldqdzh'] = data['ldqdzh']
    data['ldzdzh'] = data['ldzdzh']
    data['sj'] = data['time']
    data['fxz'] = (data['事故概率'] * 100).round()
    data['ldqdjd'] = data['qd_LON']
    data['ldqdwd'] = data['qd_LAT']
    data['ldzdjd'] = data['zd_LON']
    data['ldzdwd'] = data['zd_LAT']

    data['ssfx'] = data['道路条件SHAP']
    data['xwfx'] = data['驾驶行为SHAP']
    data['jtwffx'] = data['违法行为SHAP']
    data['tqfx'] = data['天气条件SHAP']
    data['llfx'] = data['流量状况SHAP']
    data['sdbdfx'] = data['速度波动SHAP']
    data['hcfx'] = data['货车比例SHAP']

    # 风险等级划分
    data['fxdj'] = data['事故概率'].apply(lambda x: risk_level(x))

    data = data[['Fx','xh','ldbh','ldqdzh','ldzdzh','sj','fxz','fxdj','xwfx','tqfx','ssfx','llfx','sdbdfx','jtwffx','ldqdjd','ldqdwd','ldzdjd','ldzdwd']]

    #data.to_csv('机器学习模型全时空风险.csv')
    data_json=data.to_json(orient=connect_sql['json_orient'],force_ascii=False)
    #data_json=data.to_dict(orient='dict')

    # 全路段风险
    data_road = data.groupby('sj')['fxz'].mean()

    ser_to_df = {'sj': data_road.index, 'fxpf': data_road.values}
    data_road = pd.DataFrame(ser_to_df)

    data_road['zj'] = 0
    data_road['fxpf'] = data_road['fxpf'].round()
    data_road['dldm'] = 'G204'
    data_road['dlmc'] = 'G204'
    data_road['fxdj'] = data_road['fxpf'].apply(lambda x: risk_level_allroad(x))

    data_road = data_road[['zj','dldm','dlmc','fxdj','fxpf','sj']]
    #data_road.to_csv('机器学习模型全路段风险.csv', index=False)
    data_road_json=data_road.to_json(orient=connect_sql['json_orient'],force_ascii=False)
    #data_road_json=data_road.to_dict(orient='dict')
    last_result = {"data_json":data_json,"data_road_json":data_road_json}
    return last_result

class DataCenter(): 
    def get_result(self): 
        os.remove('model-decrypted')
        os.remove('road-decrypted')
        app.run(host="0.0.0.0", port=5000)
#if __name__ == '__main__':
#	os.remove('model-decrypted')
#	os.remove('road-decrypted')
#	app.run(host="0.0.0.0", port=5000)