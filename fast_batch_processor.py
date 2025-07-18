"""
快速批量处理器
专注于高效、稳定地从网站获取数据
"""

import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import List, Dict, Any, Tuple
from anti_crawler import AntiCrawlerHandler
from model_extractor import ModelExtractor
from result_comparator import ResultComparator


class FastBatchProcessor:
    def __init__(self, max_workers: int = 3, request_interval: float = 2.0):
        """
        初始化快速批量处理器
        
        Args:
            max_workers: 最大并发工作线程数
            request_interval: 请求间隔时间（秒）
        """
        self.max_workers = max_workers
        self.request_interval = request_interval
        self.extractor = ModelExtractor()
        self.comparator = ResultComparator()
        
        # 线程安全的统计信息
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'rate_limited': 0,
            'start_time': None
        }
        self.stats_lock = threading.Lock()
        
        # 请求频率控制
        self.last_request_time = {}
        self.request_lock = threading.Lock()
        
        print(f"🚀 快速批量处理器初始化完成 (工作线程: {max_workers}, 间隔: {request_interval}s)")
    
    def _get_crawler_for_thread(self) -> AntiCrawlerHandler:
        """为每个线程获取独立的爬虫实例"""
        thread_id = threading.current_thread().ident
        if not hasattr(self, '_crawlers'):
            self._crawlers = {}
        
        if thread_id not in self._crawlers:
            self._crawlers[thread_id] = AntiCrawlerHandler()
            print(f"🕷️ 为线程 {thread_id} 创建爬虫实例")
        
        return self._crawlers[thread_id]
    
    def _rate_limit_control(self):
        """请求频率控制"""
        with self.request_lock:
            thread_id = threading.current_thread().ident
            current_time = time.time()
            
            if thread_id in self.last_request_time:
                elapsed = current_time - self.last_request_time[thread_id]
                if elapsed < self.request_interval:
                    sleep_time = self.request_interval - elapsed
                    print(f"⏰ 线程 {thread_id} 等待 {sleep_time:.1f}s")
                    time.sleep(sleep_time)
            
            self.last_request_time[thread_id] = time.time()
    
    def _update_stats(self, success: bool, rate_limited: bool = False):
        """更新统计信息"""
        with self.stats_lock:
            self.stats['total_processed'] += 1
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
            if rate_limited:
                self.stats['rate_limited'] += 1
    
    def _search_single_product(self, model_data: Tuple[int, str, str]) -> Dict[str, Any]:
        """
        搜索单个产品（线程安全版本）
        
        Args:
            model_data: (row_index, model, excel_energy_level)
            
        Returns:
            Dict: 搜索和验证结果
        """
        row_index, original_model, excel_energy_level = model_data
        thread_id = threading.current_thread().ident
        
        result = {
            'row_index': row_index,
            'original_model': original_model,
            'excel_energy_level': excel_energy_level,
            'search_success': False,
            'validation_result': '搜不到',
            'details': '',
            'thread_id': thread_id
        }
        
        try:
            # 频率控制
            self._rate_limit_control()
            
            # 获取线程专用的爬虫实例
            crawler = self._get_crawler_for_thread()
            
            # 提取型号
            extracted_model = self.extractor.extract_model(original_model)
            
            # 搜索产品
            search_result = crawler.search_product(extracted_model, max_retries=2)
            
            # 检查是否有实际的记录返回（忽略错误的total字段）
            records = search_result.get('list', []) if search_result else []
            if search_result and len(records) > 0:
                result['search_success'] = True
                
                # 提取能效等级信息
                energy_levels = crawler.extract_energy_levels(search_result)
                
                if energy_levels:
                    # 找到最佳匹配
                    mock_search_result = {
                        'search_success': True,
                        'energy_levels': energy_levels,
                        'extracted_model': extracted_model
                    }
                    
                    best_match = self.comparator.find_best_match(mock_search_result, original_model)
                    
                    if best_match:
                        search_energy_level = best_match['energy_level']
                        
                        # 对比验证
                        validation_result = self.comparator.compare_energy_levels(
                            excel_energy_level, search_energy_level
                        )
                        
                        result['validation_result'] = validation_result
                        result['search_energy_level'] = search_energy_level
                        result['matched_model'] = best_match['model']
                        result['producer'] = best_match.get('producer', '')
                        
                        # 生成详细信息
                        if validation_result == '正确':
                            result['details'] = f"匹配: {best_match['model']} - {search_energy_level}"
                        elif validation_result == '错误':
                            result['details'] = f"不匹配: Excel({excel_energy_level}) vs 搜索({search_energy_level})"
                        elif validation_result == 'Excel缺失':
                            result['details'] = f"Excel缺失，网站显示: {search_energy_level} - {best_match['model']}"
                        else:
                            result['details'] = f"无法确定: {best_match['model']}"
                    else:
                        result['details'] = f"在 {len(energy_levels)} 条记录中未找到匹配"
                else:
                    result['details'] = "无法提取能效等级信息"
            else:
                result['details'] = "搜索无结果"
            
            # 更新统计
            self._update_stats(result['search_success'])
            
        except Exception as e:
            result['details'] = f"处理出错: {str(e)}"
            self._update_stats(False)
            print(f"❌ 线程 {thread_id} 处理 {original_model} 时出错: {str(e)}")
        
        return result
    
    def process_batch(self, products_data: List[Tuple[int, str, str]]) -> List[Dict[str, Any]]:
        """
        批量处理产品数据
        
        Args:
            products_data: [(row_index, model, excel_energy_level), ...]
            
        Returns:
            List[Dict]: 处理结果列表
        """
        print(f"🚀 开始批量处理 {len(products_data)} 个产品")
        print(f"⚙️ 配置: {self.max_workers} 个工作线程, {self.request_interval}s 间隔")
        
        self.stats['start_time'] = time.time()
        results = []
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_data = {
                executor.submit(self._search_single_product, data): data 
                for data in products_data
            }
            
            # 收集结果
            for i, future in enumerate(as_completed(future_to_data), 1):
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 显示进度
                    if i % 10 == 0 or i == len(products_data):
                        self._print_progress(i, len(products_data))
                        
                except Exception as e:
                    data = future_to_data[future]
                    print(f"❌ 任务执行失败: {data[1]} - {str(e)}")
                    
                    # 创建失败结果
                    error_result = {
                        'row_index': data[0],
                        'original_model': data[1],
                        'excel_energy_level': data[2],
                        'search_success': False,
                        'validation_result': '搜不到',
                        'details': f'任务执行失败: {str(e)}'
                    }
                    results.append(error_result)
        
        # 按行索引排序结果
        results.sort(key=lambda x: x['row_index'])
        
        # 打印最终统计
        self._print_final_stats()
        
        return results
    
    def _print_progress(self, current: int, total: int):
        """打印进度信息"""
        with self.stats_lock:
            elapsed = time.time() - self.stats['start_time']
            rate = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / rate if rate > 0 else 0
            
            print(f"📊 进度: {current}/{total} ({current/total*100:.1f}%) | "
                  f"成功: {self.stats['successful']} | "
                  f"失败: {self.stats['failed']} | "
                  f"速度: {rate:.1f}/s | "
                  f"预计剩余: {eta/60:.1f}分钟")
    
    def _print_final_stats(self):
        """打印最终统计信息"""
        with self.stats_lock:
            elapsed = time.time() - self.stats['start_time']
            total = self.stats['total_processed']
            successful = self.stats['successful']
            failed = self.stats['failed']
            rate_limited = self.stats['rate_limited']
            
            print(f"\n🎉 批量处理完成!")
            print(f"📊 最终统计:")
            print(f"  总处理: {total}")
            print(f"  成功: {successful} ({successful/total*100:.1f}%)")
            print(f"  失败: {failed} ({failed/total*100:.1f}%)")
            print(f"  频率限制: {rate_limited}")
            print(f"  总耗时: {elapsed/60:.1f} 分钟")
            print(f"  平均速度: {total/elapsed:.1f} 个/秒")
    
    def close(self):
        """关闭所有爬虫实例"""
        if hasattr(self, '_crawlers'):
            for crawler in self._crawlers.values():
                if hasattr(crawler, 'close'):
                    crawler.close()
            print("🔒 所有爬虫实例已关闭")


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = [
        (1, "格力KFR-35GW/(35586)FNhAb-B1(WIFI）", "一级"),
        (2, "RF12WPdF/NhA-N1JY01(含管)", "一级"),
        (3, "格力GMV-DH120WL/Dc1", "一级"),
        (4, "奥克斯KFR-26GW/ABC123", "二级"),
        (5, "美的KFR-35GW/DEF456", "一级")
    ]
    
    processor = FastBatchProcessor(max_workers=2, request_interval=1.5)
    
    try:
        results = processor.process_batch(test_data)
        
        print(f"\n📋 处理结果:")
        for result in results:
            print(f"  {result['original_model']}: {result['validation_result']} - {result['details']}")
            
    finally:
        processor.close()
