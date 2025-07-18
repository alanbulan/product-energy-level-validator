"""
产品相关性检查模块
用于二次验证，检查匹配的产品是否与原始产品真正相关
"""

import re
import difflib
from typing import Dict, List, Any
import pandas as pd


class RelevanceChecker:
    """产品相关性检查器"""
    
    def __init__(self):
        """初始化相关性检查器"""
        # 常见的产品类型关键词
        self.product_categories = {
            '空调': ['空调', 'KFR', 'KF', 'GMV', '制冷', '变频'],
            '冰箱': ['冰箱', 'BCD', '冷藏', '冷冻', '双门', '三门'],
            '洗衣机': ['洗衣机', 'XQG', '滚筒', '波轮', '全自动'],
            '热水器': ['热水器', 'JSQ', 'JSG', '燃气', '电热'],
            '油烟机': ['油烟机', 'CXW', '抽油烟机', '吸油烟机'],
            '燃气灶': ['燃气灶', 'JZT', 'JZ', '灶具'],
            '电视': ['电视', '液晶', 'LED', 'OLED', '智能电视'],
            '吸尘器': ['吸尘器', '除尘器', '清洁器'],
            '净化器': ['净化器', '空气净化', '除甲醛'],
            '微波炉': ['微波炉', '光波炉'],
            '电磁炉': ['电磁炉', '电陶炉'],
            '豆浆机': ['豆浆机', '破壁机'],
            '电饭煲': ['电饭煲', '电饭锅', '智能煲'],
            '椅子': ['椅', '座椅', '办公椅', '电脑椅', '转椅']
        }
    
    def extract_product_category(self, model: str) -> str:
        """
        提取产品类型
        
        Args:
            model: 产品型号
            
        Returns:
            str: 产品类型，如果无法识别返回'未知'
        """
        model_lower = model.lower()
        
        for category, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword.lower() in model_lower:
                    return category
        
        return '未知'
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 使用difflib计算相似度
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        return similarity
    
    def extract_chinese_part(self, model: str) -> str:
        """
        提取型号中的中文部分
        
        Args:
            model: 产品型号
            
        Returns:
            str: 中文部分
        """
        # 提取所有中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', model)
        return ''.join(chinese_chars)
    
    def extract_brand_info(self, model: str) -> str:
        """
        提取品牌信息
        
        Args:
            model: 产品型号
            
        Returns:
            str: 品牌信息
        """
        # 常见品牌关键词
        brands = [
            '格力', '美的', '海尔', '奥克斯', '志高', '春兰', '科龙',
            '小米', '米家', '华为', '荣耀', '苹果', '三星', '索尼',
            '海信', '创维', 'TCL', '长虹', '康佳', '飞利浦',
            '西门子', '博世', '松下', '东芝', '夏普', 'LG'
        ]
        
        model_lower = model.lower()
        for brand in brands:
            if brand in model or brand.lower() in model_lower:
                return brand
        
        return ''
    
    def is_relevant_match(self, original_model: str, matched_model: str, 
                         original_producer: str = '', matched_producer: str = '') -> bool:
        """
        检查匹配的产品是否与原始产品相关
        
        Args:
            original_model: 原始产品型号
            matched_model: 匹配到的产品型号
            original_producer: 原始生产商
            matched_producer: 匹配到的生产商
            
        Returns:
            bool: 是否相关
        """
        # 1. 检查产品类型是否一致
        original_category = self.extract_product_category(original_model)
        matched_category = self.extract_product_category(matched_model)
        
        if original_category != '未知' and matched_category != '未知':
            if original_category != matched_category:
                print(f"   🔍 产品类型不匹配: {original_category} vs {matched_category}")
                return False
        
        # 2. 对于纯汉字+数字的型号，进行特殊检查
        if self.is_chinese_with_number(original_model):
            return self.check_chinese_model_relevance(original_model, matched_model)
        
        # 3. 检查品牌信息
        original_brand = self.extract_brand_info(original_model)
        matched_brand = self.extract_brand_info(matched_model)
        
        if original_brand and matched_brand and original_brand != matched_brand:
            print(f"   🔍 品牌不匹配: {original_brand} vs {matched_brand}")
            return False
        
        # 4. 检查生产商信息
        if original_producer and matched_producer:
            producer_similarity = self.calculate_text_similarity(original_producer, matched_producer)
            if producer_similarity < 0.3:
                print(f"   🔍 生产商不匹配: {original_producer} vs {matched_producer}")
                return False
        
        # 5. 基本的型号相似度检查
        model_similarity = self.calculate_text_similarity(original_model, matched_model)
        if model_similarity < 0.2:  # 很低的相似度阈值
            print(f"   🔍 型号相似度过低: {model_similarity:.2f}")
            return False
        
        return True
    
    def is_chinese_with_number(self, model: str) -> bool:
        """
        检查是否为纯汉字+数字的型号
        
        Args:
            model: 产品型号
            
        Returns:
            bool: 是否为纯汉字+数字
        """
        # 去除空格和标点
        clean_model = re.sub(r'[^\u4e00-\u9fff\w]', '', model)
        
        # 检查是否主要由汉字组成，末尾有数字
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', clean_model))
        has_number = bool(re.search(r'\d', clean_model))
        
        # 汉字占比超过50%
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', clean_model))
        total_count = len(clean_model)
        
        if total_count == 0:
            return False
        
        chinese_ratio = chinese_count / total_count
        
        return has_chinese and has_number and chinese_ratio > 0.5
    
    def check_chinese_model_relevance(self, original_model: str, matched_model: str) -> bool:
        """
        检查纯汉字+数字型号的相关性
        
        Args:
            original_model: 原始型号（如"米家无线吸尘器2"）
            matched_model: 匹配型号（如"电脑椅2017版"）
            
        Returns:
            bool: 是否相关
        """
        # 提取汉字部分
        original_chinese = self.extract_chinese_part(original_model)
        matched_chinese = self.extract_chinese_part(matched_model)
        
        print(f"   🔍 汉字部分对比: '{original_chinese}' vs '{matched_chinese}'")
        
        # 计算汉字部分的相似度
        chinese_similarity = self.calculate_text_similarity(original_chinese, matched_chinese)
        
        print(f"   🔍 汉字相似度: {chinese_similarity:.2f}")
        
        # 如果汉字部分相似度很低，判定为不相关
        if chinese_similarity < 0.3:
            return False
        
        return True
    
    def perform_relevance_check(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        对验证结果进行相关性检查
        
        Args:
            results_df: 验证结果DataFrame
            
        Returns:
            pd.DataFrame: 更新后的结果
        """
        print("🔍 开始进行产品相关性检查...")
        print("=" * 60)
        
        updated_count = 0
        
        for index, row in results_df.iterrows():
            validation_result = row.get('验证结果', '')
            
            # 只检查"错误"的结果
            if validation_result == '错误':
                original_model = row.get('产品型号', '')
                matched_model = row.get('匹配型号', '')
                
                print(f"\n检查 {index + 1}: {original_model}")
                print(f"   匹配到: {matched_model}")
                
                # 进行相关性检查
                is_relevant = self.is_relevant_match(original_model, matched_model)
                
                if not is_relevant:
                    # 更新结果为"搜不到"
                    results_df.at[index, '验证结果'] = '搜不到'
                    results_df.at[index, '详细信息'] = f'产品不相关，原始搜索无效: {original_model}'
                    updated_count += 1
                    print(f"   ✅ 已更新为'搜不到'")
                else:
                    print(f"   ✅ 确认相关，保持'错误'")
        
        print(f"\n" + "=" * 60)
        print(f"🎯 相关性检查完成!")
        print(f"📊 更新了 {updated_count} 条记录从'错误'改为'搜不到'")
        print("=" * 60)
        
        return results_df


def main():
    """测试函数"""
    checker = RelevanceChecker()
    
    # 测试用例
    test_cases = [
        ("米家无线吸尘器2", "电脑椅2017版", False),
        ("格力KFR-35GW", "KFR-35GW/FNhAa-B1", True),
        ("美的空调KFR-26GW", "格力KFR-26GW", False),
        ("海尔BCD-215", "BCD-215WDPV", True),
        ("小米净化器3", "空气净化器Pro", True),
    ]
    
    print("🧪 相关性检查测试:")
    print("=" * 50)
    
    for original, matched, expected in test_cases:
        result = checker.is_relevant_match(original, matched)
        status = "✅" if result == expected else "❌"
        print(f"{status} {original} vs {matched} -> {result} (预期: {expected})")


if __name__ == "__main__":
    main()
