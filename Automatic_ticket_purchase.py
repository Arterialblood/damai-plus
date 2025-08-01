# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Version__ = "2.1.0"
__Description__ = ""
__Created__ = 2022/2/14 10:37 下午
"""

import re
import os
import json
import tools
import argparse
import requests
import threading
import time
from requests import session


class DaMaiTicket:
    def __init__(self):
        # 登录信息
        self.login_cookies = {}
        self.session = session()
        self.login_id: str = 'account'  # 大麦网登录账户名
        self.login_password: str = 'password'  # 大麦网登录密码
        # 以下为抢票必须的参数
        self.item_id: int = 954702452  # 商品id
        self.viewer: list = ['王博弘']  # 在大麦网已填写的观影人
        self.buy_nums: int = 1  # 购买影票数量, 需与观影人数量一致
        self.ticket_price: int = 180  # 购买指定票价

    def step1_get_order_info(self, item_id, commodity_param, ticket_price=None):
        """
        获取点击购买所必须的参数信息
        :param item_id:             商品id
        :param commodity_param:     获取商品购买信息必须的参数
        :param ticket_price:        购买指定价位的票
        :return:
        """
        if not ticket_price:
            print('-' * 10, '票价未填写, 请选择票价', '-' * 10)
            return False

        commodity_param.update({'itemId': item_id})
        headers = {
            'authority': 'detail.damai.cn',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="138", "Not A(Brand";v="99", "Chromium";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.184 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        import random
        import time
        
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 2.0))
        
        response = self.session.get('https://detail.damai.cn/subpage', headers=headers, params=commodity_param)
        
        # 检查响应状态
        if response.status_code != 200:
            print(f'❌ API请求失败: {response.status_code}')
            return None, 0, ''
        
        # 检查响应内容
        if not response.text or response.text.strip() == '':
            print('❌ API返回空数据')
            return None, 0, ''
        
        # 检查是否被反爬虫拦截
        if 'punish' in response.text or 'bixi.alicdn.com' in response.text:
            print('🛡️ 检测到反爬虫拦截，等待重试...')
            time.sleep(random.uniform(3, 5))
            return None, 0, ''
        
        try:
            # 尝试解析JSON
            cleaned_text = response.text.replace('null(', '').replace('__jp0(', '')[:-1]
            ticket_info = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f'❌ JSON解析失败: {e}')
            print(f'响应内容: {response.text[:200]}...')
            return None, 0, ''
        except Exception as e:
            print(f'❌ 数据解析异常: {e}')
            return None, 0, ''
        all_ticket_sku = ticket_info['perform']['skuList']
        sku_id_sequence = 0
        sku_id = ''
        if ticket_price:
            for index, sku in enumerate(all_ticket_sku):
                if sku.get('price') and float(sku.get('price')) == float(ticket_price):
                    sku_id_sequence = index
                    sku_id = sku.get('skuId')
                    break
        return ticket_info, sku_id_sequence, sku_id

    def step2_click_buy_now(self, ex_params, sku_info):
        """
        点击立即购买
        :param ex_params:   点击立即购买按钮所发送请求的必须参数
        :param sku_info:    购买指定商品信息及数量信息
        :return:
        """

        headers = {
            'authority': 'buy.damai.cn',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://detail.damai.cn/',
            'accept-language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7'
        }
        params = {
            'exParams': json.dumps(ex_params),
            'buyParam': sku_info,
            'buyNow': 'true',
            'spm': 'a2oeg.project.projectinfo.dbuy'
        }

        response = self.session.get('https://buy.damai.cn/orderConfirm', headers=headers,
                                    params=params, cookies=self.login_cookies)
        result = re.search('window.__INIT_DATA__[\s\S]*?};', response.text)
        self.login_cookies.update(self.session.cookies)
        try:
            submit_order_info = json.loads(result.group().replace('window.__INIT_DATA__ = ', '')[:-1])
            submit_order_info.update({'output': json.loads(submit_order_info.get('output'))})
        except Exception as e:
            print('-' * 10, '获取购买必备参数异常，请重新解析response返回的参数', '-' * 10)
            print(result.group())
            return False
        return submit_order_info

    def step2_click_confirm_select_seats(self, project_id, perform_id, seat_info, sku_info):
        """ 选座购买，点击确认选座 """
        headers = {
            'authority': 'buy.damai.cn',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://seatsvc.damai.cn/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        }

        params = {
            'exParams': json.dumps({'damai': '1',
                                    'channel': 'damai_app',
                                    'umpChannel': '10002',
                                    'atomSplit': '1',
                                    'seatInfo': seat_info,
                                    'serviceVersion': '2.0.0'}).replace(' ', ''),
            'buyParam': sku_info,
            'buyNow': 'true',
            'projectId': project_id,
            'performId': perform_id,
            'spm': 'a2oeg.selectseat.bottom.dbuy',
        }

        response = requests.get('https://buy.damai.cn/orderConfirm', params=params, cookies=self.login_cookies,
                                headers=headers)
        if response.status_code == 200:
            result = re.search('window.__INIT_DATA__[\s\S]*?};', response.text)
            self.login_cookies.update(self.session.cookies)
            try:
                submit_order_info = json.loads(result.group().replace('window.__INIT_DATA__ = ', '')[:-1])
                submit_order_info.update({'output': json.loads(submit_order_info.get('output'))})
            except Exception as e:
                print('-' * 10, '获取购买必备参数异常，请重新解析response返回的参数', '-' * 10)
                print(result.group())
                return False
            return submit_order_info

    def step3_submit_order(self, submit_order_info, viewer, seat_info=None):
        """
        提交订单所需参数信息
        :param submit_order_info:   最终确认订单所需的所有信息。
        :param viewer:  指定观演人进行购票
        :param seat_info:  座位id
        :return:
        """
        headers = {
            'authority': 'buy.damai.cn',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
            'sec-ch-ua-platform': '"macOS"',
            'origin': 'https://buy.damai.cn',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://buy.damai.cn/orderConfirm?',
            'accept-language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7',
        }

        params = (
            ('feature', '{"returnUrl":"https://orders.damai.cn/orderDetail","serviceVersion":"1.8.5"}'),
            ('submitref', 'undefined'),
        )
        dm_viewer_pc = str([k for k, v in submit_order_info.get('data').items()])
        dm_viewer_pc_id_search = re.search('dmViewerPC_[0-9]*', dm_viewer_pc)
        if dm_viewer_pc_id_search:
            dm_viewer_pc_id = dm_viewer_pc_id_search.group()  # 获取到观演人的 key
            user_list = submit_order_info['data'][dm_viewer_pc_id]['fields']['dmViewerList']
            all_available_user = [name.get('viewerName') for name in user_list]
            if len(set(viewer).intersection(set(all_available_user))) != len(viewer):
                print('-' * 10, '请检查输入的观演人信息与大麦网观演人信息是否一致', '-' * 10)
                return False
            for user in user_list:
                if user.get('viewerName') in viewer:
                    user['isUsed'] = True
            # 若为选座购买, 则需要添加座位id。
            if seat_info:
                seat_info = [seat.get('seatId') for seat in seat_info]
                seat_index = 0
                for user in user_list:
                    if seat_index > len(viewer) - 1:
                        break
                    if user.get('viewerName') in viewer:
                        user['seatId'] = seat_info[seat_index]
                        seat_index += 1
        else:
            print("该场次不需要指定观演人")

        submit_order_info = json.dumps(submit_order_info)
        response = self.session.post('https://buy.damai.cn/multi/trans/createOrder',
                                     headers=headers,
                                     params=params,
                                     data=submit_order_info,
                                     cookies=self.login_cookies)
        buy_status = json.loads(response.text)
        if buy_status.get('success') is True and buy_status.get('module').get('alipayOrderId'):
            print('-' * 10, '抢票成功, 请前往 大麦网->我的大麦->交易中心->订单管理 确认订单', '-' * 10)
            print('alipayOrderId: ', buy_status.get('module').get('alipayOrderId'))
            print('支付宝支付链接: ', buy_status.get('module').get('alipayWapCashierUrl'))

    def run(self):
        if len(self.viewer) != self.buy_nums:
            print('-' * 10, '购买数量与实际观演人数量不符', '-' * 10)
            return
        if os.path.exists('cookies.pkl'):
            cookies = tools.load_cookies()
            self.login_cookies.update(cookies)
        elif 'account' == args.mode.lower():
            self.login_cookies = tools.account_login('account', self.login_id, self.login_password)
        else:
            self.login_cookies = tools.account_login('qr')

        login_status = tools.check_login_status(self.login_cookies)

        if not login_status:
            print('-' * 10, '登录失败, 请检查登录账号信息。若使用保存的cookies，则删除cookies文件重新尝试', '-' * 10)
            return
        elif login_status and not os.path.exists('cookies.pkl'):
            tools.save_cookies(self.login_cookies)

        commodity_param, ex_params = tools.get_api_param()

        submit_order_info = ''
        buy_serial_number = ''
        seat_info = None
        import time
        while True:
            ticket_info, sku_id_sequence, sku_id = self.step1_get_order_info(self.item_id, commodity_param,
                                                                             ticket_price=self.ticket_price)
            ticket_sku_status = ticket_info['skuPagePcBuyBtn']['skuBtnList'][sku_id_sequence]['btnText']
            if ticket_sku_status == '即将开抢':
                print(f'等待开售... 当前时间: {time.strftime("%H:%M:%S")}')
                time.sleep(0.1)  # 100ms刷新间隔，提高响应速度
                continue
            elif ticket_sku_status == '缺货登记':
                print('-' * 10, '手慢了，该票价已经售空: ', ticket_sku_status, '-' * 10)
                return False
            elif ticket_sku_status == '立即购买':
                print(f'🎉 检测到开售！开始抢票... 时间: {time.strftime("%H:%M:%S")}')
                buy_serial_number = '{}_{}_{}'.format(self.item_id, self.buy_nums, sku_id)
                submit_order_info = self.step2_click_buy_now(ex_params, buy_serial_number)
                break
            elif ticket_sku_status == '选座购买':
                # 获取选座购买必备的数据信息。
                city_id, project_id, item_id, perform_id = tools.get_select_seat_params(self.item_id)
                stand_id, seat_price_list = tools.get_seat_dynamic_info(self.login_cookies, project_id, item_id,
                                                                        perform_id)
                api_address = tools.get_select_seat_api(self.login_cookies, perform_id, city_id)
                buy_serial_number = '{}_{}_{}'.format(self.item_id, self.buy_nums, sku_id)
                api_address += str(stand_id) + '.json'
                response = requests.get(api_address)
                if response.status_code != 200:
                    return
                # 获取全部的座位信息
                all_seats_info = json.loads(response.text)
                # 获取可售的座位信息
                valuable_info = tools.get_valuable_seat_id(self.login_cookies, project_id, perform_id, city_id,
                                                           stand_id)
                # 获取 指定抢票价格的 sku_id, price_id
                sku_id, price_id = None, None
                for sku_info in seat_price_list:
                    if self.ticket_price == int(sku_info.get('salePrice')):
                        sku_id = sku_info.get('skuId')
                        price_id = sku_info.get('priceId')
                        break
                if not sku_id or not price_id:
                    print('-' * 10, '获取sku_id失败', '-' * 10)
                    return

                """
                过滤无效座位信息，仅留下符合条件的座位id
                1. 仅保留目标价位下的座位id(暂时只支持一种目标价位)
                2. 过滤掉不可售的座位id。
                """
                valuable_seat = tools.format_valuable_seatid(all_seats_info, valuable_info, price_id)
                # 挑选座位
                seat_info = tools.pick_seat(valuable_seat, stand_id, self.buy_nums)
                submit_order_info = self.step2_click_confirm_select_seats(project_id, perform_id, seat_info,
                                                                          buy_serial_number)
                break
        if not buy_serial_number or not submit_order_info:
            print('-' * 10, '获取购票所需信息失败', '-' * 10)
            return
        self.step3_submit_order(submit_order_info, self.viewer, seat_info)


class EnhancedDaMaiTicket(DaMaiTicket):
    """增强版抢票类，支持多线程和更快的刷新"""
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.threads = []
    
    def rapid_refresh(self, commodity_param, ex_params):
        """快速刷新线程"""
        while self.is_running:
            try:
                ticket_info, sku_id_sequence, sku_id = self.step1_get_order_info(self.item_id, commodity_param,
                                                                                 ticket_price=self.ticket_price)
                
                # 检查数据是否有效
                if ticket_info is None:
                    time.sleep(0.5)  # 数据无效时等待更长时间
                    continue
                
                ticket_sku_status = ticket_info['skuPagePcBuyBtn']['skuBtnList'][sku_id_sequence]['btnText']
                
                if ticket_sku_status == '立即购买':
                    print(f'🚀 线程检测到开售！开始抢票... 时间: {time.strftime("%H:%M:%S")}')
                    buy_serial_number = '{}_{}_{}'.format(self.item_id, self.buy_nums, sku_id)
                    submit_order_info = self.step2_click_buy_now(ex_params, buy_serial_number)
                    if submit_order_info:
                        self.step3_submit_order(submit_order_info, self.viewer, None)
                        self.is_running = False
                        break
                elif ticket_sku_status == '缺货登记':
                    print(f'❌ 线程检测到售罄: {ticket_sku_status}')
                    self.is_running = False
                    break
                
                time.sleep(random.uniform(1, 3))  # 1-3秒随机间隔，避免被反爬虫
            except Exception as e:
                print(f'线程异常: {e}')
                time.sleep(0.1)
    
    def run_enhanced(self, thread_count=3):
        """多线程抢票"""
        print(f'🎯 启动 {thread_count} 个抢票线程...')
        
        if len(self.viewer) != self.buy_nums:
            print('-' * 10, '购买数量与实际观演人数量不符', '-' * 10)
            return
        
        # 登录处理
        if os.path.exists('cookies.pkl'):
            cookies = tools.load_cookies()
            self.login_cookies.update(cookies)
        elif 'account' == args.mode.lower():
            self.login_cookies = tools.account_login('account', self.login_id, self.login_password)
        else:
            self.login_cookies = tools.account_login('qr')

        login_status = tools.check_login_status(self.login_cookies)

        if not login_status:
            print('-' * 10, '登录失败, 请检查登录账号信息。若使用保存的cookies，则删除cookies文件重新尝试', '-' * 10)
            return
        elif login_status and not os.path.exists('cookies.pkl'):
            tools.save_cookies(self.login_cookies)

        commodity_param, ex_params = tools.get_api_param()
        
        # 启动多线程
        self.is_running = True
        for i in range(thread_count):
            thread = threading.Thread(target=self.rapid_refresh, args=(commodity_param, ex_params))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            print(f'✅ 线程 {i+1} 已启动')
        
        # 主线程显示状态
        try:
            while self.is_running:
                print(f'⏰ 等待开售... 当前时间: {time.strftime("%H:%M:%S")}')
                time.sleep(1)
        except KeyboardInterrupt:
            print('\n🛑 用户中断程序')
            self.is_running = False
        
        # 等待所有线程结束
        for thread in self.threads:
            thread.join()
        
        print('🎉 抢票程序结束')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--mode', type=str, default='account', required=False,
                        help='account: account login， QR: Scan QR code login')
    parser.add_argument('--enhanced', action='store_true', help='使用增强版多线程抢票')
    parser.add_argument('--threads', type=int, default=3, help='线程数量（增强版模式）')
    args = parser.parse_args()
    
    if args.enhanced:
        print('🚀 启动增强版多线程抢票模式')
        a = EnhancedDaMaiTicket()
        a.run_enhanced(args.threads)
    else:
        print('📱 启动标准单线程抢票模式')
        a = DaMaiTicket()
        a.run()