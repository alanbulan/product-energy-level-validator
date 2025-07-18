"""
快速主程序
专注于高效、稳定地获取和验证数据
"""

import sys
import os
from datetime import datetime
from excel_handler import ExcelHandler
from fast_batch_processor import FastBatchProcessor
from relevance_checker import RelevanceChecker


class FastValidator:
    def __init__(self, excel_file: str):
        """
        初始化快速验证器
        
        Args:
            excel_file: Excel文件路径
        """
        self.excel_file = excel_file
        self.excel_handler = ExcelHandler(excel_file)
        self.processor = None
        
    def run_fast_validation(self, max_count: int = None, max_workers: int = 3, 
                           request_interval: float = 2.0):
        """
        运行快速验证
        
        Args:
            max_count: 最大处理数量
            max_workers: 最大并发线程数
            request_interval: 请求间隔（秒）
        """
        print("⚡ 快速产品能效等级验证系统")
        print("=" * 60)
        print("🎯 专注于高效、稳定地获取网站数据")
        print("=" * 60)
        
        # 1. 加载Excel数据
        print("1️⃣ 加载Excel数据...")
        if not self.excel_handler.load_data():
            print("❌ Excel数据加载失败")
            return False
        
        products_data = self.excel_handler.get_product_data()
        if max_count:
            products_data = products_data[:max_count]
        
        print(f"✅ 加载了 {len(products_data)} 条产品数据")
        
        # 2. 初始化快速处理器
        print(f"\n2️⃣ 初始化快速处理器...")
        self.processor = FastBatchProcessor(
            max_workers=max_workers,
            request_interval=request_interval
        )
        
        # 3. 批量处理
        print(f"\n3️⃣ 开始快速批量处理...")
        print(f"⚙️ 并发设置: {max_workers} 线程, {request_interval}s 间隔")
        
        try:
            results = self.processor.process_batch(products_data)
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断处理")
            return False
        except Exception as e:
            print(f"\n❌ 处理过程中出错: {str(e)}")
            return False
        
        # 4. 二次验证 - 相关性检查
        print(f"\n4️⃣ 进行产品相关性检查...")
        results = self._perform_relevance_check(results)

        # 5. 保存结果
        print(f"\n5️⃣ 保存验证结果...")
        if self._save_results(results):
            print("✅ 结果保存成功")
        else:
            print("❌ 结果保存失败")
            return False

        # 6. 显示最终报告
        print(f"\n6️⃣ 验证结果报告...")
        self._print_validation_report(results)
        
        return True

    def _perform_relevance_check(self, results: list) -> list:
        """
        进行产品相关性检查，将不相关的"错误"结果改为"搜不到"

        Args:
            results: 验证结果列表

        Returns:
            list: 更新后的结果列表
        """
        try:
            checker = RelevanceChecker()

            # 统计需要检查的数量
            error_count = sum(1 for r in results if r['validation_result'] == '错误')
            print(f"📊 发现 {error_count} 条'错误'结果，开始相关性检查...")

            if error_count == 0:
                print("✅ 无需进行相关性检查")
                return results

            updated_count = 0

            for i, result in enumerate(results):
                if result['validation_result'] == '错误':
                    original_model = result['original_model']
                    matched_model = result.get('matched_model', '')

                    # 进行相关性检查
                    is_relevant = checker.is_relevant_match(original_model, matched_model)

                    if not is_relevant:
                        # 更新结果
                        result['validation_result'] = '搜不到'
                        result['details'] = f'产品不相关，判定为搜索无效: {original_model}'
                        updated_count += 1

                        print(f"   🔄 已更新: {original_model} -> 搜不到")

            print(f"✅ 相关性检查完成，更新了 {updated_count} 条记录")
            return results

        except Exception as e:
            print(f"⚠️ 相关性检查出错: {str(e)}")
            print("继续使用原始结果...")
            return results

    def _save_results(self, results: list) -> bool:
        """保存验证结果"""
        try:
            # 更新Excel中的验证结果
            for result in results:
                row_index = result['row_index']
                validation_result = result['validation_result']
                details = result.get('details', '')
                
                # 组合结果信息
                final_result = validation_result
                if details and len(details) < 80:
                    final_result += f" - {details}"
                elif details:
                    final_result += f" - {details[:77]}..."
                
                self.excel_handler.update_result(row_index, final_result)
            
            # 保存文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"快速验证结果_{timestamp}.xlsx"
            
            return self.excel_handler.save_data(output_file)
            
        except Exception as e:
            print(f"❌ 保存结果时出错: {str(e)}")
            return False
    
    def _print_validation_report(self, results: list):
        """打印验证报告"""
        total = len(results)
        correct = sum(1 for r in results if r['validation_result'] == '正确')
        incorrect = sum(1 for r in results if r['validation_result'] == '错误')
        not_found = sum(1 for r in results if r['validation_result'] == '搜不到')
        excel_missing = sum(1 for r in results if r['validation_result'] == 'Excel缺失')
        search_success = sum(1 for r in results if r['search_success'])

        print("📊 验证结果统计:")
        print(f"  总数: {total}")
        print(f"  搜索成功: {search_success} ({search_success/total*100:.1f}%)")
        print(f"  搜索失败: {total-search_success} ({(total-search_success)/total*100:.1f}%)")
        print(f"  ✅ 验证正确: {correct} ({correct/total*100:.1f}%)")
        print(f"  ❌ 验证错误: {incorrect} ({incorrect/total*100:.1f}%)")
        print(f"  📋 Excel缺失: {excel_missing} ({excel_missing/total*100:.1f}%)")
        print(f"  ⚠️ 搜不到: {not_found} ({not_found/total*100:.1f}%)")
        
        if correct + incorrect > 0:
            accuracy = correct / (correct + incorrect) * 100
            print(f"  🎯 准确率: {accuracy:.1f}% (在找到结果的情况下)")

        # 数据质量评估
        data_available = correct + incorrect + excel_missing
        if data_available > 0:
            data_quality = (correct + excel_missing) / data_available * 100
            print(f"  📈 数据质量: {data_quality:.1f}% (正确+Excel缺失)")

        # 显示一些示例结果
        print(f"\n📋 示例结果 (前10条):")
        for i, result in enumerate(results[:10], 1):
            if result['validation_result'] == '正确':
                status_icon = "✅"
            elif result['validation_result'] == '错误':
                status_icon = "❌"
            elif result['validation_result'] == 'Excel缺失':
                status_icon = "📋"
            else:
                status_icon = "⚠️"
            print(f"  {i:2d}. {status_icon} {result['original_model'][:30]}... -> {result['validation_result']}")
    
    def close(self):
        """关闭资源"""
        if self.processor:
            self.processor.close()


def main():
    """主函数"""
    print("⚡ 快速验证系统启动")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        excel_file = "新建 Microsoft Excel 工作表.xlsx"
        print(f"使用默认Excel文件: {excel_file}")
    else:
        excel_file = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"❌ 错误：文件 '{excel_file}' 不存在")
        return
    
    # 获取参数
    max_count = None
    max_workers = 3
    request_interval = 2.0
    
    if len(sys.argv) >= 3:
        try:
            max_count = int(sys.argv[2])
            print(f"限制处理数量: {max_count}")
        except ValueError:
            print("⚠️ 处理数量参数无效")
    
    if len(sys.argv) >= 4:
        try:
            max_workers = int(sys.argv[3])
            print(f"并发线程数: {max_workers}")
        except ValueError:
            print("⚠️ 线程数参数无效，使用默认值 3")
    
    if len(sys.argv) >= 5:
        try:
            request_interval = float(sys.argv[4])
            print(f"请求间隔: {request_interval}s")
        except ValueError:
            print("⚠️ 间隔时间参数无效，使用默认值 2.0s")
    
    # 安全检查
    if max_workers > 5:
        print("⚠️ 线程数过多可能被网站封禁，建议不超过5")
        confirm = input("是否继续? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    if request_interval < 1.0:
        print("⚠️ 请求间隔过短可能被网站限制，建议不少于1秒")
        confirm = input("是否继续? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    # 创建验证器并运行
    validator = FastValidator(excel_file)
    
    try:
        success = validator.run_fast_validation(
            max_count=max_count,
            max_workers=max_workers,
            request_interval=request_interval
        )
        
        if success:
            print("\n🎉 快速验证完成！")
            print("💡 如果成功率较低，可以尝试：")
            print("   - 减少并发线程数 (参数3)")
            print("   - 增加请求间隔 (参数4)")
            print("   - 检查网络连接")
        else:
            print("\n❌ 验证过程中出现错误")
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序")
    except Exception as e:
        print(f"\n❌ 程序运行出错：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        validator.close()


if __name__ == "__main__":
    main()
