#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @CreateDate   : 2021/11/26 11:58
# @Author       : dbartist
# @Email        : dbartist@163.com
# @ScriptFile   : robot.py
# @Project      : pyrobot
# @Describe     :

import requests
import click

# default robot webhook
robot_Webhook="https://oapi.dingtalk.com/robot/send?access_token=4dc3e2cbdaf744338e0a6d218ee8aa4c01a8295ba36677bdc8ff1cdd508b9f90"


@click.command()
@click.option("--content", "-c", type = str, prompt=True, help="send msg,need content str 10.")
@click.option("--webhook", "-w", type = str, prompt=False, default="default", show_default=True, help="robot url.")
@click.option("--attype", "-a", type = click.Choice(['atno','atany','atall'],case_sensitive=False), prompt=True, default='atno',show_default=True,help="at some body.")
@click.option("--atmobiles", "-m", type = str, prompt=False, help="at mobiles like [159xxxxxx01] or [159xxxxxx01,159xxxxxx02,...] .")
def send_dingding(content,webhook,attype,atmobiles):
    try:
        # use default if no webhook1
        if webhook=="default":
            webhook = robot_Webhook

        # check attype
        if attype == "atall":
            msgbody = {"msgtype": "text", "text": {"content": content}, "at": {"isAtAll": True}}
        elif attype == "atany":
            msgbody = {"msgtype": "text", "text": {"content": content}, "at": {"atMobiles":atmobiles,"isAtAll": False}}
        elif attype == "atno":
            msgbody = {"msgtype": "text", "text": {"content": content}}
        else:
            msgbody = {"msgtype": "text", "text": {"content": content}}

        # post msg to dingding
        requests.post(webhook,json=msgbody)
    except Exception as e:
        print(f'error msg：{e}')

def main():
    send_dingding()

if __name__ == "__main__":
    main()
