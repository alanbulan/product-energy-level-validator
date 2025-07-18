"""
产品型号提取模块
实现中文字符处理逻辑：删除前面连续中文和末尾连续中文，保留中间部分
"""

import re
from typing import Optional


class ModelExtractor:
    def __init__(self):
        """初始化型号提取器"""
        # 中文字符的正则表达式
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    
    def is_chinese(self, char: str) -> bool:
        """
        判断字符是否为中文
        
        Args:
            char: 单个字符
            
        Returns:
            bool: 是否为中文字符
        """
        return bool(self.chinese_pattern.match(char))
    
    def extract_model(self, original_model: str) -> str:
        """
        提取产品型号 (针对数据特点优化版本)
        基于数据分析：80%格力，62%KFR系列，平均长度23.5字符

        Args:
            original_model: 原始产品型号

        Returns:
            str: 提取后的型号
        """
        if not original_model or not isinstance(original_model, str):
            return ""

        model = original_model.strip()
        if not model:
            return ""

        # 针对数据特点的优化处理

        # 1. 检查是否包含版本后缀，如果有则保持完整
        if self._has_version_suffix(model):
            # 只去掉品牌前缀，保留版本后缀
            return self._extract_with_version_suffix(model)

        # 2. 格力品牌特殊处理 (80%的数据)
        if model.startswith('格力'):
            extracted = model[2:]  # 去掉"格力"
            return extracted.strip()

        # 3. 美的空调特殊处理 (数据中发现的格式) - 优先处理
        if model.startswith('美的空调'):
            extracted = model[4:]  # 去掉"美的空调"
            return extracted.strip()

        # 4. 其他常见品牌处理
        common_brands = ['美的', '海尔', '奥克斯', '志高', 'TCL']
        for brand in common_brands:
            if model.startswith(brand):
                extracted = model[len(brand):]
                return extracted.strip()

        # 5. RF系列特殊处理 (无品牌前缀，保持原样)
        if model.startswith('RF'):
            return model

        # 6. 通用中文前缀处理 (原有逻辑)
        return self._extract_generic(model)

    def _extract_generic(self, model: str) -> str:
        """
        通用的中文前缀处理逻辑
        """
        # 找到前面连续中文的结束位置
        start_pos = 0
        for i, char in enumerate(model):
            if not self.is_chinese(char):
                start_pos = i
                break
        else:
            # 如果全是中文，返回原字符串
            return model

        # 从末尾开始，找到连续中文的开始位置
        end_pos = len(model)
        for i in range(len(model) - 1, -1, -1):
            if not self.is_chinese(model[i]):
                end_pos = i + 1
                break
        else:
            # 如果全是中文，返回原字符串
            return model

        # 提取中间部分
        extracted = model[start_pos:end_pos]

        return extracted.strip() if extracted else model

    def _has_version_suffix(self, model: str) -> bool:
        """
        检查是否包含版本后缀

        Args:
            model: 产品型号

        Returns:
            bool: 是否包含版本后缀
        """
        # 常见的版本后缀模式
        version_patterns = [
            r'.*版$',           # 以"版"结尾：上下版、水箱版、2017版
            r'.*pro$',          # 以"pro"结尾：x2pro
            r'.*Pro$',          # 以"Pro"结尾：x2Pro
            r'.*plus$',         # 以"plus"结尾：x2plus
            r'.*Plus$',         # 以"Plus"结尾：x2Plus
            r'.*max$',          # 以"max"结尾：x2max
            r'.*Max$',          # 以"Max"结尾：x2Max
            r'.*mini$',         # 以"mini"结尾：x2mini
            r'.*Mini$',         # 以"Mini"结尾：x2Mini
            r'.*lite$',         # 以"lite"结尾：x2lite
            r'.*Lite$',         # 以"Lite"结尾：x2Lite
        ]

        for pattern in version_patterns:
            if re.match(pattern, model, re.IGNORECASE):
                return True

        return False

    def _extract_with_version_suffix(self, model: str) -> str:
        """
        提取带版本后缀的型号，只去掉品牌前缀

        Args:
            model: 原始型号

        Returns:
            str: 提取后的型号（保留版本后缀）
        """
        # 1. 格力品牌特殊处理
        if model.startswith('格力'):
            return model[2:].strip()

        # 2. 美的空调特殊处理 - 优先处理
        if model.startswith('美的空调'):
            return model[4:].strip()

        # 3. 其他常见品牌处理
        common_brands = ['美的', '海尔', '奥克斯', '志高', 'TCL', '小米', '米家']
        for brand in common_brands:
            if model.startswith(brand):
                return model[len(brand):].strip()

        # 4. 如果没有品牌前缀，保持原样
        return model

    def batch_extract(self, models: list) -> list:
        """
        批量提取型号
        
        Args:
            models: 原始型号列表
            
        Returns:
            list: 提取后的型号列表
        """
        return [self.extract_model(model) for model in models]
    
    def get_extraction_info(self, original_model: str) -> dict:
        """
        获取提取过程的详细信息
        
        Args:
            original_model: 原始产品型号
            
        Returns:
            dict: 包含原始型号、提取型号和处理信息的字典
        """
        if not original_model or not isinstance(original_model, str):
            return {
                'original': original_model,
                'extracted': '',
                'removed_prefix': '',
                'removed_suffix': '',
                'changed': False
            }
        
        model = original_model.strip()
        if not model:
            return {
                'original': original_model,
                'extracted': '',
                'removed_prefix': '',
                'removed_suffix': '',
                'changed': False
            }
        
        # 找到前面连续中文的结束位置
        start_pos = 0
        for i, char in enumerate(model):
            if not self.is_chinese(char):
                start_pos = i
                break
        else:
            # 如果全是中文，返回原字符串
            return {
                'original': original_model,
                'extracted': model,
                'removed_prefix': '',
                'removed_suffix': '',
                'changed': False
            }
        
        # 从末尾开始，找到连续中文的开始位置
        end_pos = len(model)
        for i in range(len(model) - 1, -1, -1):
            if not self.is_chinese(model[i]):
                end_pos = i + 1
                break
        else:
            # 如果全是中文，返回原字符串
            return {
                'original': original_model,
                'extracted': model,
                'removed_prefix': '',
                'removed_suffix': '',
                'changed': False
            }
        
        # 提取各部分
        removed_prefix = model[:start_pos]
        extracted = model[start_pos:end_pos]
        removed_suffix = model[end_pos:]
        
        final_extracted = extracted.strip() if extracted else model
        changed = (removed_prefix != '' or removed_suffix != '')
        
        return {
            'original': original_model,
            'extracted': final_extracted,
            'removed_prefix': removed_prefix,
            'removed_suffix': removed_suffix,
            'changed': changed
        }


# 测试代码
if __name__ == "__main__":
    extractor = ModelExtractor()
    
    # 测试用例
    test_cases = [
        "格力KFR-35GW/(35586)FNhAb-B1(WIFI）",
        "格力FGR7.2Pd/KaNh-N1",
        "RF12WPdF/NhA-N1JY01(含管)",
        "格力GMV-DH120WL/Dc1",
        "格力KFR-26GW/(26504)FNhAc-B1",
        "美的KFR-35GW/BP2DN1Y-TR(B1)",
        "海尔KFR-35GW/03EDS81A",
        "TCL KFRd-35GW/D-XQ11Bp(A1)"
    ]
    
    print("产品型号提取测试：")
    print("=" * 80)
    
    for i, model in enumerate(test_cases, 1):
        info = extractor.get_extraction_info(model)
        print(f"{i}. 原始型号: {info['original']}")
        print(f"   提取型号: {info['extracted']}")
        if info['changed']:
            print(f"   删除前缀: '{info['removed_prefix']}'")
            print(f"   删除后缀: '{info['removed_suffix']}'")
        else:
            print("   无变化")
        print("-" * 40)
