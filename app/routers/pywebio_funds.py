# -*- coding: utf-8 -*-
import json
import os
import re
import time
import requests
from pywebio import config
from pywebio.input import *
from pywebio.output import *
from functools import partial
from pywebio.session import run_js, set_env

fund_list_file = 'funds.ini'


def query_fund_api(code):
    url = 'http://fundgz.1234567.com.cn/js/%s.js' % code
    headers = {'content-type': 'application/json',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

    try:
        r = requests.get(url, headers=headers)
        content = r.text
        pattern = r'^jsonpgz\((.*)\)'
        search = re.findall(pattern, content)
        name = json.loads(search[0])['name']
        gszzl = json.loads(search[0])['gszzl']
        gztime = json.loads(search[0])['gztime'][-5:]
        return name, gszzl, gztime
    except:
        return False


def read_fund():
    if not os.path.isfile(fund_list_file):
        f = open(fund_list_file, 'w')
        f.close()

    try:
        with open(fund_list_file, 'r') as f:
            _funds = [line.strip('\n') for line in f.readlines()]
            return _funds
    except Exception as err:
        print(err)
        return False


def check_vaild(code):
    if not query_fund_api(code):
        return '基金代码不存在'

    _funds = read_fund()
    if code in _funds:
        return '基金已在自选中'

    if len(_funds) >= 20:
        return '只能添加20个基金'


def remove_fund(choice: str, code: int):
    if choice == '删除':
        with open(fund_list_file, "r") as infile:
            lines = infile.readlines()

        with open(fund_list_file, "w") as outfile:
            for line in lines:
                if line.strip('\n') != code:
                    outfile.write(line)

    run_js("window.location.href='/query/funds/'")


@config(theme="minty")
def index():
    state = {
        'title': '自选查询',
    }
    set_env(**state)

    run_js("$('footer').remove()")

    put_html(r"""<h3>查看自选</h3>""")
    put_html(r"""<hr width=100% size=3 color=#5151A2 style="FILTER: alpha(opacity=100,finishopacity=0,style=3)">""")
    put_link(name='基金', url='/add/funds/', new_window=False)
    put_html(r"""</br>""")
    put_link(name='股票', url='/add/stocks/', new_window=False)


@config(theme="minty")
def add_fund():
    state = {
        'title': '自选基金查询',
    }
    set_env(**state)

    run_js("$('footer').remove()")

    put_link(name='查看自选', url='/query/funds/', new_window=False)
    put_html(r"""<hr width=100% size=3 color=#5151A2 style="FILTER: alpha(opacity=100,finishopacity=0,style=3)">""")

    fund = input_group('添加自选', [
        input(type=TEXT, name='code', validate=check_vaild, placeholder='输入基金代码', ),
        actions('', [
            {'label': '确认', 'value': 'add', 'type': 'submit', },
            {'label': '重置', 'value': 'reset', 'type': 'reset', }
        ], name='action')
    ])

    with open(fund_list_file, mode='a') as f:
        f.write(str(fund['code']) + '\n')

    run_js("window.location.href='/query/funds/'")


@config(theme="minty")
def query_fund():
    clear('result')

    state = {
        'title': '自选基金查询',
    }
    set_env(**state)

    run_js("$('footer').remove()")

    put_link(name='添加自选', url='/add/funds/', new_window=False)
    put_html(r"""<hr width=100% size=3 color=#5151A2 style="FILTER: alpha(opacity=100,finishopacity=0,style=3)">""")

    _funds = read_fund()

    while True:
        fund_info = [[index + 1, value, query_fund_api(value)] for index, value in enumerate(_funds)]

        with use_scope('result', clear=True):
            put_table(
                tdata=[
                    [
                        put_text(fund[0]),
                        put_text(fund[2][0]),
                        put_text(fund[2][1]),
                        put_text(fund[2][2]),
                        put_buttons(['删除'], onclick=partial(remove_fund, code=fund[1]))
                    ] for fund in fund_info
                ],
                header=[
                    '序号',
                    '基金名称',
                    '涨跌(%)',
                    '时间',
                    '操作',
                ],
                scope='result',
            )

            time.sleep(10)