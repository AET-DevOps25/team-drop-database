# Travel Buddy AI - 旅游景点向量搜索与 RAG 推荐系统

## 📋 项目概述

Travel Buddy AI 是一个基于向量搜索和检索增强生成 (RAG) 技术的智能旅游推荐系统。该系统能够：

- 🔍 **语义搜索**: 使用向量嵌入技术实现基于语义的景点搜索
- 🤖 **智能推荐**: 结合 LLM 生成个性化旅行推荐
- 📊 **多模式检索**: 支持密集和稀疏向量的混合检索
- 🗄️ **数据整合**: 连接现有的旅游景点数据库
- 🌐 **RESTful API**: 提供完整的 API 接口

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Web    │    │   FastAPI       │    │   Qdrant        │
│   Application   │◄──►│   Backend       │◄──►│   Vector DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Attractions   │
                       │   Database      │
                       └─────────────────┘
```

## 🚀 核心功能

### 1. 向量搜索服务 (Vector Search)

- **混合检索**: 结合密集向量（语义）和稀疏向量（关键词）
- **过滤支持**: 按城市、国家等条件过滤
- **相似度阈值**: 可调节的搜索精度控制

### 2. RAG 推荐服务 (Recommendation)

- **通用推荐**: 基于自然语言查询的景点推荐
- **城市推荐**: 特定城市的深度旅行建议
- **主题推荐**: 基于兴趣主题的个性化推荐

### 3. 数据管理

- **自动索引**: 将景点数据自动向量化并索引
- **批量处理**: 支持大规模数据的批量索引
- **增量更新**: 支持单个景点的增删改

## 📁 项目结构

```
travel_buddy_ai/
├── api/                    # API 路由
│   ├── v1.py              # 主路由
│   ├── vector_api.py      # 向量搜索 API
│   └── recommendation_api.py # 推荐服务 API
├── core/                  # 核心模块
│   ├── config.py          # 配置管理
│   ├── db.py              # 数据库连接
│   └── logger.py          # 日志配置
├── models/                # 数据模型
│   └── attractions.py     # 景点相关模型
├── repositories/          # 数据访问层
│   └── attraction_repository.py # 景点数据仓库
├── services/              # 业务逻辑层
│   ├── vector_service.py  # 向量服务
│   └── recommendation_service.py # 推荐服务
└── main.py               # 应用入口
```

## 🛠️ 安装与配置

### 1. 环境要求

- Python 3.10+
- PostgreSQL (包含景点数据)
- Qdrant 向量数据库
- OpenAI API 密钥

### 2. 安装依赖

```bash
cd genai
pip install -e .
```

### 3. 环境配置

复制 `.env.example` 到 `.env` 并配置相关参数：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant 向量数据库配置
QDRANT_HOST=localhost
QDRANT_PORT=6333

# 数据库配置
ATTRACTION_DB_HOST=localhost
ATTRACTION_DB_PORT=5432
ATTRACTION_DB_NAME=attractions_db
ATTRACTION_DB_USER=postgres
ATTRACTION_DB_PASSWORD=password
```

### 4. 启动服务

```bash
python -m travel_buddy_ai.main
```

服务将在 `http://localhost:8000` 启动。

## 📖 API 使用指南

### 向量搜索 API

#### 1. 语义搜索景点

```bash
POST /api/v1/vector/search
Content-Type: application/json

{
    "query": "古代文化遗址",
    "limit": 10,
    "score_threshold": 0.7,
    "city_filter": "北京"
}
```

#### 2. 索引景点数据

```bash
# 批量索引所有景点
POST /api/v1/vector/index/batch
{
    "page_size": 100,
    "city_filter": "上海"
}

# 索引指定景点
POST /api/v1/vector/index
{
    "attraction_ids": [1, 2, 3],
    "force_reindex": false
}
```

#### 3. 管理向量集合

```bash
# 获取集合列表
GET /api/v1/vector/collections

# 获取集合信息
GET /api/v1/vector/collections/attraction_vectors/info

# 删除景点索引
DELETE /api/v1/vector/attractions/123
```

### 推荐服务 API

#### 1. 通用旅行推荐

```bash
POST /api/v1/recommendations/general
Content-Type: application/json

{
    "query": "我想找一些适合亲子游的景点",
    "limit": 5,
    "score_threshold": 0.7,
    "city_filter": "杭州"
}
```

#### 2. 城市推荐

```bash
POST /api/v1/recommendations/city
Content-Type: application/json

{
    "city_name": "西安",
    "interest_keywords": "历史文化 古建筑",
    "limit": 8
}
```

#### 3. 主题推荐

```bash
POST /api/v1/recommendations/themed
Content-Type: application/json

{
    "theme": "自然风光",
    "location": "云南",
    "limit": 6
}
```

## 🔧 配置选项

### 向量搜索配置

- `ATTRACTION_VECTORS_COLLECTION`: 向量集合名称
- `SIMILARITY_THRESHOLD`: 默认相似度阈值
- `MAX_SEARCH_RESULTS`: 最大搜索结果数

### 数据库配置

- `ATTRACTION_DB_*`: 景点数据库连接参数
- `QDRANT_*`: Qdrant 向量数据库连接参数

### LLM 配置

- `OPENAI_API_KEY`: OpenAI API 密钥
- `CHUNK_SIZE`: 文本分块大小
- `CHUNK_OVERLAP`: 分块重叠大小

## 🚀 部署建议

### 开发环境

```bash
# 启动开发服务器
uvicorn travel_buddy_ai.main:AppCreator.create_app --factory --reload --host 0.0.0.0 --port 8000
```

### 生产环境

使用 gunicorn 或 uvicorn 部署：

```bash
# 使用 gunicorn
gunicorn travel_buddy_ai.main:AppCreator.create_app --factory -c travel_buddy_ai/gunicorn_conf.py

# 或使用 uvicorn
uvicorn travel_buddy_ai.main:AppCreator.create_app --factory --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署

可以参考现有的 Docker 配置，添加新的环境变量和依赖。

## 🔍 使用示例

### 1. 索引现有景点数据

```python
from travel_buddy_ai.services.vector_service import AttractionVectorService

# 创建向量服务实例
vector_service = AttractionVectorService()

# 批量索引所有景点
await vector_service.index_attractions_to_vector_store(page_size=100)
```

### 2. 语义搜索

```python
# 搜索相关景点
results = await vector_service.retrieve_by_similarity(
    query="适合拍照的网红景点",
    limit=10,
    score_threshold=0.7,
    city_filter="成都"
)

for result in results:
    print(f"景点: {result.attraction.name}")
    print(f"评分: {result.score}")
    print(f"描述: {result.attraction.description}")
```

### 3. 生成推荐

```python
from travel_buddy_ai.services.recommendation_service import TravelRecommendationService

# 创建推荐服务实例
recommendation_service = TravelRecommendationService()

# 获取旅行推荐
recommendation = await recommendation_service.get_travel_recommendations(
    query="计划一次3天的历史文化之旅",
    limit=8,
    city_filter="西安"
)

print(recommendation)
```

## 🤝 与现有系统集成

该向量搜索系统设计为与您现有的旅游项目无缝集成：

1. **数据库兼容**: 直接连接现有的 PostgreSQL 景点数据库
2. **API 集成**: 可通过 REST API 与前端应用集成
3. **微服务架构**: 可作为独立的微服务运行
4. **扩展性**: 支持自定义搜索逻辑和推荐策略

## 📝 待办事项

- [ ] 添加用户个性化推荐
- [ ] 支持地理位置搜索
- [ ] 添加缓存机制
- [ ] 实现A/B测试框架
- [ ] 添加推荐效果评估指标
- [ ] 支持多语言搜索

## 🐛 问题排查

### 常见问题

1. **连接 Qdrant 失败**
   - 检查 Qdrant 服务是否启动
   - 验证连接配置和端口

2. **OpenAI API 调用失败**
   - 确认 API 密钥正确
   - 检查网络连接和配额限制

3. **数据库连接失败**
   - 验证数据库连接参数
   - 确认数据库表结构与代码匹配

### 日志查看

系统日志会输出到控制台，包含详细的错误信息和调试信息。

---

该系统为您的旅游项目提供了强大的语义搜索和智能推荐能力，可以显著提升用户体验和推荐质量。
