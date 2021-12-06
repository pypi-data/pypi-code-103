import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def Mymail(*args,**kwargs):
    m = MIMEMultipart()
    m['From']=kwargs.get('send')
    m['Subject'] = kwargs.get('subject')
    textApart = MIMEText(kwargs.get('content'),'html', 'utf-8')
    m.attach(textApart)
    for filepath in args:
        imageApart = MIMEApplication(open(filepath, 'rb').read())
        imageApart.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
        m.attach(imageApart)
    try:
        server = smtplib.SMTP_SSL(kwargs.get('smtp'))
        server.login(kwargs.get('send'), kwargs.get('code'))
        server.sendmail(kwargs.get('send'), kwargs.get('to'), m.as_string())
        print(F'{kwargs.get("subject")}:Send Success')
        server.quit()
        return kwargs.get('to'),True
    except smtplib.SMTPException as err:
        print(F'{kwargs.get("subject")}:Send Error:', err)
        return kwargs.get('to'),False
