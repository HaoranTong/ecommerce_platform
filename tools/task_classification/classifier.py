#!/usr/bin/env python3
"""
AI任务分类器 - 混合智能分类算法实现
用于自动识别用户任务类型并匹配相应的检查点

作者: AI工作流优化系统  
版本: 1.0.0
"""

import re
import yaml
import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TaskClassification:
    """任务分类结果数据类"""
    primary_type: str           # 主要任务类型
    secondary_types: List[str]  # 辅助任务类型
    confidence: float          # 主类型置信度
    keywords: Dict[str, List[str]]  # 提取的关键词
    checkpoints: List[str]     # 匹配的检查点
    reasoning: str             # 分类理由

class TaskClassifier:
    """
    AI任务智能分类器
    
    核心功能:
    1. 多维度关键词提取和权重评分
    2. 基于规则的检查点动态匹配
    3. 置信度控制和异常处理
    """
    
    def __init__(self, config_dir: str = "tools/task_classification/config"):
        """初始化分类器"""
        self.config_dir = Path(config_dir)
        self._load_configurations()
    
    def _load_configurations(self):
        """加载所有配置文件"""
        try:
            # 加载任务类型配置
            with open(self.config_dir / "task_types.yaml", 'r', encoding='utf-8') as f:
                self.task_types = yaml.safe_load(f)
            
            # 加载关键词库
            with open(self.config_dir / "keywords.yaml", 'r', encoding='utf-8') as f:
                self.keywords_db = yaml.safe_load(f)
            
            # 加载检查点映射规则
            with open(self.config_dir / "checkpoint_mapping.yaml", 'r', encoding='utf-8') as f:
                self.checkpoint_rules = yaml.safe_load(f)
                
            # 加载权重配置
            with open(self.config_dir / "weights.yaml", 'r', encoding='utf-8') as f:
                self.weights = yaml.safe_load(f)
                
        except FileNotFoundError as e:
            raise RuntimeError(f"配置文件缺失: {e}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"配置文件格式错误: {e}")
    
    def extract_keywords(self, user_input: str) -> Dict[str, List[str]]:
        """
        多维度关键词提取
        
        提取维度:
        1. action_verbs - 动作动词 (实现, 开发, 测试等)
        2. tech_terms - 技术词汇 (API, 数据库, 模型等)  
        3. tech_stack - 技术栈 (FastAPI, SQLAlchemy等)
        4. context_clues - 上下文线索 (新的, 修改, 整体等)
        5. domain_terms - 业务领域词汇 (用户认证, 订单管理等)
        """
        text = user_input.lower()
        extracted = {
            'action_verbs': [],
            'tech_terms': [],
            'tech_stack': [],
            'context_clues': [],
            'domain_terms': []
        }
        
        # 遍历所有关键词类别
        for category, keywords in self.keywords_db.items():
            if category == 'regex_patterns':
                # 处理正则表达式模式
                for pattern in keywords:
                    if pattern.startswith('/') and pattern.endswith('/'):
                        regex_pattern = pattern[1:-1]
                        try:
                            if re.search(regex_pattern, text):
                                # 将正则匹配的结果添加到tech_terms中
                                extracted['tech_terms'].append(pattern.strip('/'))
                        except re.error:
                            continue
                continue
            
            # 确保提取字典中有该类别
            if category not in extracted:
                extracted[category] = []
            
            for keyword in keywords:
                # 支持正则表达式匹配
                if keyword.startswith('/') and keyword.endswith('/'):
                    pattern = keyword[1:-1]
                    try:
                        if re.search(pattern, text):
                            extracted[category].append(keyword.strip('/'))
                    except re.error:
                        continue
                else:
                    if keyword in text:
                        extracted[category].append(keyword)
        
        return extracted
    
    def calculate_type_score(self, task_type: str, keywords: Dict[str, List[str]]) -> Tuple[float, str]:
        """
        计算特定任务类型的匹配分数
        
        算法:
        1. 按类别计算匹配关键词数量
        2. 应用权重计算加权分数
        3. 标准化到0-100分区间
        4. 生成详细的评分理由
        """
        if task_type not in self.task_types:
            return 0.0, f"未知任务类型: {task_type}"
        
        type_config = self.task_types[task_type]
        total_score = 0.0
        max_possible_score = 0.0
        scoring_details = []
        
        # 按维度计算分数
        for dimension, config in type_config.items():
            weight = config.get('weight', 0)
            type_keywords = set(config.get('keywords', []))
            matched_keywords = set(keywords.get(dimension, []))
            
            # 计算匹配度
            if type_keywords:
                match_ratio = len(matched_keywords & type_keywords) / len(type_keywords)
                dimension_score = match_ratio * weight
                total_score += dimension_score
                
                scoring_details.append(
                    f"{dimension}: {len(matched_keywords & type_keywords)}/{len(type_keywords)} "
                    f"匹配 (权重{weight}) = {dimension_score:.1f}分"
                )
            
            max_possible_score += weight
        
        # 标准化分数
        if max_possible_score > 0:
            normalized_score = (total_score / max_possible_score) * 100
        else:
            normalized_score = 0.0
        
        reasoning = f"{task_type}类型评分详情:\n" + "\n".join(scoring_details) + \
                   f"\n总分: {total_score:.1f}/{max_possible_score} = {normalized_score:.1f}%"
        
        return normalized_score, reasoning
    
    def match_checkpoints(self, primary_type: str, secondary_types: List[str], 
                         keywords: Dict[str, List[str]]) -> List[str]:
        """
        基于任务类型动态匹配检查点
        
        匹配策略:
        1. 加载主类型的必选检查点
        2. 基于关键词条件匹配可选检查点
        3. 为辅助类型添加相关检查点
        4. 去重并按优先级排序
        """
        checkpoints = set()
        
        # 处理主类型检查点
        if primary_type in self.checkpoint_rules:
            rules = self.checkpoint_rules[primary_type]
            
            # 添加必选检查点
            required = rules.get('required_checkpoints', [])
            checkpoints.update(required)
            
            # 处理条件检查点
            conditional_rules = rules.get('conditional_rules', [])
            all_keywords = []
            for keyword_list in keywords.values():
                all_keywords.extend(keyword_list)
            
            for rule in conditional_rules:
                condition = rule['condition']
                if self._evaluate_condition(condition, all_keywords):
                    checkpoints.update(rule['add_checkpoints'])
        
        # 处理辅助类型检查点
        for secondary_type in secondary_types:
            if secondary_type in self.checkpoint_rules:
                rules = self.checkpoint_rules[secondary_type]
                # 只添加高相关度的检查点
                high_relevance = rules.get('high_relevance_checkpoints', [])
                checkpoints.update(high_relevance)
        
        return sorted(list(checkpoints))
    
    def _evaluate_condition(self, condition: str, keywords: List[str]) -> bool:
        """评估条件表达式是否满足"""
        # 支持简单的关键词匹配条件
        # 例: "API" in keywords, "数据库|模型" in keywords
        
        if " in keywords" in condition:
            keyword_part = condition.split(" in keywords")[0].strip().strip('"')
            
            # 处理OR条件 (|分隔)
            if '|' in keyword_part:
                or_keywords = [k.strip() for k in keyword_part.split('|')]
                return any(keyword in keywords for keyword in or_keywords)
            else:
                return keyword_part in keywords
        
        # 可以扩展支持更复杂的条件表达式
        return False
    
    def classify(self, user_input: str) -> TaskClassification:
        """
        执行完整的任务分类流程
        
        流程:
        1. 关键词提取
        2. 各类型评分计算  
        3. 分类决策
        4. 检查点匹配
        5. 结果封装
        """
        # 步骤1: 关键词提取
        keywords = self.extract_keywords(user_input)
        
        # 步骤2: 类型评分
        type_scores = {}
        all_reasoning = []
        
        for task_type in self.task_types.keys():
            score, reasoning = self.calculate_type_score(task_type, keywords)
            type_scores[task_type] = score
            all_reasoning.append(reasoning)
        
        # 步骤3: 分类决策
        # 主类型: 最高分
        primary_type = max(type_scores, key=type_scores.get)
        primary_confidence = type_scores[primary_type]
        
        # 辅助类型: 分数 > 60 且非主类型
        secondary_types = [
            task_type for task_type, score in type_scores.items()
            if score > 60 and task_type != primary_type
        ]
        
        # 步骤4: 检查点匹配
        checkpoints = self.match_checkpoints(primary_type, secondary_types, keywords)
        
        # 步骤5: 生成完整推理过程
        full_reasoning = f"""
## 🧠 任务分类分析过程

### 1. 关键词提取结果
{self._format_keywords(keywords)}

### 2. 各类型评分详情
{chr(10).join(all_reasoning)}

### 3. 分类决策结果
- 主要任务类型: {primary_type} (置信度: {primary_confidence:.1f}%)
- 辅助任务类型: {', '.join(secondary_types) if secondary_types else '无'}

### 4. 检查点匹配结果
匹配到 {len(checkpoints)} 个相关检查点: {', '.join(checkpoints)}
"""
        
        return TaskClassification(
            primary_type=primary_type,
            secondary_types=secondary_types,
            confidence=primary_confidence,
            keywords=keywords,
            checkpoints=checkpoints,
            reasoning=full_reasoning
        )
    
    def _format_keywords(self, keywords: Dict[str, List[str]]) -> str:
        """格式化关键词输出"""
        formatted = []
        for category, keyword_list in keywords.items():
            if keyword_list:
                formatted.append(f"- {category}: {', '.join(keyword_list)}")
        return '\n'.join(formatted) if formatted else "- 未检测到明显的关键词"

# 流程执行验证器
class WorkflowValidator:
    """
    AI工作流程执行验证器
    确保AI严格按照8步流程执行
    """
    
    def __init__(self):
        self.required_steps = [
            "读取工作状态",
            "AI-START检查点验证", 
            "智能任务分类",
            "检查点匹配",
            "生成TODO清单",
            "用户确认",
            "执行工作",
            "状态更新"
        ]
        self.current_step = 0
        self.step_outputs = {}
    
    def validate_step_output(self, step_name: str, output: str) -> Tuple[bool, str]:
        """验证步骤输出格式是否正确"""
        
        if step_name == "智能任务分类":
            return self._validate_classification_output(output)
        elif step_name == "检查点匹配":
            return self._validate_checkpoint_output(output)
        # 可以继续添加其他步骤的验证
        
        return True, "验证通过"
    
    def _validate_classification_output(self, output: str) -> Tuple[bool, str]:
        """验证任务分类输出格式"""
        required_sections = [
            "## 📋 任务分类分析",
            "### 用户原始指令",
            "### 关键词提取结果",
            "### 分类评分结果", 
            "### 最终分类结果"
        ]
        
        for section in required_sections:
            if section not in output:
                return False, f"缺少必需部分: {section}"
        
        return True, "分类输出格式正确"
    
    def _validate_checkpoint_output(self, output: str) -> Tuple[bool, str]:
        """验证检查点匹配输出格式"""
        if "## 📋 基于任务类型的检查点匹配" not in output:
            return False, "缺少检查点匹配标题"
        
        if "### 最终匹配检查点清单" not in output:
            return False, "缺少最终检查点清单"
        
        return True, "检查点匹配输出格式正确"

# 使用示例
if __name__ == "__main__":
    # 初始化分类器
    classifier = TaskClassifier()
    
    # 测试用例
    test_input = "实现用户认证模块的API接口，包括登录、注册和权限验证功能"
    
    # 执行分类
    result = classifier.classify(test_input)
    
    # 输出结果
    print("=" * 60)
    print("AI任务分类器测试结果")
    print("=" * 60)
    print(result.reasoning)
    print(f"\n🎯 **最终分类结果**:")
    print(f"主要类型: {result.primary_type}")
    print(f"辅助类型: {', '.join(result.secondary_types)}")
    print(f"置信度: {result.confidence:.1f}%")
    print(f"匹配检查点: {', '.join(result.checkpoints)}")