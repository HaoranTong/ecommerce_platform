"""
购物车系统测试脚本
使用 PowerShell: .\test_cart_system.ps1
"""

# 定义API基础URL
$baseUrl = "http://localhost:8000"
$apiUrl = "$baseUrl/api"

Write-Host "========================================" -ForegroundColor Green
Write-Host "        购物车系统 API 测试" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green

# 定义测试数据
$randomSuffix = Get-Random -Minimum 1000 -Maximum 9999
$testUser = @{
    username = "cart_test_user_$randomSuffix"
    email = "cart_test_$randomSuffix@example.com"
    password = "password123"
    phone = "13800138000"
    real_name = "购物车测试用户"
}

$testProduct = @{
    name = "测试购物车商品"
    sku = "CART-TEST-001"
    description = "购物车测试专用商品"
    price = 99.99
    stock_quantity = 50
    category_id = 1
}

try {
    Write-Host "`n1. 用户注册和登录..." -ForegroundColor Yellow
    
    # 用户注册
    $registerResponse = Invoke-RestMethod -Uri "$apiUrl/auth/register" -Method Post -Body ($testUser | ConvertTo-Json) -ContentType "application/json" -ErrorAction SilentlyContinue
    
    # 用户登录
    $loginData = @{
        username = $testUser.username
        password = $testUser.password
    }
    
    $loginResponse = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -Body ($loginData | ConvertTo-Json) -ContentType "application/json"
    $token = $loginResponse.access_token
    
    Write-Host "✓ 用户登录成功，Token: $($token.Substring(0, 20))..." -ForegroundColor Green
    
    # 设置授权头
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    Write-Host "`n2. 获取空购物车状态..." -ForegroundColor Yellow
    
    # 获取购物车详情
    $cartResponse = Invoke-RestMethod -Uri "$apiUrl/cart" -Method Get -Headers $headers
    Write-Host "✓ 空购物车状态:" -ForegroundColor Green
    Write-Host "  - 商品种类: $($cartResponse.total_items)" -ForegroundColor Cyan
    Write-Host "  - 总数量: $($cartResponse.total_quantity)" -ForegroundColor Cyan
    Write-Host "  - 总金额: ¥$($cartResponse.total_amount)" -ForegroundColor Cyan
    
    Write-Host "`n3. 获取可用商品列表..." -ForegroundColor Yellow
    
    # 获取商品列表
    $productsResponse = Invoke-RestMethod -Uri "$apiUrl/products" -Method Get -Headers $headers
    
    if (-not $productsResponse -or $productsResponse.Count -eq 0) {
        Write-Host "✗ 没有可用商品，无法测试购物车" -ForegroundColor Red
        exit 1
    }
    
    $firstProduct = $productsResponse[0]
    $productId = $firstProduct.id
    
    Write-Host "✓ 找到商品: $($firstProduct.name) (ID: $productId)" -ForegroundColor Green
    Write-Host "  - SKU: $($firstProduct.sku)" -ForegroundColor Cyan
    Write-Host "  - 商品ID: $productId" -ForegroundColor Cyan
    Write-Host "  - 库存: $($firstProduct.stock_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n4. 添加商品到购物车..." -ForegroundColor Yellow
    
    # 添加商品到购物车
    $addToCartData = @{
        product_id = $productId
        quantity = 2
    }
    
    $addResponse = Invoke-RestMethod -Uri "$apiUrl/cart/add" -Method Post -Body ($addToCartData | ConvertTo-Json) -Headers $headers
    Write-Host "✓ $($addResponse.message)" -ForegroundColor Green
    Write-Host "  - 购物车商品种类: $($addResponse.cart_count)" -ForegroundColor Cyan
    Write-Host "  - 购物车总数量: $($addResponse.total_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n5. 再次添加相同商品..." -ForegroundColor Yellow
    
    # 再次添加相同商品
    $addToCartData.quantity = 1
    $addResponse2 = Invoke-RestMethod -Uri "$apiUrl/cart/add" -Method Post -Body ($addToCartData | ConvertTo-Json) -Headers $headers
    Write-Host "✓ $($addResponse2.message)" -ForegroundColor Green
    Write-Host "  - 购物车商品种类: $($addResponse2.cart_count)" -ForegroundColor Cyan
    Write-Host "  - 购物车总数量: $($addResponse2.total_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n6. 获取购物车详情..." -ForegroundColor Yellow
    
    # 获取购物车详情
    $cartResponse = Invoke-RestMethod -Uri "$apiUrl/cart" -Method Get -Headers $headers
    Write-Host "✓ 购物车详情:" -ForegroundColor Green
    Write-Host "  - 商品种类: $($cartResponse.total_items)" -ForegroundColor Cyan
    Write-Host "  - 总数量: $($cartResponse.total_quantity)" -ForegroundColor Cyan
    Write-Host "  - 总金额: ¥$($cartResponse.total_amount)" -ForegroundColor Cyan
    
    foreach ($item in $cartResponse.items) {
        Write-Host "  商品: $($item.product_name)" -ForegroundColor Cyan
        Write-Host "    - 数量: $($item.quantity)" -ForegroundColor Cyan
        Write-Host "    - 单价: ¥$($item.price)" -ForegroundColor Cyan
        Write-Host "    - 小计: ¥$($item.subtotal)" -ForegroundColor Cyan
        Write-Host "    - 库存: $($item.stock_quantity)" -ForegroundColor Cyan
    }
    
    Write-Host "`n7. 更新商品数量..." -ForegroundColor Yellow
    
    # 更新商品数量
    $updateData = @{
        quantity = 5
    }
    
    $updateResponse = Invoke-RestMethod -Uri "$apiUrl/cart/items/$productId" -Method Put -Body ($updateData | ConvertTo-Json) -Headers $headers
    Write-Host "✓ $($updateResponse.message)" -ForegroundColor Green
    Write-Host "  - 购物车总数量: $($updateResponse.total_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n8. 获取购物车统计..." -ForegroundColor Yellow
    
    # 获取购物车统计
    $countResponse = Invoke-RestMethod -Uri "$apiUrl/cart/count" -Method Get -Headers $headers
    Write-Host "✓ 购物车统计:" -ForegroundColor Green
    Write-Host "  - 商品种类: $($countResponse.cart_count)" -ForegroundColor Cyan
    Write-Host "  - 总数量: $($countResponse.total_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n9. 移除商品..." -ForegroundColor Yellow
    
    # 移除商品
    $removeResponse = Invoke-RestMethod -Uri "$apiUrl/cart/items/$productId" -Method Delete -Headers $headers
    Write-Host "✓ $($removeResponse.message)" -ForegroundColor Green
    Write-Host "  - 购物车总数量: $($removeResponse.total_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n10. 验证购物车已空..." -ForegroundColor Yellow
    
    # 验证购物车为空
    $finalCartResponse = Invoke-RestMethod -Uri "$apiUrl/cart" -Method Get -Headers $headers
    Write-Host "✓ 最终购物车状态:" -ForegroundColor Green
    Write-Host "  - 商品种类: $($finalCartResponse.total_items)" -ForegroundColor Cyan
    Write-Host "  - 总数量: $($finalCartResponse.total_quantity)" -ForegroundColor Cyan
    Write-Host "  - 总金额: ¥$($finalCartResponse.total_amount)" -ForegroundColor Cyan
    
    Write-Host "`n11. 测试清空购物车功能..." -ForegroundColor Yellow
    
    # 先添加商品
    $addToCartData = @{
        product_id = $productId
        quantity = 3
    }
    Invoke-RestMethod -Uri "$apiUrl/cart/add" -Method Post -Body ($addToCartData | ConvertTo-Json) -Headers $headers | Out-Null
    
    # 清空购物车
    $clearResponse = Invoke-RestMethod -Uri "$apiUrl/cart/clear" -Method Delete -Headers $headers
    Write-Host "✓ $($clearResponse.message)" -ForegroundColor Green
    Write-Host "  - 购物车总数量: $($clearResponse.total_quantity)" -ForegroundColor Cyan
    
    Write-Host "`n12. 测试边界情况..." -ForegroundColor Yellow
    
    # 测试库存不足情况
    try {
        $largeQuantityData = @{
            product_id = $productId
            quantity = 999
        }
        Invoke-RestMethod -Uri "$apiUrl/cart/add" -Method Post -Body ($largeQuantityData | ConvertTo-Json) -Headers $headers
        Write-Host "✗ 应该抛出库存不足错误" -ForegroundColor Red
    } catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-Host "✓ 正确处理库存不足情况" -ForegroundColor Green
        } else {
            Write-Host "✗ 意外错误: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    # 测试删除不存在的商品
    try {
        Invoke-RestMethod -Uri "$apiUrl/cart/items/999999" -Method Delete -Headers $headers
        Write-Host "✗ 应该抛出商品不存在错误" -ForegroundColor Red
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "✓ 正确处理商品不存在情况" -ForegroundColor Green
        } else {
            Write-Host "✗ 意外错误: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "        购物车系统测试完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

} catch {
    Write-Host "`n❌ 测试过程中出现错误：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP状态码: $statusCode" -ForegroundColor Red
        
        try {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            Write-Host "错误详情: $errorBody" -ForegroundColor Red
        } catch {
            Write-Host "无法读取错误详情" -ForegroundColor Red
        }
    }
    
    exit 1
}
