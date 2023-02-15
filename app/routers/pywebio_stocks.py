# -*- coding: utf-8 -*-

import os
import time
from pywebio import config
from pywebio.input import *
from pywebio.output import *
from functools import partial
from pywebio.session import run_js, set_env
import akshare as ak

stocks_list_file = 'stocks.ini'


def read_stocks_file():
    if not os.path.isfile(stocks_list_file):
        f = open(stocks_list_file, 'w')
        f.close()

    try:
        with open(stocks_list_file, 'r') as f:
            _stocks = [line.strip('\n') for line in f.readlines()]
            return _stocks
    except Exception as err:
        print(err)
        return False


def check_stock(code):
    try:
        ak.stock_individual_info_em(symbol=code)
        return True
    except:
        return False


def query_stocks_data():
    _data = []
    self_stocks = read_stocks_file()

    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stocks = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'].isin([str(i) for i in self_stocks])].iloc[:,
             [1, 2, 3, 4, 5]]

    for _, row in stocks.iterrows():
        _data.append([row['代码'], row['名称'], row['最新价'], row['涨跌幅']])
    return _data


def check_vaild(code):
    if not check_stock(code):
        return '股票代码不存在'

    _stock = read_stocks_file()
    if code in _stock:
        return '股票已在自选中'


def remove_stock(choice: str, code: int):
    if choice == '删除':
        with open(stocks_list_file, "r") as infile:
            lines = infile.readlines()

        with open(stocks_list_file, "w") as outfile:
            for line in lines:
                if line.strip('\n') != code:
                    outfile.write(line)

    run_js("window.location.href='/query/stocks/'")


@config(theme="minty")
def add_stock():
    state = {
        'title': '自选股票查询',
    }
    set_env(**state)

    run_js("$('footer').remove()")

    put_link(name='查看自选', url='/query/stocks/', new_window=False)
    put_html(r"""<hr width=100% size=3 color=#5151A2 style="FILTER: alpha(opacity=100,finishopacity=0,style=3)">""")

    stock = input_group('添加自选', [
        input(type=TEXT, name='code', validate=check_vaild, placeholder='输入股票代码', ),
        actions('', [
            {'label': '确认', 'value': 'add', 'type': 'submit', },
            {'label': '重置', 'value': 'reset', 'type': 'reset', }
        ], name='action')
    ])

    with open(stocks_list_file, mode='a') as f:
        f.write(str(stock['code']) + '\n')

    run_js("window.location.href='/query/stocks/'")


@config(theme="minty")
def query_stock():
    clear('result')

    state = {
        'title': '自选股票查询',
    }
    set_env(**state)

    run_js("$('footer').remove()")

    put_link(name='添加自选', url='/add/stocks/', new_window=False)
    put_html(r"""<hr width=100% size=3 color=#5151A2 style="FILTER: alpha(opacity=100,finishopacity=0,style=3)">""")

    while True:
        stocks_data = query_stocks_data()

        with use_scope('result', clear=True):
            put_table(
                tdata=[
                    [
                        put_text(stock[0]),
                        put_text(stock[1]),
                        put_text(stock[2]),
                        put_text(stock[3]),
                        put_text("15:00" if int(time.strftime("%H%M")) > 1500 else time.strftime("%H:%M")),
                        put_buttons(['删除'], onclick=partial(remove_stock, code=stock[0]))
                    ] for stock in stocks_data
                ],
                header=[
                    '代码',
                    '名称',
                    '最新价',
                    '涨跌(%)',
                    '时间',
                    '操作',
                ],
                scope='result',
            )

            time.sleep(5)