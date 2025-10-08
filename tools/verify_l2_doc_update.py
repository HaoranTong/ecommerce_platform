"""
验证L2文档补充完成情况

检查5项补充内容是否已添加到 design.md：
1. 模块独立定义原则
2. ErrorResponse定义
3. metadata使用规范
4. Token响应格式
5. API文档规范
"""

print("=" * 80)
print("L2文档补充验证")
print("=" * 80)

import re

# 读取design.md
with open("docs/design/modules/user-auth/design.md", "r", encoding="utf-8") as f:
    content = f.read()

# 检查项列表
checks = [
    {
        "name": "1. 模块独立定义原则",
        "keywords": ["模块独立定义原则", "禁止跨模块共享", "schemas.py 中独立定义"],
        "required": 2
    },
    {
        "name": "2. ErrorResponse定义",
        "keywords": ["ErrorResponse", "错误响应格式", "class ErrorResponse"],
        "required": 2
    },
    {
        "name": "3. metadata使用规范",
        "keywords": ["metadata字段使用规范", "分页信息", "统计数据", "可选字段"],
        "required": 3
    },
    {
        "name": "4. Token响应格式",
        "keywords": ["Token响应格式规范", "Token Schema定义", "access_token", "expires_in", "OAuth2标准"],
        "required": 4
    },
    {
        "name": "5. API文档规范",
        "keywords": ["API文档规范", "summary", "description", "response_model", "OpenAPI"],
        "required": 3
    },
    {
        "name": "6. 密码强度修正",
        "keywords": ["不强制大小写", "密码安全规范", "必须包含字母和数字"],
        "required": 2
    },
    {
        "name": "7. phone字段业务用途",
        "keywords": ["phone字段", "手机号验证码登录", "短信验证码", "扩展字段业务用途"],
        "required": 3
    },
    {
        "name": "8. real_name字段业务用途",
        "keywords": ["real_name字段", "实名认证", "订单配送", "发票开具"],
        "required": 3
    }
]

print("\n检查结果：\n")

all_passed = True
for check in checks:
    found_count = sum(1 for kw in check["keywords"] if kw in content)
    passed = found_count >= check["required"]
    status = "✅" if passed else "❌"
    
    print(f"{status} {check['name']}")
    print(f"   匹配关键词: {found_count}/{len(check['keywords'])} (要求至少{check['required']})")
    
    if not passed:
        all_passed = False
        print(f"   缺失关键词: {[kw for kw in check['keywords'] if kw not in content]}")
    print()

# 统计文档长度
lines = content.split('\n')
print("=" * 80)
print(f"文档统计：")
print(f"  总行数: {len(lines)}")
print(f"  总字符数: {len(content)}")
print()

# 提取章节标题
sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
print(f"  主要章节数: {len([s for s in sections if not s.startswith('#')])}")
print()

if all_passed:
    print("✅ 所有补充内容已添加到设计文档")
else:
    print("⚠️ 部分内容未完全添加，请检查")

print("=" * 80)

# 额外验证：检查是否修正了"大小写字母"的错误
if "大小写字母" in content and "不强制大小写" in content:
    print("⚠️ 警告：文档中同时存在'大小写字母'和'不强制大小写'，可能存在冲突")
elif "大小写字母" in content:
    print("❌ 错误：文档中仍包含'大小写字母'，需要修正")
elif "不强制大小写" in content:
    print("✅ 密码强度描述已修正为'不强制大小写'")
else:
    print("⚠️ 未找到密码强度相关描述")

print("=" * 80)
print("\n文档更新完成！")
