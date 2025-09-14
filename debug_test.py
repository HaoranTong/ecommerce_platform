import pytest


def test_debug_product_creation(unit_test_client):
    """Debug product creation to see the actual error"""
    response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '测试商品',
        'description': '这是一个测试商品',
        'status': 'published',
        'sort_order': 1
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    assert False, f"Debug info - Status: {response.status_code}, Response: {response.text}"