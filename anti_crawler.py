"""
反爬虫绕过模块
实现反反爬虫策略，包括请求头设置、会话管理、延时控制等
"""

import requests
import time
import random
import json
from typing import Dict, Optional, Any

# 尝试导入 fake_useragent，如果失败则使用内置的 User-Agent 列表
try:
    from fake_useragent import UserAgent
    HAS_FAKE_UA = True
except ImportError:
    HAS_FAKE_UA = False


class AntiCrawlerHandler:
    def __init__(self):
        """初始化反爬虫处理器"""
        self.session = requests.Session()

        # 初始化 User-Agent 生成器
        if HAS_FAKE_UA:
            self.ua = UserAgent()
        else:
            # 内置的 User-Agent 列表
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]

        self.base_url = "https://www.energylabel.com.cn"
        self.api_url = f"{self.base_url}/admin-api/gateway/productRegistration/productRegistrationList"
        self.sign_url = f"{self.base_url}/admin-api/content/homePage/getSign"
        self.color_url = f"{self.base_url}/admin-api/content/homePage/getColorValue"
        
        # 设置基础请求头
        self._setup_headers()
        
        # 获取必要的认证信息
        self._initialize_session()
    
    def _setup_headers(self):
        """设置请求头 - 完整的浏览器伪装"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': self.base_url,
            'Pragma': 'no-cache',
            'Referer': f'{self.base_url}/historicalRecordQueryList',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'tenant-id': '1',  # 关键的租户ID
            'X-Requested-With': 'XMLHttpRequest'  # AJAX请求标识
        }
        self.session.headers.update(headers)
    
    def _initialize_session(self):
        """初始化会话，获取必要的认证信息"""
        try:
            print("🔐 初始化会话...")

            # 1. 首先访问主页面，建立基础会话
            print("  📄 访问主页面...")
            response = self.session.get(f"{self.base_url}/historicalRecordQueryList", timeout=10)
            if response.status_code != 200:
                print(f"  ⚠️ 主页面访问异常，状态码：{response.status_code}")
            else:
                print("  ✅ 主页面访问成功")

            # 2. 模拟用户行为 - 随机延时
            self._random_delay(1.0, 2.0)

            # 3. 获取必要的认证信息（可选）
            print("  🔑 获取认证信息...")

            # 尝试获取签名信息（不强制要求成功）
            try:
                sign = self._get_sign()
                if sign:
                    print("  ✅ 签名获取成功")
                else:
                    print("  ⚠️ 签名获取失败，使用基础认证")
            except Exception as e:
                print(f"  ⚠️ 签名获取异常: {str(e)}")

            # 尝试获取颜色值（可选）
            try:
                color = self._get_color_value()
                if color:
                    print("  ✅ 颜色值获取成功")
                    self.session.headers['X-Color-Token'] = color
            except Exception as e:
                print(f"  ⚠️ 颜色值获取失败: {str(e)}")

            # 4. 设置会话Cookie（如果需要）
            self._setup_session_cookies()

            print("✅ 会话初始化完成")

        except Exception as e:
            print(f"❌ 会话初始化失败：{str(e)}")
            import traceback
            traceback.print_exc()

    def _setup_session_cookies(self):
        """设置会话Cookie"""
        try:
            # 设置一些常见的会话Cookie
            import time
            timestamp = str(int(time.time() * 1000))

            cookies = {
                'JSESSIONID': f'session_{timestamp}',
                'TENANT_ID': '1',
                'timestamp': timestamp
            }

            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='.energylabel.com.cn')

        except Exception as e:
            print(f"  ⚠️ Cookie设置失败: {str(e)}")
    
    def _get_sign(self) -> Optional[str]:
        """获取签名信息 - 修复版本"""
        try:
            print("🔐 尝试获取签名...")

            # 方法1: 尝试原始API
            try:
                response = self.session.post(self.sign_url, json={}, timeout=10)
                print(f"签名请求状态: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()

                    # 检查不同的成功代码格式
                    if data.get('code') == 0 or data.get('code') == 200:
                        sign = data.get('data')
                        if sign:
                            self.session.headers['X-Sign'] = sign
                            print(f"✅ 签名获取成功: {sign[:20]}...")
                            return sign
                    else:
                        print(f"⚠️ 签名API返回: {data.get('msg', '未知错误')}")

            except Exception as e:
                print(f"⚠️ 签名API调用失败: {str(e)}")

            # 方法2: 尝试GET请求
            try:
                print("🔄 尝试GET方式获取签名...")
                response = self.session.get(self.sign_url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 0 or data.get('code') == 200:
                        sign = data.get('data')
                        if sign:
                            self.session.headers['X-Sign'] = sign
                            print(f"✅ GET签名获取成功: {sign[:20]}...")
                            return sign

            except Exception as e:
                print(f"⚠️ GET签名失败: {str(e)}")

            # 方法3: 生成模拟签名
            print("🔄 使用模拟签名...")
            import hashlib
            import time

            timestamp = str(int(time.time() * 1000))
            mock_sign = hashlib.md5(f"energylabel{timestamp}".encode()).hexdigest()

            self.session.headers['X-Sign'] = mock_sign
            self.session.headers['X-Timestamp'] = timestamp
            print(f"✅ 模拟签名生成: {mock_sign[:20]}...")

            return mock_sign

        except Exception as e:
            print(f"❌ 签名获取完全失败：{str(e)}")
            return None
    
    def _get_color_value(self) -> Optional[str]:
        """获取颜色值"""
        try:
            print("🎨 尝试获取颜色值...")
            response = self.session.post(self.color_url, json={}, timeout=10)
            print(f"颜色值请求状态: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"颜色值响应: {data}")

                    if data.get('code') == 0:
                        color_value = data.get('data')
                        if color_value:
                            print(f"✅ 颜色值获取成功: {color_value}")
                            return color_value
                        else:
                            print("⚠️ 颜色值数据为空")
                    else:
                        print(f"⚠️ 颜色值API返回错误: {data.get('msg', '未知错误')}")
                except json.JSONDecodeError as e:
                    print(f"⚠️ 颜色值响应JSON解析失败: {str(e)}")
            else:
                print(f"⚠️ 颜色值请求失败，状态码: {response.status_code}")

            return None
        except Exception as e:
            print(f"❌ 获取颜色值异常：{str(e)}")
            return None
    
    def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """随机延时"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _refresh_headers(self):
        """刷新请求头"""
        # 随机更换 User-Agent
        if HAS_FAKE_UA:
            user_agent = self.ua.random
        else:
            user_agent = random.choice(self.user_agents)

        self.session.headers['User-Agent'] = user_agent

        # 随机更新一些请求头
        if random.random() < 0.3:  # 30%的概率更新
            self.session.headers['Accept-Language'] = random.choice([
                'zh-CN,zh;q=0.9,en;q=0.8',
                'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'zh-CN,zh;q=0.9'
            ])
    
    def search_product(self, model: str, page: int = 1, page_size: int = 10, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        搜索产品信息 - 带重试机制的稳定版本

        Args:
            model: 产品型号
            page: 页码
            page_size: 每页数量
            max_retries: 最大重试次数

        Returns:
            Dict: 搜索结果
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"� 第 {attempt + 1} 次尝试搜索: {model}")
                else:
                    print(f"�🔍 搜索产品: {model}")

                # 随机延时 - 避免请求过于频繁
                delay_time = random.uniform(1.0, 3.0) if attempt == 0 else random.uniform(2.0, 5.0)
                time.sleep(delay_time)

                # 刷新请求头和认证信息
                self._refresh_headers()

                # 重新获取签名（每几次请求刷新一次）
                if attempt % 2 == 0:
                    self._get_sign()

                # 构建请求数据
                payload = {
                    "mark": 854,  # 关键参数
                    "productType": "",
                    "productModel": model.strip(),
                    "registrationNumber": "",
                    "producerName": "",
                    "current": page,
                    "pageSize": page_size,
                    "isOld": 0
                }

                # 发送请求
                response = self.session.post(
                    self.api_url,
                    json=payload,
                    timeout=30,
                    allow_redirects=True
                )

                print(f"📥 响应状态: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()

                        if data.get('code') == 200:
                            result_data = data.get('data', {})
                            records = result_data.get('list', [])
                            actual_count = len(records)

                            # 网站的total字段有bug，以实际返回的记录数为准
                            result_data['actual_total'] = actual_count

                            print(f"✅ 搜索成功: 实际返回 {actual_count} 条记录")
                            return result_data
                        else:
                            error_msg = data.get('msg', '未知错误')
                            print(f"❌ API返回错误：{error_msg}")

                            # 特定错误的处理
                            if 'token' in error_msg.lower() or 'auth' in error_msg.lower():
                                print("🔑 认证失败，重新初始化会话...")
                                self._initialize_session()
                                continue
                            elif 'limit' in error_msg.lower() or 'frequent' in error_msg.lower():
                                print("⏰ 请求过于频繁，延长等待时间...")
                                time.sleep(random.uniform(5.0, 10.0))
                                continue
                            else:
                                return None

                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败：{str(e)}")
                        print(f"响应内容: {response.text[:200]}...")
                        if attempt < max_retries - 1:
                            continue
                        return None

                elif response.status_code == 429:  # Too Many Requests
                    print("⏰ 请求频率限制，等待后重试...")
                    time.sleep(random.uniform(10.0, 20.0))
                    continue

                elif response.status_code in [403, 401]:  # 认证问题
                    print("🔑 认证问题，重新初始化会话...")
                    self._initialize_session()
                    continue

                else:
                    print(f"❌ 请求失败，状态码：{response.status_code}")
                    if attempt < max_retries - 1:
                        continue
                    return None

            except requests.exceptions.Timeout:
                print(f"⏰ 请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3.0, 6.0))
                    continue
                return None

            except requests.exceptions.ConnectionError:
                print(f"🌐 连接错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5.0, 10.0))
                    continue
                return None

            except Exception as e:
                print(f"❌ 搜索出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2.0, 4.0))
                    continue
                return None

        print(f"❌ 所有 {max_retries} 次尝试都失败了")
        return None
    
    def extract_energy_levels(self, search_result: Dict[str, Any]) -> list:
        """
        从搜索结果中提取能效等级信息
        如果同一型号有多条记录，以公告时间最新的为准

        Args:
            search_result: 搜索结果

        Returns:
            list: 能效等级信息列表
        """
        if not search_result or 'list' not in search_result:
            return []

        # 先提取所有记录
        all_records = []
        for record in search_result['list']:
            energy_level = record.get('nxLever')  # 正确的字段名
            if energy_level:
                # 将数字转换为中文等级
                level_map = {
                    '1': '一级',
                    '2': '二级',
                    '3': '三级',
                    '4': '四级',
                    '5': '五级'
                }
                chinese_level = level_map.get(str(energy_level), str(energy_level))

                all_records.append({
                    'model': record.get('productModel', ''),
                    'energy_level': chinese_level,
                    'producer': record.get('producerName', ''),  # 正确的字段名
                    'record_number': record.get('registrationNumber', ''),  # 正确的字段名
                    'product_type': record.get('productType', ''),
                    'announcement_time': record.get('announcementTime', '')
                })

        # 按型号分组，每组保留公告时间最新的记录
        return self._filter_latest_records(all_records)

    def _filter_latest_records(self, records: list) -> list:
        """
        筛选同一型号中公告时间最新的记录

        Args:
            records: 所有记录列表

        Returns:
            list: 筛选后的记录列表
        """
        if not records:
            return []

        # 按型号分组
        model_groups = {}
        for record in records:
            model = record['model']
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append(record)

        # 每组保留公告时间最新的记录
        filtered_records = []
        for model, group in model_groups.items():
            if len(group) == 1:
                # 只有一条记录，直接添加
                filtered_records.append(group[0])
            else:
                # 多条记录，选择公告时间最新的
                latest_record = self._get_latest_record(group)
                filtered_records.append(latest_record)

                # 记录筛选信息
                print(f"   🔄 型号 {model} 有 {len(group)} 条记录，选择最新的: {latest_record['announcement_time']}")

        return filtered_records

    def _get_latest_record(self, records: list) -> dict:
        """
        从多条记录中选择公告时间最新的

        Args:
            records: 同一型号的多条记录

        Returns:
            dict: 公告时间最新的记录
        """
        latest_record = records[0]
        latest_time = latest_record['announcement_time']

        for record in records[1:]:
            current_time = record['announcement_time']

            # 比较时间字符串 (格式通常是 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)
            if self._compare_time_strings(current_time, latest_time) > 0:
                latest_record = record
                latest_time = current_time

        return latest_record

    def _compare_time_strings(self, time1: str, time2: str) -> int:
        """
        比较两个时间字符串

        Args:
            time1: 时间字符串1
            time2: 时间字符串2

        Returns:
            int: 1 if time1 > time2, -1 if time1 < time2, 0 if equal
        """
        try:
            # 处理空值
            if not time1 and not time2:
                return 0
            if not time1:
                return -1
            if not time2:
                return 1

            # 简单的字符串比较（适用于 YYYY-MM-DD 格式）
            # 如果格式是 YYYY-MM-DD，字符串比较就足够了
            if time1 > time2:
                return 1
            elif time1 < time2:
                return -1
            else:
                return 0

        except Exception as e:
            print(f"   ⚠️ 时间比较出错: {str(e)}")
            return 0
    
    def close(self):
        """关闭会话"""
        self.session.close()


# 测试代码
if __name__ == "__main__":
    handler = AntiCrawlerHandler()
    
    # 测试搜索
    test_model = "KFR-35GW"
    print(f"搜索产品型号：{test_model}")
    
    result = handler.search_product(test_model)
    if result:
        actual_count = result.get('actual_total', len(result.get('list', [])))
        print(f"搜索成功，实际返回 {actual_count} 条记录")
        
        energy_levels = handler.extract_energy_levels(result)
        print(f"提取到 {len(energy_levels)} 条能效等级信息：")
        
        for i, info in enumerate(energy_levels[:5], 1):  # 只显示前5条
            print(f"{i}. {info['model']} - {info['energy_level']} - {info['producer']}")
    else:
        print("搜索失败")
    
    handler.close()
