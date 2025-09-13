<!--
文档说明：
- 内容：推荐系统模块API接口实现细节，记录推荐算法的具体实现和机器学习模型
- 使用方法：开发人员实现推荐功能时的参考，算法实现的详细记录
- 更新方法：实现代码变更时同步更新，记录实际的算法实现
- 引用关系：基于api-spec.md规范，记录实际推荐算法实现
- 更新频率：算法实现优化时
-->

# 推荐系统模块API实现

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 实现架构

### 文件结构
```
app/recommendation/
├── __init__.py
├── engines/
│   ├── __init__.py
│   ├── collaborative.py     # 协同过滤算法
│   ├── content_based.py     # 基于内容的推荐
│   ├── trending.py          # 热门推荐算法
│   └── real_time.py         # 实时推荐算法
├── models/
│   ├── __init__.py
│   ├── user_behavior.py     # 用户行为模型
│   └── product_similarity.py # 商品相似度模型
├── services/
│   ├── __init__.py
│   ├── recommendation_service.py # 推荐服务主逻辑
│   └── feedback_service.py      # 反馈处理服务
└── utils/
    ├── __init__.py
    ├── feature_extraction.py   # 特征提取工具
    └── cache_manager.py        # 缓存管理
```

## 协同过滤算法实现

### 用户-商品矩阵构建
```python
# app/recommendation/engines/collaborative.py
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.models import User, Product, Order, OrderItem

class CollaborativeFiltering:
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        
    def build_user_item_matrix(self):
        """构建用户-商品评分矩阵"""
        # 从订单数据构建评分矩阵
        query = """
        SELECT user_id, product_id, 
               SUM(quantity) as purchase_count,
               COUNT(*) as order_frequency
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'completed'
        GROUP BY user_id, product_id
        """
        
        df = pd.read_sql(query, get_db_connection())
        
        # 计算隐式评分 (购买次数 + 订单频率)
        df['rating'] = df['purchase_count'] * 0.7 + df['order_frequency'] * 0.3
        
        # 构建矩阵
        self.user_item_matrix = df.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='rating',
            fill_value=0
        )
        
        return self.user_item_matrix
    
    def calculate_user_similarity(self):
        """计算用户相似度矩阵"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
            
        self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
        return self.user_similarity_matrix
    
    def get_recommendations(self, user_id: int, num_recommendations: int = 10):
        """为用户生成推荐"""
        if user_id not in self.user_item_matrix.index:
            return self._get_default_recommendations(num_recommendations)
        
        user_index = self.user_item_matrix.index.get_loc(user_id)
        user_similarities = self.user_similarity_matrix[user_index]
        
        # 找到最相似的用户
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # 前10个相似用户
        
        # 获取相似用户喜欢但当前用户未购买的商品
        user_items = self.user_item_matrix.iloc[user_index]
        recommendations = {}
        
        for similar_user_idx in similar_users:
            similarity_score = user_similarities[similar_user_idx]
            similar_user_items = self.user_item_matrix.iloc[similar_user_idx]
            
            for product_id, rating in similar_user_items.items():
                if rating > 0 and user_items[product_id] == 0:
                    if product_id not in recommendations:
                        recommendations[product_id] = 0
                    recommendations[product_id] += rating * similarity_score
        
        # 排序并返回前N个推荐
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {
                "product_id": product_id,
                "score": score,
                "algorithm": "collaborative_filtering"
            }
            for product_id, score in sorted_recommendations[:num_recommendations]
        ]
```

## 基于内容的推荐实现

### 商品特征提取
```python
# app/recommendation/engines/content_based.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba

class ContentBasedRecommendation:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.product_features = None
        self.product_similarity_matrix = None
    
    def extract_product_features(self):
        """提取商品特征"""
        products = Product.query.all()
        
        # 构建商品文本特征
        product_texts = []
        product_ids = []
        
        for product in products:
            # 分词处理商品名称和描述
            text = f"{product.name} {product.description or ''}"
            segmented_text = " ".join(jieba.cut(text))
            product_texts.append(segmented_text)
            product_ids.append(product.id)
        
        # TF-IDF特征提取
        self.product_features = self.tfidf_vectorizer.fit_transform(product_texts)
        self.product_ids = product_ids
        
        return self.product_features
    
    def calculate_product_similarity(self):
        """计算商品相似度"""
        if self.product_features is None:
            self.extract_product_features()
            
        self.product_similarity_matrix = cosine_similarity(self.product_features)
        return self.product_similarity_matrix
    
    def get_similar_products(self, product_id: int, num_recommendations: int = 10):
        """获取相似商品推荐"""
        try:
            product_index = self.product_ids.index(product_id)
        except ValueError:
            return []
        
        similarity_scores = self.product_similarity_matrix[product_index]
        similar_indices = np.argsort(similarity_scores)[::-1][1:num_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            recommendations.append({
                "product_id": self.product_ids[idx],
                "score": similarity_scores[idx],
                "algorithm": "content_based"
            })
        
        return recommendations
    
    def get_user_content_recommendations(self, user_id: int, num_recommendations: int = 10):
        """基于用户历史购买的内容推荐"""
        # 获取用户购买历史
        user_products = db.query(Product).join(OrderItem).join(Order).filter(
            Order.user_id == user_id,
            Order.status == 'completed'
        ).all()
        
        if not user_products:
            return []
        
        # 获取用户偏好的商品特征
        user_product_ids = [p.id for p in user_products]
        recommendations = {}
        
        for product_id in user_product_ids:
            similar_products = self.get_similar_products(product_id, 20)
            for rec in similar_products:
                rec_product_id = rec["product_id"]
                if rec_product_id not in user_product_ids:
                    if rec_product_id not in recommendations:
                        recommendations[rec_product_id] = 0
                    recommendations[rec_product_id] += rec["score"]
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "product_id": product_id,
                "score": score,
                "algorithm": "content_based"
            }
            for product_id, score in sorted_recommendations[:num_recommendations]
        ]
```

## 实时推荐实现

### 基于会话的推荐
```python
# app/recommendation/engines/real_time.py
from collections import defaultdict
import redis
import json

class RealTimeRecommendation:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
        
    def track_user_behavior(self, user_id: int, action: str, product_id: int):
        """追踪用户行为"""
        behavior_key = f"user_behavior:{user_id}"
        
        behavior_data = {
            "action": action,
            "product_id": product_id,
            "timestamp": time.time()
        }
        
        # 存储到Redis列表，保留最近100个行为
        self.redis_client.lpush(behavior_key, json.dumps(behavior_data))
        self.redis_client.ltrim(behavior_key, 0, 99)
        self.redis_client.expire(behavior_key, 3600)  # 1小时过期
    
    def get_session_recommendations(self, user_id: int, num_recommendations: int = 10):
        """基于用户会话的实时推荐"""
        behavior_key = f"user_behavior:{user_id}"
        behaviors = self.redis_client.lrange(behavior_key, 0, -1)
        
        if not behaviors:
            return []
        
        # 分析行为模式
        product_scores = defaultdict(float)
        action_weights = {
            "view": 1.0,
            "click": 2.0,
            "add_to_cart": 5.0,
            "purchase": 10.0
        }
        
        for behavior_json in behaviors:
            behavior = json.loads(behavior_json)
            action = behavior["action"]
            product_id = behavior["product_id"]
            timestamp = behavior["timestamp"]
            
            # 时间衰减因子
            time_decay = np.exp(-(time.time() - timestamp) / 1800)  # 30分钟半衰期
            
            # 计算分数
            score = action_weights.get(action, 1.0) * time_decay
            product_scores[product_id] += score
        
        # 基于浏览的商品获取相似推荐
        content_recommender = ContentBasedRecommendation()
        recommendations = {}
        
        for product_id, score in product_scores.items():
            similar_products = content_recommender.get_similar_products(product_id, 10)
            for rec in similar_products:
                rec_product_id = rec["product_id"]
                if rec_product_id not in product_scores:  # 避免推荐已浏览的商品
                    if rec_product_id not in recommendations:
                        recommendations[rec_product_id] = 0
                    recommendations[rec_product_id] += rec["score"] * score
        
        # 排序返回
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "product_id": product_id,
                "score": score,
                "algorithm": "real_time"
            }
            for product_id, score in sorted_recommendations[:num_recommendations]
        ]
```

## 推荐服务主逻辑

### 混合推荐算法
```python
# app/recommendation/services/recommendation_service.py
class RecommendationService:
    def __init__(self):
        self.collaborative_engine = CollaborativeFiltering()
        self.content_engine = ContentBasedRecommendation()
        self.real_time_engine = RealTimeRecommendation()
        self.trending_engine = TrendingRecommendation()
        
    def get_user_recommendations(self, user_id: int, num_recommendations: int = 10):
        """获取用户混合推荐"""
        all_recommendations = []
        
        # 协同过滤推荐 (权重40%)
        collaborative_recs = self.collaborative_engine.get_recommendations(user_id, 20)
        for rec in collaborative_recs:
            rec["score"] *= 0.4
            all_recommendations.append(rec)
        
        # 基于内容推荐 (权重30%)
        content_recs = self.content_engine.get_user_content_recommendations(user_id, 20)
        for rec in content_recs:
            rec["score"] *= 0.3
            all_recommendations.append(rec)
        
        # 实时推荐 (权重20%)
        real_time_recs = self.real_time_engine.get_session_recommendations(user_id, 20)
        for rec in real_time_recs:
            rec["score"] *= 0.2
            all_recommendations.append(rec)
        
        # 热门推荐 (权重10%)
        trending_recs = self.trending_engine.get_trending_products(20)
        for rec in trending_recs:
            rec["score"] *= 0.1
            all_recommendations.append(rec)
        
        # 合并同一商品的分数
        product_scores = defaultdict(float)
        for rec in all_recommendations:
            product_scores[rec["product_id"]] += rec["score"]
        
        # 排序并获取商品详情
        sorted_products = sorted(
            product_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_recommendations]
        
        recommendations = []
        for product_id, score in sorted_products:
            product = Product.query.get(product_id)
            if product:
                recommendations.append({
                    "product_id": product_id,
                    "product_name": product.name,
                    "price": float(product.price),
                    "image_url": product.image_url,
                    "score": score,
                    "reason": self._get_recommendation_reason(user_id, product_id)
                })
        
        return recommendations
    
    def _get_recommendation_reason(self, user_id: int, product_id: int):
        """生成推荐理由"""
        # 简化的推荐理由生成逻辑
        user_history = self._get_user_purchase_history(user_id)
        if user_history:
            return "基于您的购买历史"
        else:
            return "热门商品推荐"
```

## 缓存管理实现

### Redis缓存策略
```python
# app/recommendation/utils/cache_manager.py
class RecommendationCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
        self.cache_ttl = 3600  # 1小时缓存
    
    def get_user_recommendations_cache(self, user_id: int):
        """获取用户推荐缓存"""
        cache_key = f"user_recommendations:{user_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def set_user_recommendations_cache(self, user_id: int, recommendations: list):
        """设置用户推荐缓存"""
        cache_key = f"user_recommendations:{user_id}"
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(recommendations)
        )
    
    def invalidate_user_cache(self, user_id: int):
        """清除用户推荐缓存"""
        cache_key = f"user_recommendations:{user_id}"
        self.redis_client.delete(cache_key)
```