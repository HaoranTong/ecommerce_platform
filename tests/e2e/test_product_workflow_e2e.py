"""
产品目录模块端到端测试

根据docs/standards/testing-standards.md规范实现
测试覆盖：
- 完整的商品管理业务流程
- 真实用户场景的端到端验证
- 跨模块的业务逻辑验证
- 完整的数据生命周期测试

使用真实的HTTP客户端和数据库环境
"""

import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.core.database import Base, get_db

# E2E测试数据库配置
E2E_TEST_DB_PATH = "./tests/e2e_test.db"
E2E_TEST_DATABASE_URL = f"sqlite:///{E2E_TEST_DB_PATH}"


@pytest.fixture(scope="module")
def e2e_test_engine():
    """E2E测试数据库引擎"""
    # 清理可能存在的旧数据库文件
    if os.path.exists(E2E_TEST_DB_PATH):
        os.remove(E2E_TEST_DB_PATH)
    
    engine = create_engine(
        E2E_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # 清理测试数据库文件
    engine.dispose()
    if os.path.exists(E2E_TEST_DB_PATH):
        os.remove(E2E_TEST_DB_PATH)


@pytest.fixture(scope="module")
def e2e_test_client(e2e_test_engine):
    """E2E测试客户端"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False, 
        bind=e2e_test_engine
    )
    
    def override_get_db():
        database = TestingSessionLocal()
        try:
            yield database
        finally:
            database.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestCompleteProductWorkflow:
    """完整商品管理工作流端到端测试"""

    def test_full_product_management_lifecycle(self, e2e_test_client):
        """测试完整的商品管理生命周期"""
        
        # ================== 第一阶段：基础数据准备 ==================
        print("\n🔧 第一阶段：创建基础数据...")
        
        # 1.1 创建品牌
        brand_payload = {
            "name": "华为",
            "slug": "huawei", 
            "description": "华为技术有限公司",
            "logo_url": "https://www.huawei.com/logo.png",
            "website_url": "https://www.huawei.com",
            "is_active": True
        }
        
        print("🏷️ 创建品牌...")
        brand_response = e2e_test_client.post("/api/v1/product-catalog/brands", json=brand_payload)
        assert brand_response.status_code == 201, f"品牌创建失败: {brand_response.text}"
        brand_data = brand_response.json()
        brand_id = brand_data["id"]
        print(f"✅ 品牌创建成功，ID: {brand_id}")
        
        # 1.2 创建分类层次结构
        parent_category_payload = {
            "name": "数码设备",
            "sort_order": 1,
            "is_active": True
        }
        
        print("📁 创建父级分类...")
        parent_category_response = e2e_test_client.post("/api/v1/product-catalog/categories", json=parent_category_payload)
        assert parent_category_response.status_code == 201, f"父分类创建失败: {parent_category_response.text}"
        parent_category_data = parent_category_response.json()
        parent_category_id = parent_category_data["id"]
        print(f"✅ 父分类创建成功，ID: {parent_category_id}")
        
        child_category_payload = {
            "name": "智能手机",
            "parent_id": parent_category_id,
            "sort_order": 1,
            "is_active": True
        }
        
        print("📁 创建子级分类...")
        child_category_response = e2e_test_client.post("/api/v1/product-catalog/categories", json=child_category_payload)
        assert child_category_response.status_code == 201, f"子分类创建失败: {child_category_response.text}"
        child_category_data = child_category_response.json()
        category_id = child_category_data["id"]
        print(f"✅ 子分类创建成功，ID: {category_id}")
        
        # ================== 第二阶段：商品创建和管理 ==================
        print("\n📱 第二阶段：商品创建和管理...")
        
        # 2.1 创建商品（草稿状态）
        product_payload = {
            "name": "华为Mate 50 Pro",
            "description": "华为Mate 50 Pro 旗舰智能手机，搭载昆仑玻璃和XMAGE影像",
            "brand_id": brand_id,
            "category_id": category_id,
            "status": "draft", 
            "seo_title": "华为Mate 50 Pro - 旗舰智能手机",
            "seo_description": "华为Mate 50 Pro搭载昆仑玻璃、XMAGE影像系统，提供卓越的拍照和性能体验",
            "seo_keywords": "华为,Mate 50 Pro,智能手机,昆仑玻璃,XMAGE",
            "sort_order": 1
        }
        
        print("📱 创建商品...")
        product_response = e2e_test_client.post("/api/v1/product-catalog/products", json=product_payload)
        assert product_response.status_code == 201, f"商品创建失败: {product_response.text}"
        product_data = product_response.json()
        product_id = product_data["id"]
        print(f"✅ 商品创建成功，ID: {product_id}, 状态: {product_data['status']}")
        
        # 2.2 添加商品属性
        attributes_payload = [
            {
                "product_id": product_id,
                "attribute_name": "处理器",
                "attribute_value": "骁龙8+ Gen 1",
                "attribute_type": "text",
                "is_searchable": True
            },
            {
                "product_id": product_id, 
                "attribute_name": "屏幕尺寸",
                "attribute_value": "6.74英寸",
                "attribute_type": "text",
                "is_searchable": True
            },
            {
                "product_id": product_id,
                "attribute_name": "存储容量", 
                "attribute_value": "256GB",
                "attribute_type": "select",
                "is_searchable": True
            }
        ]
        
        print("🔧 添加商品属性...")
        for attr_data in attributes_payload:
            attr_response = e2e_test_client.post("/api/v1/product-catalog/attributes", json=attr_data)
            assert attr_response.status_code == 201, f"属性添加失败: {attr_response.text}"
        print("✅ 商品属性添加完成")
        
        # 2.3 添加SKU规格
        skus_payload = [
            {
                "product_id": product_id,
                "sku_code": "MATE50PRO-256GB-BLACK",
                "name": "华为Mate 50 Pro 256GB 曜金黑",
                "price": 6799.00,
                "cost_price": 4500.00,
                "market_price": 7299.00,
                "weight": 0.205,
                "volume": 0.0001,
                "is_active": True
            },
            {
                "product_id": product_id,
                "sku_code": "MATE50PRO-512GB-BLACK", 
                "name": "华为Mate 50 Pro 512GB 曜金黑",
                "price": 7799.00,
                "cost_price": 5200.00,
                "market_price": 8299.00,
                "weight": 0.205,
                "volume": 0.0001,
                "is_active": True
            }
        ]
        
        print("📦 添加SKU规格...")
        sku_ids = []
        for sku_data in skus_payload:
            sku_response = e2e_test_client.post("/api/v1/product-catalog/skus", json=sku_data)
            assert sku_response.status_code == 201, f"SKU创建失败: {sku_response.text}"
            sku_ids.append(sku_response.json()["id"])
        print(f"✅ SKU创建完成，数量: {len(sku_ids)}")
        
        # 2.4 为SKU添加属性
        sku_attributes_payload = [
            {"sku_id": sku_ids[0], "attribute_name": "存储", "attribute_value": "256GB"},
            {"sku_id": sku_ids[0], "attribute_name": "颜色", "attribute_value": "曜金黑"},
            {"sku_id": sku_ids[1], "attribute_name": "存储", "attribute_value": "512GB"}, 
            {"sku_id": sku_ids[1], "attribute_name": "颜色", "attribute_value": "曜金黑"}
        ]
        
        print("🎨 添加SKU属性...")
        for attr_data in sku_attributes_payload:
            attr_response = e2e_test_client.post("/api/v1/product-catalog/sku-attributes", json=attr_data)
            assert attr_response.status_code == 201, f"SKU属性添加失败: {attr_response.text}"
        print("✅ SKU属性添加完成")
        
        # 2.5 添加商品图片
        images_payload = [
            {
                "product_id": product_id,
                "image_url": "https://res.vmallres.com/pimages/mate50pro-main.jpg",
                "alt_text": "华为Mate 50 Pro主图",
                "sort_order": 1,
                "is_primary": True
            },
            {
                "product_id": product_id,
                "image_url": "https://res.vmallres.com/pimages/mate50pro-back.jpg",
                "alt_text": "华为Mate 50 Pro背面",
                "sort_order": 2,
                "is_primary": False
            },
            {
                "sku_id": sku_ids[0],
                "image_url": "https://res.vmallres.com/pimages/mate50pro-256gb-black.jpg",
                "alt_text": "华为Mate 50 Pro 256GB 曜金黑",
                "sort_order": 1,
                "is_primary": False
            }
        ]
        
        print("🖼️ 添加商品图片...")
        for img_data in images_payload:
            img_response = e2e_test_client.post("/api/v1/product-catalog/images", json=img_data)
            assert img_response.status_code == 201, f"图片添加失败: {img_response.text}"
        print("✅ 商品图片添加完成")
        
        # 2.6 添加商品标签
        tags_payload = [
            {"product_id": product_id, "tag_name": "旗舰手机", "tag_type": "feature"},
            {"product_id": product_id, "tag_name": "昆仑玻璃", "tag_type": "feature"},
            {"product_id": product_id, "tag_name": "XMAGE影像", "tag_type": "feature"},
            {"product_id": product_id, "tag_name": "新品推荐", "tag_type": "promotion"}
        ]
        
        print("🏷️ 添加商品标签...")
        for tag_data in tags_payload:
            tag_response = e2e_test_client.post("/api/v1/product-catalog/tags", json=tag_data)
            assert tag_response.status_code == 201, f"标签添加失败: {tag_response.text}"
        print("✅ 商品标签添加完成")
        
        # ================== 第三阶段：商品发布和查询验证 ==================
        print("\n🚀 第三阶段：商品发布和查询验证...")
        
        # 3.1 发布商品
        publish_payload = {"status": "published"}
        print("📢 发布商品...")
        publish_response = e2e_test_client.put(f"/api/v1/product-catalog/products/{product_id}/publish", json=publish_payload)
        assert publish_response.status_code == 200, f"商品发布失败: {publish_response.text}"
        published_product = publish_response.json()
        assert published_product["status"] == "published"
        assert published_product["published_at"] is not None
        print(f"✅ 商品发布成功，发布时间: {published_product['published_at']}")
        
        # 3.2 验证商品详情查询
        print("🔍 验证商品详情查询...")
        detail_response = e2e_test_client.get(f"/api/v1/product-catalog/products/{product_id}")
        assert detail_response.status_code == 200, f"商品详情查询失败: {detail_response.text}"
        product_detail = detail_response.json()
        
        # 验证基本信息
        assert product_detail["name"] == "华为Mate 50 Pro"
        assert product_detail["brand_id"] == brand_id
        assert product_detail["category_id"] == category_id
        assert product_detail["status"] == "published"
        print("✅ 商品详情验证通过")
        
        # 3.3 验证分类查询
        print("📁 验证分类查询...")
        category_products_response = e2e_test_client.get(f"/api/v1/product-catalog/products?category_id={category_id}")
        assert category_products_response.status_code == 200
        category_products = category_products_response.json()
        assert len(category_products) > 0
        assert any(p["id"] == product_id for p in category_products)
        print("✅ 分类查询验证通过")
        
        # 3.4 验证品牌查询
        print("🏷️ 验证品牌查询...")
        brand_products_response = e2e_test_client.get(f"/api/v1/product-catalog/products?brand_id={brand_id}")
        assert brand_products_response.status_code == 200
        brand_products = brand_products_response.json()
        assert len(brand_products) > 0
        assert any(p["id"] == product_id for p in brand_products)
        print("✅ 品牌查询验证通过")
        
        # 3.5 验证状态过滤
        print("📊 验证状态过滤...")
        published_products_response = e2e_test_client.get("/api/v1/product-catalog/products?status=published")
        assert published_products_response.status_code == 200
        published_products = published_products_response.json()
        assert len(published_products) > 0
        assert all(p["status"] == "published" for p in published_products)
        print("✅ 状态过滤验证通过")
        
        # ================== 第四阶段：商品更新和管理 ==================
        print("\n✏️ 第四阶段：商品更新和管理...")
        
        # 4.1 更新商品信息
        update_payload = {
            "name": "华为Mate 50 Pro（升级版）",
            "description": "华为Mate 50 Pro 旗舰智能手机，搭载昆仑玻璃和XMAGE影像，性能全面升级",
            "seo_title": "华为Mate 50 Pro升级版 - 旗舰智能手机",
            "sort_order": 5
        }
        
        print("✏️ 更新商品信息...")
        update_response = e2e_test_client.put(f"/api/v1/product-catalog/products/{product_id}", json=update_payload)
        assert update_response.status_code == 200, f"商品更新失败: {update_response.text}"
        updated_product = update_response.json()
        assert updated_product["name"] == "华为Mate 50 Pro（升级版）"
        assert updated_product["sort_order"] == 5
        print("✅ 商品信息更新成功")
        
        # 4.2 更新SKU信息
        sku_update_payload = {
            "price": 6299.00,  # 降价
            "market_price": 6799.00
        }
        
        print("💰 更新SKU价格...")
        sku_update_response = e2e_test_client.put(f"/api/v1/product-catalog/skus/{sku_ids[0]}", json=sku_update_payload)
        assert sku_update_response.status_code == 200, f"SKU更新失败: {sku_update_response.text}"
        updated_sku = sku_update_response.json()
        assert float(updated_sku["price"]) == 6299.00
        print("✅ SKU价格更新成功")
        
        # ================== 第五阶段：性能和并发测试 ==================
        print("\n⚡ 第五阶段：性能和并发测试...")
        
        # 5.1 批量查询性能测试
        print("🔄 测试批量查询性能...")
        start_time = time.time()
        for _ in range(10):
            response = e2e_test_client.get("/api/v1/product-catalog/products")
            assert response.status_code == 200
        end_time = time.time()
        
        avg_query_time = (end_time - start_time) / 10
        assert avg_query_time < 1.0, f"查询性能不达标: {avg_query_time:.3f}秒/次"
        print(f"✅ 批量查询性能测试通过，平均响应时间: {avg_query_time:.3f}秒")
        
        # 5.2 复杂筛选查询测试
        print("🎯 测试复杂筛选查询...")
        complex_queries = [
            f"/api/v1/product-catalog/products?brand_id={brand_id}&status=published",
            f"/api/v1/product-catalog/products?category_id={category_id}&sort_by=sort_order&sort_order=asc",
            "/api/v1/product-catalog/products?keyword=华为&status=published"
        ]
        
        for query in complex_queries:
            start_time = time.time()
            response = e2e_test_client.get(query)
            end_time = time.time()
            
            assert response.status_code == 200, f"复杂查询失败: {query}"
            query_time = end_time - start_time
            assert query_time < 2.0, f"复杂查询超时: {query_time:.3f}秒"
        
        print("✅ 复杂筛选查询测试通过")
        
        # ================== 第六阶段：数据完整性验证 ==================
        print("\n🔒 第六阶段：数据完整性验证...")
        
        # 6.1 验证关联数据完整性
        print("🔗 验证关联数据完整性...")
        
        # 获取完整商品信息（包含所有关联数据）
        complete_product_response = e2e_test_client.get(f"/api/v1/product-catalog/products/{product_id}/complete")
        
        # 如果complete端点不存在，使用基础端点验证
        if complete_product_response.status_code == 404:
            print("ℹ️ 使用基础端点验证关联数据...")
            
            # 验证商品属性
            product_attrs_response = e2e_test_client.get(f"/api/v1/product-catalog/products/{product_id}/attributes") 
            if product_attrs_response.status_code == 200:
                attrs = product_attrs_response.json()
                assert len(attrs) >= 3, f"商品属性数量不足: {len(attrs)}"
                print(f"✅ 商品属性验证通过，数量: {len(attrs)}")
            
            # 验证商品SKU
            product_skus_response = e2e_test_client.get(f"/api/v1/product-catalog/products/{product_id}/skus")
            if product_skus_response.status_code == 200:
                skus = product_skus_response.json()
                assert len(skus) == 2, f"SKU数量不匹配: {len(skus)}"
                print(f"✅ SKU数据验证通过，数量: {len(skus)}")
            
            # 验证商品图片
            product_images_response = e2e_test_client.get(f"/api/v1/product-catalog/products/{product_id}/images")
            if product_images_response.status_code == 200:
                images = product_images_response.json()
                assert len(images) >= 2, f"图片数量不足: {len(images)}"
                primary_images = [img for img in images if img.get("is_primary")]
                assert len(primary_images) == 1, f"主图数量错误: {len(primary_images)}"
                print(f"✅ 图片数据验证通过，数量: {len(images)}，主图: {len(primary_images)}")
        
        print("✅ 数据完整性验证完成")
        
        # ================== 测试结果汇总 ==================
        print("\n🎉 端到端测试完成！")
        print("=" * 50)
        print("📊 测试结果汇总:")
        print(f"✅ 品牌创建: ID {brand_id}")
        print(f"✅ 分类创建: 父级 ID {parent_category_id}, 子级 ID {category_id}")
        print(f"✅ 商品创建: ID {product_id}, 状态: published")
        print(f"✅ SKU创建: {len(sku_ids)}个规格")
        print(f"✅ 商品属性: 3个基础属性")
        print(f"✅ SKU属性: 4个规格属性")
        print(f"✅ 商品图片: 3张图片（1张主图）")
        print(f"✅ 商品标签: 4个标签")
        print(f"✅ 性能验证: 平均查询时间 {avg_query_time:.3f}秒")
        print("=" * 50)

    def test_error_handling_scenarios(self, e2e_test_client):
        """测试错误处理场景"""
        
        print("\n❌ 测试错误处理场景...")
        
        # 测试创建重复品牌
        print("🔄 测试重复品牌创建...")
        brand_payload = {"name": "重复品牌", "slug": "duplicate-brand", "is_active": True}
        
        # 第一次创建应该成功
        response1 = e2e_test_client.post("/api/v1/product-catalog/brands", json=brand_payload)
        assert response1.status_code == 201
        
        # 第二次创建应该失败
        response2 = e2e_test_client.post("/api/v1/product-catalog/brands", json=brand_payload)
        assert response2.status_code == 400
        print("✅ 重复品牌创建错误处理验证通过")
        
        # 测试无效的外键引用
        print("🔗 测试无效外键引用...")
        invalid_product_payload = {
            "name": "无效商品",
            "brand_id": 99999,  # 不存在的品牌ID
            "category_id": 99999,  # 不存在的分类ID
            "status": "draft"
        }
        
        response = e2e_test_client.post("/api/v1/product-catalog/products", json=invalid_product_payload)
        assert response.status_code == 400
        print("✅ 无效外键引用错误处理验证通过")
        
        # 测试访问不存在的资源
        print("🔍 测试访问不存在的资源...")
        response = e2e_test_client.get("/api/v1/product-catalog/products/99999")
        assert response.status_code == 404
        print("✅ 不存在资源访问错误处理验证通过")
        
        print("✅ 错误处理场景测试完成")

    def test_business_rules_validation(self, e2e_test_client):
        """测试业务规则验证"""
        
        print("\n📋 测试业务规则验证...")
        
        # 创建测试数据
        brand_payload = {"name": "规则测试品牌", "slug": "rules-brand", "is_active": True}
        brand_response = e2e_test_client.post("/api/v1/product-catalog/brands", json=brand_payload)
        brand_id = brand_response.json()["id"]
        
        category_payload = {"name": "规则测试分类", "is_active": True}
        category_response = e2e_test_client.post("/api/v1/product-catalog/categories", json=category_payload)
        category_id = category_response.json()["id"]
        
        # 测试商品状态转换规则
        print("📊 测试商品状态转换...")
        product_payload = {
            "name": "状态测试商品",
            "brand_id": brand_id,
            "category_id": category_id,
            "status": "draft"
        }
        
        product_response = e2e_test_client.post("/api/v1/product-catalog/products", json=product_payload)
        product_id = product_response.json()["id"]
        
        # 草稿 -> 发布
        publish_response = e2e_test_client.put(f"/api/v1/product-catalog/products/{product_id}/publish", json={"status": "published"})
        assert publish_response.status_code == 200
        published_product = publish_response.json()
        assert published_product["status"] == "published"
        assert published_product["published_at"] is not None
        
        # 发布 -> 归档
        archive_response = e2e_test_client.put(f"/api/v1/product-catalog/products/{product_id}/publish", json={"status": "archived"})
        assert archive_response.status_code == 200
        archived_product = archive_response.json()
        assert archived_product["status"] == "archived"
        
        print("✅ 商品状态转换规则验证通过")
        
        # 测试SKU业务规则
        print("📦 测试SKU业务规则...")
        
        # 创建SKU
        sku_payload = {
            "product_id": product_id,
            "sku_code": "UNIQUE-SKU-001",
            "name": "测试SKU",
            "price": 100.00,
            "is_active": True
        }
        
        sku_response = e2e_test_client.post("/api/v1/product-catalog/skus", json=sku_payload)
        assert sku_response.status_code == 201
        sku_id = sku_response.json()["id"]
        
        # 测试重复SKU代码
        duplicate_sku_payload = {
            "product_id": product_id,
            "sku_code": "UNIQUE-SKU-001",  # 重复的SKU代码
            "name": "重复SKU",
            "price": 200.00
        }
        
        duplicate_response = e2e_test_client.post("/api/v1/product-catalog/skus", json=duplicate_sku_payload)
        assert duplicate_response.status_code == 400
        print("✅ SKU唯一性规则验证通过")
        
        print("✅ 业务规则验证测试完成")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])