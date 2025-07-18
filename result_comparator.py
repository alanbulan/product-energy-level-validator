"""
结果对比和判断逻辑模块
对比搜索结果与Excel中的能耗等级，判断正确/错误/搜不到
"""

from typing import Dict, List, Optional, Any
import re
import difflib


class ResultComparator:
    def __init__(self):
        """初始化结果对比器"""
        # 能效等级标准化映射
        self.level_mapping = {
            # 数字形式
            '1': '一级',
            '2': '二级',
            '3': '三级',
            '4': '四级',
            '5': '五级',
            # 中文形式
            '一级': '一级',
            '二级': '二级',
            '三级': '三级',
            '四级': '四级',
            '五级': '五级',
            # 其他可能的表示形式
            '1级': '一级',
            '2级': '二级',
            '3级': '三级',
            '4级': '四级',
            '5级': '五级',
            'I': '一级',
            'II': '二级',
            'III': '三级',
            'IV': '四级',
            'V': '五级',
            # 特殊情况
            '未知': None,
            'N/A': None,
            'null': None,
            '': None
        }
    
    def normalize_energy_level(self, level: str) -> Optional[str]:
        """
        标准化能效等级
        
        Args:
            level: 原始能效等级
            
        Returns:
            Optional[str]: 标准化后的能效等级
        """
        if not level or not isinstance(level, str):
            return None
        
        # 清理字符串
        level = level.strip()
        
        # 移除可能的额外字符
        level = re.sub(r'[^\w\u4e00-\u9fff]', '', level)
        
        # 查找映射
        return self.level_mapping.get(level)
    
    def calculate_similarity_score(self, model1: str, model2: str) -> float:
        """
        计算两个型号的相似度分数

        Args:
            model1: 型号1
            model2: 型号2

        Returns:
            float: 相似度分数 (0-1)
        """
        if not model1 or not model2:
            return 0.0

        # 使用序列匹配器计算相似度
        similarity = difflib.SequenceMatcher(None, model1.lower(), model2.lower()).ratio()
        return similarity

    def extract_brand_from_model(self, model: str) -> str:
        """
        从型号中提取品牌信息 (智能版本)

        Args:
            model: 产品型号或生产商信息

        Returns:
            str: 品牌名称
        """
        if not model:
            return ""

        # 基于数据分析优化的品牌列表 (按重要性排序)
        # 数据显示：格力82%，奥克斯11%，美的3%，TCL1%
        priority_brands = [
            # 高优先级品牌 (数据中的主力)
            '格力', '奥克斯', '美的', 'TCL',
            # 中优先级品牌 (常见)
            '海尔', '志高', '海信', '长虹', '科龙', '容声',
            # 低优先级品牌 (补充)
            '春兰', '新科', '华凌', '小天鹅', '统帅', '卡萨帝', '美菱',
            '创维', '康佳', '夏普', '松下', '三菱', '大金', '日立', '东芝',
            # 国际品牌
            'LG', 'SAMSUNG', '三星', 'SONY', '索尼', 'PHILIPS', '飞利浦',
            'SIEMENS', '西门子', 'BOSCH', '博世', 'WHIRLPOOL', '惠而浦',
            # 专业空调品牌
            '约克', 'YORK', '开利', 'CARRIER', '特灵', 'TRANE', '麦克维尔',
            '顿汉布什', '克莱门特', '盾安', '申菱', '欧科', '天加'
        ]

        brands = priority_brands

        model_clean = model.strip()
        model_lower = model_clean.lower()

        # 1. 直接匹配品牌关键词
        for brand in brands:
            if brand in model_clean or brand.lower() in model_lower:
                return brand

        # 2. 从生产商字段中提取品牌（更准确）
        # 匹配常见的公司名称模式
        company_patterns = [
            r'([\u4e00-\u9fff]+)(?:电器|空调|制冷|科技|实业|集团|有限公司|股份|公司)',  # 中文公司名
            r'([A-Z][a-z]+)(?:\s+(?:Electric|Electronics|Technology|Corp|Ltd|Inc))',  # 英文公司名
            r'([\u4e00-\u9fff]{2,4})(?:[\u4e00-\u9fff]*电器)',  # 简化中文品牌
        ]

        import re
        for pattern in company_patterns:
            match = re.search(pattern, model_clean)
            if match:
                extracted_brand = match.group(1)
                # 过滤掉过于通用的词汇
                if extracted_brand not in ['有限', '股份', '电器', '空调', '制冷', '科技']:
                    return extracted_brand

        # 3. 提取型号前缀作为可能的品牌
        # 匹配型号开头的中文字符
        chinese_prefix = re.match(r'^([\u4e00-\u9fff]+)', model_clean)
        if chinese_prefix:
            prefix = chinese_prefix.group(1)
            # 如果前缀长度合理（2-4个字符），可能是品牌
            if 2 <= len(prefix) <= 4:
                return prefix

        # 4. 提取英文前缀作为可能的品牌
        english_prefix = re.match(r'^([A-Z][A-Za-z]+)', model_clean)
        if english_prefix:
            prefix = english_prefix.group(1)
            # 排除常见的型号前缀
            if prefix not in ['KFR', 'KF', 'RF', 'GR', 'BCD', 'XQG']:
                return prefix

        return ""

    def brands_similar(self, brand1: str, brand2: str) -> bool:
        """
        判断两个品牌是否相似

        Args:
            brand1: 品牌1
            brand2: 品牌2

        Returns:
            bool: 是否相似
        """
        if not brand1 or not brand2:
            return False

        # 品牌别名映射
        brand_aliases = {
            '格力': ['GREE', 'gree', '珠海格力', '格力电器'],
            '美的': ['MIDEA', 'midea', '美的集团', '美的电器'],
            '海尔': ['HAIER', 'haier', '海尔集团', '青岛海尔'],
            '奥克斯': ['AUX', 'aux', '奥克斯集团'],
            '志高': ['CHIGO', 'chigo', '志高空调'],
            'TCL': ['tcl', 'TCL集团', 'TCL电器'],
            '海信': ['HISENSE', 'hisense', '海信集团'],
            '长虹': ['CHANGHONG', 'changhong', '四川长虹'],
            '科龙': ['KELON', 'kelon', '海信科龙'],
            '容声': ['RONSHEN', 'ronshen'],
            '华凌': ['WAHIN', 'wahin'],
            '卡萨帝': ['CASARTE', 'casarte'],
            '统帅': ['LEADER', 'leader'],
            '小天鹅': ['LITTLESWAN', 'littleswan'],
            '三星': ['SAMSUNG', 'samsung'],
            '松下': ['PANASONIC', 'panasonic'],
            '三菱': ['MITSUBISHI', 'mitsubishi'],
            '大金': ['DAIKIN', 'daikin'],
            '西门子': ['SIEMENS', 'siemens'],
            '博世': ['BOSCH', 'bosch'],
            '惠而浦': ['WHIRLPOOL', 'whirlpool']
        }

        brand1_lower = brand1.lower()
        brand2_lower = brand2.lower()

        # 直接匹配
        if brand1_lower == brand2_lower:
            return True

        # 检查别名映射
        for main_brand, aliases in brand_aliases.items():
            main_brand_lower = main_brand.lower()
            aliases_lower = [alias.lower() for alias in aliases]

            # 如果两个品牌都属于同一个品牌系列
            if ((brand1_lower == main_brand_lower or brand1_lower in aliases_lower) and
                (brand2_lower == main_brand_lower or brand2_lower in aliases_lower)):
                return True

        # 包含关系检查
        if brand1_lower in brand2_lower or brand2_lower in brand1_lower:
            return True

        # 相似度检查（用于处理拼写变体）
        similarity = self.calculate_similarity_score(brand1, brand2)
        return similarity > 0.8  # 80%以上相似度认为是同一品牌

    def normalize_brand_name(self, brand: str) -> str:
        """
        标准化品牌名称

        Args:
            brand: 原始品牌名

        Returns:
            str: 标准化后的品牌名
        """
        if not brand:
            return ""

        # 品牌标准化映射
        brand_normalization = {
            'GREE': '格力',
            'gree': '格力',
            '珠海格力': '格力',
            '格力电器': '格力',
            'MIDEA': '美的',
            'midea': '美的',
            '美的集团': '美的',
            '美的电器': '美的',
            'HAIER': '海尔',
            'haier': '海尔',
            '海尔集团': '海尔',
            '青岛海尔': '海尔',
            'AUX': '奥克斯',
            'aux': '奥克斯',
            'CHIGO': '志高',
            'chigo': '志高',
            'HISENSE': '海信',
            'hisense': '海信',
            'SAMSUNG': '三星',
            'samsung': '三星',
            'PANASONIC': '松下',
            'panasonic': '松下'
        }

        return brand_normalization.get(brand, brand)

    def extract_power_spec(self, model: str) -> str:
        """
        从型号中提取功率规格

        Args:
            model: 产品型号

        Returns:
            str: 功率规格 (如 "35", "26")
        """
        # 匹配常见的功率规格模式
        import re
        patterns = [
            r'KFR?-(\d+)GW',  # KFR-35GW, KF-26GW
            r'(\d+)GW',       # 35GW
            r'KFR?-(\d+)',    # KFR-35
        ]

        for pattern in patterns:
            match = re.search(pattern, model, re.IGNORECASE)
            if match:
                return match.group(1)

        return ""

    def score_match(self, original_model: str, extracted_model: str, candidate: Dict[str, Any]) -> float:
        """
        为候选记录计算匹配分数

        Args:
            original_model: 原始型号
            extracted_model: 提取后的型号
            candidate: 候选记录

        Returns:
            float: 匹配分数 (0-100)
        """
        candidate_model = candidate.get('model', '')
        candidate_producer = candidate.get('producer', '')

        score = 0.0

        # 1. 精确匹配 (100分)
        if candidate_model == original_model:
            return 100.0
        if candidate_model == extracted_model:
            return 95.0

        # 2. 相似度匹配 (0-90分)
        similarity_original = self.calculate_similarity_score(original_model, candidate_model)
        similarity_extracted = self.calculate_similarity_score(extracted_model, candidate_model)
        max_similarity = max(similarity_original, similarity_extracted)
        score += max_similarity * 90

        # 3. 包含关系匹配 (额外加分)
        if candidate_model in original_model or original_model in candidate_model:
            score += 10
        if candidate_model in extracted_model or extracted_model in candidate_model:
            score += 8

        # 4. 品牌匹配 (基于数据分析优化权重)
        original_brand = self.extract_brand_from_model(original_model)
        candidate_brand_from_producer = self.extract_brand_from_model(candidate_producer)
        candidate_brand_from_model = self.extract_brand_from_model(candidate_model)

        # 优先使用生产商字段中的品牌，因为更准确
        candidate_brand = candidate_brand_from_producer or candidate_brand_from_model

        if original_brand and candidate_brand:
            # 格力品牌特殊处理 (数据中占82%)
            if original_brand == '格力' and self.brands_similar(original_brand, candidate_brand):
                score += 20  # 格力匹配加分更高
            # 其他高优先级品牌
            elif original_brand in ['奥克斯', '美的', 'TCL'] and self.brands_similar(original_brand, candidate_brand):
                score += 18
            # 精确匹配
            elif original_brand == candidate_brand:
                score += 15
            # 模糊匹配（考虑品牌的不同表示方式）
            elif self.brands_similar(original_brand, candidate_brand):
                score += 12

        # 如果没有提取到原始品牌，但候选记录有明确的品牌信息，小幅加分
        elif not original_brand and candidate_brand:
            score += 3

        # 5. KFR系列特殊匹配 (数据中占62%)
        if 'KFR' in original_model and 'KFR' in candidate_model:
            score += 8  # KFR系列匹配加分

        # 6. 功率规格匹配 (额外加分)
        original_power = self.extract_power_spec(original_model)
        candidate_power = self.extract_power_spec(candidate_model)
        if original_power and candidate_power and original_power == candidate_power:
            score += 12  # 提高功率匹配权重

        # 6. 信息完整度 (额外加分)
        if candidate.get('energy_level'):
            score += 2
        if candidate.get('producer'):
            score += 2
        if candidate.get('record_number'):
            score += 1

        return min(score, 100.0)  # 最高100分

    def find_best_match(self, search_result: Dict[str, Any], original_model: str) -> Optional[Dict[str, Any]]:
        """
        从搜索结果中找到最佳匹配 (智能版本)

        Args:
            search_result: 搜索结果
            original_model: 原始产品型号

        Returns:
            Optional[Dict]: 最佳匹配的记录
        """
        if not search_result['search_success'] or not search_result['energy_levels']:
            return None

        energy_levels = search_result['energy_levels']
        extracted_model = search_result.get('extracted_model', original_model)

        # 如果只有一个结果，直接返回
        if len(energy_levels) == 1:
            return energy_levels[0]

        # 计算每个候选记录的匹配分数
        scored_candidates = []
        for candidate in energy_levels:
            score = self.score_match(original_model, extracted_model, candidate)
            scored_candidates.append((score, candidate))

        # 按分数排序，选择最高分的
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        best_score, best_match = scored_candidates[0]

        # 如果最高分太低（小于30），可能匹配不可靠
        if best_score < 30:
            print(f"⚠️ 最佳匹配分数较低 ({best_score:.1f})，匹配可能不准确")

        print(f"🎯 最佳匹配: {best_match['model']} (分数: {best_score:.1f})")

        # 显示前3个候选的分数（用于调试）
        print("📊 候选匹配分数:")
        for i, (score, candidate) in enumerate(scored_candidates[:3], 1):
            print(f"  {i}. {candidate['model']} - {score:.1f}分")

        return best_match
    
    def compare_energy_levels(self, excel_level: str, search_level: str) -> str:
        """
        对比能效等级

        Args:
            excel_level: Excel中的能效等级
            search_level: 搜索到的能效等级

        Returns:
            str: 对比结果（'正确'、'错误'、'搜不到'、'Excel缺失'）
        """
        # 标准化两个等级
        normalized_excel = self.normalize_energy_level(excel_level)
        normalized_search = self.normalize_energy_level(search_level)

        # 如果搜索结果为空或无法标准化，返回"搜不到"
        if not normalized_search:
            return '搜不到'

        # 如果Excel中的等级为空但网站有数据，返回"Excel缺失"
        if not normalized_excel:
            return 'Excel缺失'

        # 对比标准化后的等级
        if normalized_excel == normalized_search:
            return '正确'
        else:
            return '错误'
    
    def validate_single_product(self, original_model: str, excel_energy_level: str, 
                              search_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单个产品
        
        Args:
            original_model: 原始产品型号
            excel_energy_level: Excel中的能效等级
            search_result: 搜索结果
            
        Returns:
            Dict: 验证结果
        """
        result = {
            'original_model': original_model,
            'excel_energy_level': excel_energy_level,
            'search_success': search_result['search_success'],
            'found_records': len(search_result.get('energy_levels', [])),
            'matched_record': None,
            'search_energy_level': None,
            'validation_result': '搜不到',
            'details': ''
        }
        
        # 如果搜索失败
        if not search_result['search_success']:
            result['details'] = f"搜索失败: {search_result.get('error_message', '未知错误')}"
            return result
        
        # 如果没有找到记录
        if not search_result.get('energy_levels'):
            result['details'] = "未找到匹配的产品记录"
            return result
        
        # 找到最佳匹配
        best_match = self.find_best_match(search_result, original_model)
        if best_match:
            result['matched_record'] = best_match
            result['search_energy_level'] = best_match['energy_level']
            
            # 对比能效等级
            validation_result = self.compare_energy_levels(excel_energy_level, best_match['energy_level'])
            result['validation_result'] = validation_result
            
            # 添加详细信息
            if validation_result == '正确':
                result['details'] = f"匹配成功: {best_match['model']} - {best_match['energy_level']}"
            elif validation_result == '错误':
                result['details'] = f"等级不匹配: Excel({excel_energy_level}) vs 搜索({best_match['energy_level']}) - {best_match['model']}"
            elif validation_result == 'Excel缺失':
                result['details'] = f"Excel缺失能效等级，网站显示: {best_match['energy_level']} - {best_match['model']}"
            else:
                result['details'] = f"无法确定等级: {best_match['model']}"
        else:
            result['details'] = f"在 {len(search_result['energy_levels'])} 条记录中未找到匹配项"
        
        return result
    
    def batch_validate(self, products_data: List[tuple], search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量验证产品
        
        Args:
            products_data: 产品数据列表 [(row_index, model, energy_level), ...]
            search_results: 搜索结果列表
            
        Returns:
            List[Dict]: 验证结果列表
        """
        if len(products_data) != len(search_results):
            raise ValueError("产品数据和搜索结果数量不匹配")
        
        validation_results = []
        
        for (row_index, model, excel_level), search_result in zip(products_data, search_results):
            validation_result = self.validate_single_product(model, excel_level, search_result)
            validation_result['row_index'] = row_index
            validation_results.append(validation_result)
        
        return validation_results
    
    def get_validation_statistics(self, validation_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        获取验证统计信息
        
        Args:
            validation_results: 验证结果列表
            
        Returns:
            Dict: 统计信息
        """
        stats = {
            '总数': len(validation_results),
            '正确': 0,
            '错误': 0,
            '搜不到': 0,
            '搜索成功': 0,
            '搜索失败': 0,
            '找到记录': 0
        }
        
        for result in validation_results:
            validation_result = result['validation_result']
            stats[validation_result] += 1
            
            if result['search_success']:
                stats['搜索成功'] += 1
                if result['found_records'] > 0:
                    stats['找到记录'] += 1
            else:
                stats['搜索失败'] += 1
        
        return stats


# 测试代码
if __name__ == "__main__":
    comparator = ResultComparator()
    
    # 测试能效等级标准化
    test_levels = ['1', '一级', '1级', 'I', '2', '二级', 'invalid']
    print("能效等级标准化测试：")
    for level in test_levels:
        normalized = comparator.normalize_energy_level(level)
        print(f"{level} -> {normalized}")
    
    print("\n能效等级对比测试：")
    test_cases = [
        ('一级', '1'),
        ('二级', '2'),
        ('一级', '二级'),
        ('1级', 'I'),
        ('三级', None)
    ]
    
    for excel_level, search_level in test_cases:
        result = comparator.compare_energy_levels(excel_level, search_level)
        print(f"Excel: {excel_level}, 搜索: {search_level} -> {result}")
