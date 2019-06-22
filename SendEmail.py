#coding:utf-8
import smtplib
from email.mime.text import MIMEText

class SendEmail:
    global send_user
    global email_host
    global password
    password = "qytwhmerljtwbdja"
    email_host = "smtp.qq.com"
    send_user = "545496535@qq.com"

def send_mail(user_list,sub,content):
    user = "系统通知" + "<" + send_user + ">"
    message = MIMEText(content,_subtype='plain',_charset='utf-8')
    message['Subject'] = sub
    message['From'] = user
    message['To'] = ";".join(user_list)
    server = smtplib.SMTP_SSL(host='smtp.qq.com')
    server.connect(email_host,465)
    server.login(send_user,password)
    server.sendmail(user,user_list,message.as_string())
    print('发送成功')
    server.close()
