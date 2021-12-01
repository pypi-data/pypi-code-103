import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import os

def cargar_registro(model_name,model_code,model_area,model_type,model_met1,model_m1_v,model_met2,model_m2_v,model_ddrf,model_retr,period,result):

    dfFinal = pd.DataFrame({'nombre_modelo': [model_name], 
                        'cod_modelo': [model_code], 
                        'area_modelo': [model_area], 
                        'tipo_modelo': [model_type], 
                        'metrica_modelo_1': [model_met1], 
                        'valor_metrica_modelo_1': [model_m1_v], 
                        'metrica_modelo_2': [model_met2], 
                        'valor_metrica_modelo_2': [model_m2_v], 
                        'flg_data_drift': [model_ddrf], 
                        'flg_recalibracion': [model_retr], 
                        'resultado_proceso': [result]})

    ruta = '/' + model_name + '/' + period + '/'

    cred_object = firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": "monitoreo-gdm",
        "private_key_id": "6418c30962ac48ac61d32437802fb580ceaa2a02",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCx8vJcBdKwo+tH\n8HQI7s0r8QjztxNsykJPQf2ZzlXRYV9jJVLBWFv4hkatOSsBcWsOQPGGDsORHDtE\nj8dYOOhzVu5y2DK1OdBTLCyKRUWEbpxcYIBEBFnLCkMQTGhCzNc3k2etlkWBk8g1\n4RpHidZHWMCRq5UBvHB/BFCO6sDk99xzgSV1Y+XMgaOGefhrQKdCwrYNPeQJ1BE3\nGvJjyIEcU6dhyubsrvCjkzd1IOMK9/nVJzvHIYVh+ArTyxMBaqeK7C7L1R2gWaPt\nix1BLjSx5/pfLzT6KyzlrRcqGqk0Z2g6YZAiNn9soGAbjMd040JZ9ITvuhph8Ity\nNlnfKfixAgMBAAECggEAD7hME7gJ+EPKzaSew4lBA8A7z7fdFe+6MuE8A4HYT/Jf\nqFUMPftNyKMoDDZwJ6T61ZwEGhkkyqVpUPG4pQEF++Zykx+pPxw33Jka6C4daYkR\n9BEsU5Xkzsx9xytQzJHm80ho0MtlIYDKH4Reu3IgRVZAUL4NIEWi1H2vliiD2NYs\n2L5ws1JKAsNh3xKdG8dabZqhMn27AZoGx9xf34ccbEp4wajLRF6RBOYNbGkzXech\ndRSAdfn3H1ReNbLfwy7wbTLfMQ4bU/wzU8L1zvyuQjPbAxCyuNADw8vEzJK6LuVs\nEE9adyQMz7NGrS3z7EEw0mCNfA6D/xzJpOjFpU75pwKBgQDgBvhWA6Q62wIWvILT\n1ZsgVpTF6eNvjug+moDl07R6s+QxnHyz6H0GMgQSYFZsBahktkQ0ljiSSNmpFoSX\nqcQxRTVGrlZQTjsH9hxtr60n3ttsWy7PLbVMp1rtLKlIwIOCD5Hoil8zBs6FzFTG\n7BXVpDnOO3FZPxD7vb8M26iEhwKBgQDLWHgINWnqFZW4JYqfvIQRJl4k+SaFZqVS\nhGhcHYKYIfTivXoFxi/GseSl7xyWaTMLxTFFHopoPZlUAbiWiK3Xb2vDWefveaCH\nrBJ8/D8tMndl5C1rxINK7X0vFQKIduodDbgpqRuBvFQO3U65wRvofr/1qnIYjKyi\nC/R6wO4fBwKBgCMq9PELwUw79Sf8j80RSzjYXqJzBPEOTgcF2hY6FartcnUXS7wy\nUu4WC+2WkfqDKNwmgK6ApoDQTtrsXgQw8kuJwcNGuuYAYePuDqhpW5VWtrtb1Q1Q\n75UI8I0q5ag2EG7qYs1Oa4NnHiSC3wwbI5JWJXzqd/C6pb/fGY67LMkhAoGBAJNR\nrOSFjg5BRQ78Y8oGUcf6/AndV8Md8ngt5U2XM530O+5pR5YXV1WkW/q7mQJ/hLPq\nUR+6WJvcxNDPzmOA8jE6T+BfqmEcxOiGCX7zYPHltgrjnOSOonAOTrtlhUhInqQd\n5GaKVZtQTbXXL8nz1bxC19+rdK3EfO2Jq72jOODRAoGBAL/yymWiZt8jlWJ0K2J1\npLoggEVi5QmHEQWhgL8uvNG3b0L6LTxz5aedgcdHd8fFmdWZNU8aVLnE90zjojOL\n+3ofpe8jV9vYGjlf4CY7cIo0MfTvSMZcjP3AUvDuuvyJH0/pe32+FIKcIaBNkvV0\nkqrfMeL8/BKUkqfpKJ9GZD6c\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-jyyut@monitoreo-gdm.iam.gserviceaccount.com",
        "client_id": "113040927407929871362",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-jyyut%40monitoreo-gdm.iam.gserviceaccount.com"})
    
    databaseURL = "https://monitoreo-gdm-default-rtdb.firebaseio.com/"
    
    if not firebase_admin._apps:
        default_app = firebase_admin.initialize_app(cred_object, {
        'databaseURL':databaseURL
        })

    nuevaCols = [x.replace(".", "") for x in dfFinal.columns]
    dfFinal.columns = nuevaCols

    dicti = dfFinal.to_dict('records')
    dfFinal.reset_index(inplace=True, drop=True)
    dicti2 = dfFinal.to_dict()

    ref = db.reference(ruta)
    ref.set(dicti2) 