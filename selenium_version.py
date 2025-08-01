# -*- coding: UTF-8 -*-
"""
基于Selenium的抢票版本
完全绕过反爬虫限制
"""

import time
import json
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SeleniumTicketBot:
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.item_id = 954702452111  # 商品ID
        self.ticket_price = 180  # 票价
        self.buy_nums = 1  # 购买数量
        self.viewer = ['王博弘']  # 观影人
        
    def setup_driver(self):
        """设置Chrome驱动"""
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        # 添加随机用户代理
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.184 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7204.184 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7204.184 Safari/537.36',
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            # 尝试新版本API
            service = Service('./chromedriver_mac')
            self.driver = webdriver.Chrome(service=service, options=options)
        except TypeError:
            # 兼容旧版本API
            self.driver = webdriver.Chrome(executable_path='./chromedriver_mac', options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self):
        """登录大麦网"""
        print("🔐 开始登录...")
        
        # 检查是否有保存的cookies
        try:
            with open('cookies.pkl', 'rb') as f:
                import pickle
                cookies = pickle.load(f)
                
            self.driver.get('https://www.damai.cn')
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            print("✅ 已加载保存的cookies")
            return True
        except:
            print("📱 需要重新登录")
            
        # 扫码登录
        self.driver.get('https://passport.damai.cn/login')
        
        # 等待用户扫码登录
        print("📱 请在浏览器中扫码登录...")
        try:
            WebDriverWait(self.driver, 180).until(
                EC.url_contains('damai.cn')
            )
            print("✅ 登录成功")
            
            # 保存cookies
            cookies = self.driver.get_cookies()
            with open('cookies.pkl', 'wb') as f:
                import pickle
                pickle.dump(cookies, f)
            print("💾 已保存cookies")
            return True
        except TimeoutException:
            print("❌ 登录超时")
            return False
            
    def check_ticket_status(self):
        """检查票务状态"""
        try:
            # 检查浏览器是否还在运行
            try:
                self.driver.current_url
            except:
                print("❌ 浏览器窗口已关闭，重新启动...")
                self.setup_driver()
                return 'restart'
            
            # 访问商品页面
            url = f'https://detail.damai.cn/item.htm?id={self.item_id}'
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找购买按钮
            try:
                buy_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '立即购买') or contains(text(), '即将开抢') or contains(text(), '缺货登记')]")
            except:
                # 兼容旧版本API
                buy_buttons = self.driver.find_elements_by_xpath("//button[contains(text(), '立即购买') or contains(text(), '即将开抢') or contains(text(), '缺货登记')]")
            
            if buy_buttons:
                button_text = buy_buttons[0].text
                print(f"🎫 当前状态: {button_text}")
                
                if '立即购买' in button_text:
                    return 'buy'
                elif '即将开抢' in button_text:
                    return 'waiting'
                elif '缺货登记' in button_text:
                    return 'sold_out'
            
            return 'unknown'
            
        except Exception as e:
            print(f"❌ 检查状态失败: {e}")
            return 'error'
    
    def buy_ticket(self):
        """购买票务"""
        try:
            print("🚀 开始抢票...")
            
            # 点击立即购买
            try:
                buy_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '立即购买')]"))
                )
            except:
                # 兼容旧版本API
                buy_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '立即购买')]"))
                )
            buy_button.click()
            
            # 等待确认页面
            time.sleep(2)
            
            # 选择观影人
            try:
                viewer_checkbox = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//label[contains(text(), '{self.viewer[0]}')]"))
                )
            except:
                # 兼容旧版本API
                viewer_checkbox = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//label[contains(text(), '{self.viewer[0]}')]"))
                )
            viewer_checkbox.click()
            
            # 提交订单
            try:
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '提交订单')]"))
                )
            except:
                # 兼容旧版本API
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '提交订单')]"))
                )
            submit_button.click()
            
            print("🎉 抢票成功！")
            return True
            
        except Exception as e:
            print(f"❌ 抢票失败: {e}")
            return False
    
    def run_monitor(self):
        """运行监控"""
        print("🔍 开始监控票务状态...")
        
        while self.is_running:
            try:
                status = self.check_ticket_status()
                
                if status == 'buy':
                    print("🎉 检测到开售！开始抢票...")
                    if self.buy_ticket():
                        self.is_running = False
                        break
                elif status == 'waiting':
                    print(f"⏰ 等待开售... {time.strftime('%H:%M:%S')}")
                elif status == 'sold_out':
                    print("❌ 票已售罄")
                    self.is_running = False
                    break
                elif status == 'restart':
                    print("🔄 重新启动浏览器...")
                    time.sleep(5)
                    continue
                else:
                    print(f"❓ 未知状态: {status}")
                
                # 随机延迟
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                time.sleep(5)
    
    def run(self):
        """主运行函数"""
        try:
            self.setup_driver()
            
            if not self.login():
                print("❌ 登录失败")
                return
            
            self.is_running = True
            self.run_monitor()
            
        except Exception as e:
            print(f"❌ 程序异常: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == '__main__':
    bot = SeleniumTicketBot()
    bot.run() 