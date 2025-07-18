"""
Excel数据处理模块
负责读取和写入Excel文件中的产品型号和能耗等级数据
"""

import pandas as pd
import os
from typing import List, Tuple, Optional


class ExcelHandler:
    def __init__(self, file_path: str):
        """
        初始化Excel处理器
        
        Args:
            file_path: Excel文件路径
        """
        self.file_path = file_path
        self.df = None
        
    def load_data(self) -> bool:
        """
        加载Excel数据
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.file_path):
                print(f"错误：文件 {self.file_path} 不存在")
                return False
                
            self.df = pd.read_excel(self.file_path)
            
            # 检查必要的列是否存在
            required_columns = ['产品型号', '能耗级别\n（一级/二级）']
            for col in required_columns:
                if col not in self.df.columns:
                    print(f"错误：缺少必要的列 '{col}'")
                    return False
            
            # 如果没有结果列，创建一个
            if '验证结果' not in self.df.columns:
                self.df['验证结果'] = ''
                
            print(f"成功加载Excel文件，共 {len(self.df)} 行数据")
            return True
            
        except Exception as e:
            print(f"加载Excel文件时出错：{str(e)}")
            return False
    
    def get_product_data(self) -> List[Tuple[int, str, str]]:
        """
        获取产品数据
        
        Returns:
            List[Tuple[int, str, str]]: (行号, 产品型号, 能耗等级) 的列表
        """
        if self.df is None:
            return []
            
        data = []
        for index, row in self.df.iterrows():
            model = str(row['产品型号']).strip() if pd.notna(row['产品型号']) else ''
            energy_level = str(row['能耗级别\n（一级/二级）']).strip() if pd.notna(row['能耗级别\n（一级/二级）']) else ''
            
            if model:  # 只处理有型号的行
                data.append((index, model, energy_level))
                
        return data
    
    def update_result(self, row_index: int, result: str) -> bool:
        """
        更新验证结果
        
        Args:
            row_index: 行索引
            result: 验证结果
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if self.df is None:
                return False
                
            self.df.at[row_index, '验证结果'] = result
            return True
            
        except Exception as e:
            print(f"更新结果时出错：{str(e)}")
            return False
    
    def save_data(self, output_path: Optional[str] = None) -> bool:
        """
        保存数据到Excel文件
        
        Args:
            output_path: 输出文件路径，如果为None则覆盖原文件
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if self.df is None:
                return False
                
            save_path = output_path if output_path else self.file_path
            self.df.to_excel(save_path, index=False)
            print(f"数据已保存到：{save_path}")
            return True
            
        except Exception as e:
            print(f"保存Excel文件时出错：{str(e)}")
            return False
    
    def get_statistics(self) -> dict:
        """
        获取验证结果统计
        
        Returns:
            dict: 统计结果
        """
        if self.df is None or '验证结果' not in self.df.columns:
            return {}
            
        stats = {
            '总数': len(self.df),
            '正确': len(self.df[self.df['验证结果'] == '正确']),
            '错误': len(self.df[self.df['验证结果'] == '错误']),
            '搜不到': len(self.df[self.df['验证结果'] == '搜不到']),
            '未处理': len(self.df[self.df['验证结果'] == ''])
        }
        
        return stats


# 测试代码
if __name__ == "__main__":
    handler = ExcelHandler("新建 Microsoft Excel 工作表.xlsx")
    
    if handler.load_data():
        data = handler.get_product_data()
        print(f"获取到 {len(data)} 条产品数据")
        
        # 显示前5条数据
        for i, (index, model, energy_level) in enumerate(data[:5]):
            print(f"{i+1}. 行{index+1}: {model} -> {energy_level}")
