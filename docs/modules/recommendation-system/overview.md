# 推荐系统模块 (Recommendation System Module)

## 模块概述

推荐系统模块基于机器学习算法和用户行为分析，提供个性化商品推荐、相关商品推荐、热门商品推荐和智能搜索建议。支持实时推荐和离线计算相结合的架构。

### 主要功能

1. **个性化推荐**
   - 基于协同过滤的商品推荐
   - 基于内容的商品推荐
   - 混合推荐算法
   - 冷启动问题解决

2. **实时推荐**
   - 浏览历史推荐
   - 购物车关联推荐
   - 实时热门推荐
   - 地理位置推荐

3. **智能搜索**
   - 搜索建议自动补全
   - 搜索结果个性化排序
   - 同义词扩展
   - 搜索意图识别

4. **推荐优化**
   - A/B测试框架
   - 推荐效果评估
   - 算法参数调优
   - 多样性控制

## 技术架构

### 核心组件

```
recommendation/
├── controllers/
│   ├── recommendation_controller.py  # 推荐控制器
│   ├── search_controller.py          # 搜索控制器
│   ├── analytics_controller.py       # 分析控制器
│   └── experiment_controller.py      # 实验控制器
├── services/
│   ├── recommendation_service.py     # 推荐业务逻辑
│   ├── ranking_service.py            # 排序服务
│   ├── feature_service.py            # 特征服务
│   ├── model_service.py              # 模型服务
│   └── experiment_service.py         # 实验服务
├── algorithms/
│   ├── collaborative_filtering.py   # 协同过滤
│   ├── content_based.py              # 基于内容
│   ├── deep_learning.py              # 深度学习
│   ├── hybrid_recommender.py         # 混合推荐
│   └── ranking_algorithm.py          # 排序算法
├── models/
│   ├── user_profile.py               # 用户画像模型
│   ├── item_profile.py               # 商品画像模型
│   ├── interaction.py                # 交互模型
│   ├── recommendation.py             # 推荐模型
│   └── experiment.py                 # 实验模型
├── events/
│   ├── user_behavior_events.py       # 用户行为事件
│   └── recommendation_events.py      # 推荐事件
└── utils/
    ├── feature_engineering.py        # 特征工程
    ├── model_utils.py                # 模型工具
    ├── evaluation_utils.py           # 评估工具
    └── cache_utils.py                # 缓存工具
```

### 数据库设计

```sql
-- 用户画像表
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL,
    demographics JSONB, -- 人口统计学特征
    preferences JSONB, -- 偏好特征
    behavior_features JSONB, -- 行为特征
    embedding_vector FLOAT8[], -- 用户向量表示
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 商品画像表
CREATE TABLE item_profiles (
    id UUID PRIMARY KEY,
    product_id UUID UNIQUE NOT NULL,
    category_features JSONB, -- 分类特征
    content_features JSONB, -- 内容特征
    statistical_features JSONB, -- 统计特征
    embedding_vector FLOAT8[], -- 商品向量表示
    popularity_score FLOAT8 DEFAULT 0,
    quality_score FLOAT8 DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户行为记录表
CREATE TABLE user_interactions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    item_id UUID NOT NULL,
    interaction_type VARCHAR(20) NOT NULL, -- 'view', 'click', 'cart', 'purchase', 'favorite', 'share'
    interaction_value FLOAT8 DEFAULT 1.0, -- 交互强度
    context JSONB, -- 上下文信息（设备、时间、页面等）
    session_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 推荐结果缓存表
CREATE TABLE recommendation_cache (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    scenario VARCHAR(50) NOT NULL, -- 'homepage', 'product_detail', 'cart', 'search'
    algorithm VARCHAR(50) NOT NULL,
    recommendations JSONB NOT NULL, -- 推荐商品列表
    metadata JSONB, -- 推荐元数据（分数、原因等）
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, scenario, algorithm)
);

-- 推荐模型表
CREATE TABLE recommendation_models (
    id UUID PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'collaborative_filtering', 'content_based', 'deep_learning'
    algorithm_config JSONB NOT NULL,
    model_path VARCHAR(500), -- 模型文件路径
    performance_metrics JSONB, -- 性能指标
    training_data_info JSONB, -- 训练数据信息
    status VARCHAR(20) DEFAULT 'training', -- 'training', 'ready', 'deployed', 'deprecated'
    version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deployed_at TIMESTAMP WITH TIME ZONE
);

-- A/B测试实验表
CREATE TABLE recommendation_experiments (
    id UUID PRIMARY KEY,
    experiment_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'running', 'paused', 'completed'
    traffic_allocation FLOAT8 NOT NULL, -- 流量分配比例
    control_algorithm VARCHAR(50) NOT NULL,
    treatment_algorithm VARCHAR(50) NOT NULL,
    target_metrics JSONB NOT NULL, -- 目标指标
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    results JSONB, -- 实验结果
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 推荐效果统计表
CREATE TABLE recommendation_analytics (
    id UUID PRIMARY KEY,
    date DATE NOT NULL,
    scenario VARCHAR(50) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    total_requests INTEGER DEFAULT 0,
    click_through_rate FLOAT8 DEFAULT 0,
    conversion_rate FLOAT8 DEFAULT 0,
    revenue_per_request FLOAT8 DEFAULT 0,
    average_position FLOAT8 DEFAULT 0,
    diversity_score FLOAT8 DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(date, scenario, algorithm)
);
```

### 特征工程

```python
class FeatureEngineering:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def build_user_features(self, user_id: str) -> UserFeatures:
        """构建用户特征"""
        # 1. 基础人口统计学特征
        user_info = await self.db.get_user_basic_info(user_id)
        demographic_features = {
            'age_group': self._get_age_group(user_info.age) if user_info.age else 'unknown',
            'gender': user_info.gender or 'unknown',
            'city': user_info.city or 'unknown',
            'registration_days': (datetime.now() - user_info.created_at).days
        }
        
        # 2. 行为特征
        interactions = await self.db.get_user_interactions(user_id, days=90)
        behavior_features = {
            'total_views': len([i for i in interactions if i.interaction_type == 'view']),
            'total_purchases': len([i for i in interactions if i.interaction_type == 'purchase']),
            'avg_session_duration': self._calculate_avg_session_duration(interactions),
            'favorite_categories': self._get_favorite_categories(interactions),
            'preferred_price_range': self._get_preferred_price_range(interactions),
            'shopping_time_pattern': self._get_shopping_time_pattern(interactions),
            'device_preference': self._get_device_preference(interactions)
        }
        
        # 3. 偏好特征
        preference_features = {
            'brand_affinity': await self._calculate_brand_affinity(user_id),
            'category_preferences': await self._calculate_category_preferences(user_id),
            'price_sensitivity': await self._calculate_price_sensitivity(user_id),
            'quality_preference': await self._calculate_quality_preference(user_id)
        }
        
        return UserFeatures(
            user_id=user_id,
            demographic=demographic_features,
            behavior=behavior_features,
            preferences=preference_features
        )
    
    async def build_item_features(self, product_id: str) -> ItemFeatures:
        """构建商品特征"""
        # 1. 基础商品信息
        product = await self.db.get_product_detail(product_id)
        basic_features = {
            'category_id': product.category_id,
            'brand_id': product.brand_id,
            'price': float(product.price),
            'age_days': (datetime.now() - product.created_at).days
        }
        
        # 2. 内容特征
        content_features = {
            'title_length': len(product.name),
            'description_length': len(product.description or ''),
            'image_count': len(product.images),
            'has_video': product.video_url is not None,
            'attribute_count': len(product.attributes)
        }
        
        # 3. 统计特征
        stats = await self.db.get_product_statistics(product_id, days=30)
        statistical_features = {
            'view_count': stats.view_count,
            'purchase_count': stats.purchase_count,
            'conversion_rate': stats.conversion_rate,
            'avg_rating': stats.avg_rating,
            'review_count': stats.review_count,
            'return_rate': stats.return_rate,
            'inventory_level': stats.current_inventory
        }
        
        # 4. 市场特征
        market_features = {
            'category_popularity': await self._get_category_popularity(product.category_id),
            'brand_popularity': await self._get_brand_popularity(product.brand_id),
            'price_competitiveness': await self._get_price_competitiveness(product_id),
            'seasonal_trend': await self._get_seasonal_trend(product.category_id)
        }
        
        return ItemFeatures(
            product_id=product_id,
            basic=basic_features,
            content=content_features,
            statistical=statistical_features,
            market=market_features
        )
```

## 推荐算法

### 协同过滤算法

```python
class CollaborativeFilteringRecommender:
    def __init__(self, model_config: dict):
        self.config = model_config
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
    
    async def train(self, interactions: List[Interaction]):
        """训练协同过滤模型"""
        # 1. 构建用户-商品交互矩阵
        interaction_matrix = self._build_interaction_matrix(interactions)
        
        # 2. 计算用户相似度矩阵
        self.user_similarity_matrix = self._calculate_user_similarity(interaction_matrix)
        
        # 3. 计算商品相似度矩阵
        self.item_similarity_matrix = self._calculate_item_similarity(interaction_matrix)
        
        # 4. 保存模型
        await self._save_model()
    
    async def recommend(self, user_id: str, num_recommendations: int = 10) -> List[Recommendation]:
        """为用户生成推荐"""
        # 1. 获取用户历史交互
        user_interactions = await self.db.get_user_interactions(user_id)
        interacted_items = {i.item_id for i in user_interactions}
        
        # 2. 基于用户的协同过滤
        user_based_scores = await self._user_based_recommendation(user_id, interacted_items)
        
        # 3. 基于商品的协同过滤
        item_based_scores = await self._item_based_recommendation(user_id, interacted_items)
        
        # 4. 混合两种方法的结果
        combined_scores = self._combine_scores(user_based_scores, item_based_scores)
        
        # 5. 排序并返回top-N推荐
        recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:num_recommendations]
        
        return [
            Recommendation(
                item_id=item_id,
                score=score,
                algorithm='collaborative_filtering',
                explanation=f"基于相似用户的购买行为推荐"
            )
            for item_id, score in recommendations
        ]
    
    def _calculate_user_similarity(self, interaction_matrix):
        """计算用户相似度（余弦相似度）"""
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity(interaction_matrix)
    
    def _calculate_item_similarity(self, interaction_matrix):
        """计算商品相似度"""
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity(interaction_matrix.T)
    
    async def _user_based_recommendation(self, user_id: str, interacted_items: set) -> dict:
        """基于用户的协同过滤推荐"""
        # 找到相似用户
        similar_users = await self._find_similar_users(user_id, top_k=50)
        
        # 收集相似用户喜欢的商品
        candidate_items = {}
        for similar_user_id, similarity in similar_users:
            similar_user_interactions = await self.db.get_user_interactions(similar_user_id)
            
            for interaction in similar_user_interactions:
                if interaction.item_id not in interacted_items:
                    item_id = interaction.item_id
                    if item_id not in candidate_items:
                        candidate_items[item_id] = 0
                    
                    # 加权评分：相似度 × 交互强度
                    candidate_items[item_id] += similarity * interaction.interaction_value
        
        return candidate_items

class ContentBasedRecommender:
    def __init__(self, model_config: dict):
        self.config = model_config
        self.item_features_matrix = None
        self.feature_vectorizer = None
    
    async def train(self, items: List[Item]):
        """训练基于内容的推荐模型"""
        # 1. 提取商品特征
        item_features = []
        for item in items:
            features = await self._extract_item_features(item)
            item_features.append(features)
        
        # 2. 特征向量化
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.feature_vectorizer = TfidfVectorizer(max_features=10000)
        self.item_features_matrix = self.feature_vectorizer.fit_transform(item_features)
        
        # 3. 保存模型
        await self._save_model()
    
    async def recommend(self, user_id: str, num_recommendations: int = 10) -> List[Recommendation]:
        """基于内容的推荐"""
        # 1. 构建用户画像
        user_profile = await self._build_user_profile(user_id)
        
        # 2. 计算用户画像与商品特征的相似度
        user_vector = self.feature_vectorizer.transform([user_profile])
        similarities = cosine_similarity(user_vector, self.item_features_matrix).flatten()
        
        # 3. 排序并过滤已交互商品
        user_interactions = await self.db.get_user_interactions(user_id)
        interacted_items = {i.item_id for i in user_interactions}
        
        recommendations = []
        for i, similarity in enumerate(similarities):
            item_id = self.item_ids[i]  # 需要维护商品ID映射
            if item_id not in interacted_items:
                recommendations.append((item_id, similarity))
        
        # 4. 返回top-N推荐
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [
            Recommendation(
                item_id=item_id,
                score=score,
                algorithm='content_based',
                explanation=f"基于您的兴趣偏好推荐"
            )
            for item_id, score in recommendations[:num_recommendations]
        ]

class DeepLearningRecommender:
    def __init__(self, model_config: dict):
        self.config = model_config
        self.model = None
        
    async def train(self, interactions: List[Interaction], user_features: dict, item_features: dict):
        """训练深度学习推荐模型"""
        import tensorflow as tf
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Input, Embedding, Dense, Concatenate, Dropout
        
        # 1. 准备训练数据
        train_data = self._prepare_training_data(interactions, user_features, item_features)
        
        # 2. 构建神经网络模型
        # 用户输入
        user_input = Input(shape=(len(user_features[0]),), name='user_features')
        user_dense = Dense(128, activation='relu')(user_input)
        user_dense = Dropout(0.2)(user_dense)
        
        # 商品输入
        item_input = Input(shape=(len(item_features[0]),), name='item_features')
        item_dense = Dense(128, activation='relu')(item_input)
        item_dense = Dropout(0.2)(item_dense)
        
        # 特征融合
        concat = Concatenate()([user_dense, item_dense])
        hidden = Dense(256, activation='relu')(concat)
        hidden = Dropout(0.3)(hidden)
        hidden = Dense(128, activation='relu')(hidden)
        output = Dense(1, activation='sigmoid', name='rating')(hidden)
        
        # 3. 编译模型
        self.model = Model(inputs=[user_input, item_input], outputs=output)
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'auc']
        )
        
        # 4. 训练模型
        history = self.model.fit(
            train_data['X'],
            train_data['y'],
            epochs=self.config.get('epochs', 100),
            batch_size=self.config.get('batch_size', 256),
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(patience=10),
                tf.keras.callbacks.ReduceLROnPlateau(patience=5)
            ]
        )
        
        # 5. 保存模型
        await self._save_model()
        
        return history
```

## API 接口

### 推荐服务

```yaml
/api/v1/recommendations:
  GET /users/{user_id}/products:
    summary: 获取用户个性化推荐
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: scenario
        in: query
        schema:
          type: string
          enum: [homepage, product_detail, cart, checkout]
          default: homepage
      - name: limit
        in: query
        schema:
          type: integer
          default: 10
          maximum: 50
    responses:
      200:
        description: 推荐商品列表
        content:
          application/json:
            schema:
              type: object
              properties:
                recommendations:
                  type: array
                  items:
                    $ref: '#/components/schemas/ProductRecommendation'
                metadata:
                  type: object
                  properties:
                    algorithm:
                      type: string
                    explanation:
                      type: string

  GET /products/{product_id}/related:
    summary: 获取相关商品推荐
    parameters:
      - name: product_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: limit
        in: query
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: 相关商品列表

  GET /trending:
    summary: 获取热门商品推荐
    parameters:
      - name: category_id
        in: query
        schema:
          type: string
          format: uuid
      - name: time_window
        in: query
        schema:
          type: string
          enum: [1h, 24h, 7d, 30d]
          default: 24h
    responses:
      200:
        description: 热门商品列表

  POST /feedback:
    summary: 记录用户反馈
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              user_id:
                type: string
                format: uuid
              product_id:
                type: string
                format: uuid
              feedback_type:
                type: string
                enum: [like, dislike, not_interested, purchased]
              context:
                type: object
    responses:
      201:
        description: 反馈记录成功
```

## 性能优化

### 缓存策略

1. **多级缓存**
   - L1: 应用内存缓存 (热门推荐)
   - L2: Redis缓存 (个性化推荐)
   - L3: 数据库 (完整推荐数据)

2. **预计算**
   - 离线批量计算相似度矩阵
   - 预生成热门用户推荐
   - 缓存商品相关推荐

3. **实时更新**
   - 增量更新用户画像
   - 实时调整推荐权重
   - 动态过滤售罄商品

## 监控指标

### 业务指标

- 推荐点击率 (CTR)
- 推荐转化率 (CVR)
- 推荐收入贡献
- 用户满意度

### 技术指标

- 推荐响应时间
- 缓存命中率
- 模型预测准确率
- 特征计算延迟

### 算法指标

- 推荐覆盖率
- 推荐多样性
- 推荐新颖性
- 推荐公平性

## 部署配置

### 环境变量

```bash
# 数据库配置
RECOMMENDATION_DB_URL=postgresql://user:pass@localhost/recommendation_db

# 机器学习配置
ML_MODEL_PATH=/models/recommendation
TENSORFLOW_SERVING_URL=http://localhost:8501

# 特征存储配置
FEATURE_STORE_URL=redis://localhost:6379/5
FEATURE_CACHE_TTL=3600

# 算法配置
DEFAULT_ALGORITHM=hybrid
ENABLE_REAL_TIME_UPDATES=true
```

## 相关文档

- [商品模块](../product-catalog/overview.md)
- [用户模块](../user-auth/overview.md)
- [机器学习架构](../../architecture/machine-learning.md)
- [实时计算](../../architecture/real-time-processing.md)
