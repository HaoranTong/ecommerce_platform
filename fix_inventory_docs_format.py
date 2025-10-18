#!/usr/bin/env python3
"""
批量修复 inventory-management 模块文档格式问题

修复内容：
1. 添加 YAML Front Matter
2. 添加"依赖标准"章节
3. 为代码块添加语言标识
"""

import re
from pathlib import Path

# 文档目录
DOCS_DIR = Path("docs/design/modules/inventory-management")

# YAML Front Matter 模板
YAML_TEMPLATES = {
    "design.md": """---
title: "库存管理模块设计文档"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "系统架构师"
dependencies:
  - "docs/standards/api-standards.md"
  - "docs/standards/database-standards.md"
  - "docs/standards/architecture-standards.md"
  - "docs/architecture/application-architecture.md"
labels:
  - "inventory-management"
  - "system-design"
  - "repository-pattern"
---

""",
    "overview.md": """---
title: "库存管理模块概览"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "技术经理"
dependencies:
  - "docs/architecture/business-architecture.md"
  - "docs/architecture/application-architecture.md"
labels:
  - "inventory-management"
  - "module-overview"
---

""",
    "README.md": """---
title: "库存管理模块快速指南"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "开发团队"
dependencies:
  - "docs/design/modules/inventory-management/design.md"
  - "docs/design/modules/inventory-management/requirements.md"
labels:
  - "inventory-management"
  - "quick-guide"
---

""",
    "requirements.md": """---
title: "库存管理模块需求规格说明"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "产品经理"
dependencies:
  - "docs/requirements/functional.md"
  - "docs/requirements/non-functional.md"
  - "docs/standards/requirements-standards.md"
labels:
  - "inventory-management"
  - "requirements"
---

""",
    "implementation.md": """---
title: "库存管理模块实现指南"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "开发工程师"
dependencies:
  - "docs/design/modules/inventory-management/design.md"
  - "docs/standards/code-standards.md"
  - "docs/standards/architecture-standards.md"
labels:
  - "inventory-management"
  - "implementation"
  - "repository-pattern"
---

""",
    "api-spec.md": """---
title: "库存管理模块API规范"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "API架构师"
dependencies:
  - "docs/standards/api-standards.md"
  - "docs/design/modules/inventory-management/design.md"
labels:
  - "inventory-management"
  - "api-specification"
  - "restful"
---

""",
    "api-implementation.md": """---
title: "库存管理模块API实现文档"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "API开发工程师"
dependencies:
  - "docs/design/modules/inventory-management/api-spec.md"
  - "docs/standards/api-standards.md"
labels:
  - "inventory-management"
  - "api-implementation"
---

"""
}

# 依赖标准章节模板
DEPENDENCY_SECTION = """
## 依赖标准

本文档遵循以下标准规范：

| 标准文档 | 版本 | 应用范围 |
|---------|------|---------|
| [API设计标准](../../standards/api-standards.md) | v1.0 | RESTful API设计、路由命名 |
| [数据库设计标准](../../standards/database-standards.md) | v1.0 | 表结构设计、字段命名、索引设计 |
| [架构设计标准](../../standards/architecture-standards.md) | v1.0 | 四层架构、Repository模式、依赖注入 |
| [应用架构](../../architecture/application-architecture.md) | v1.0 | 模块化单体、模块边界、依赖管理 |

**架构版本**: V2.0 - 四层架构 (Router → Service → Repository → Model)

"""


def add_yaml_front_matter(content: str, filename: str) -> str:
    """添加或替换 YAML Front Matter"""
    yaml_template = YAML_TEMPLATES.get(filename, "")
    if not yaml_template:
        print(f"  ⚠️  {filename} 没有 YAML 模板，跳过")
        return content
    
    # 检查是否已有 YAML Front Matter
    if content.startswith("---"):
        # 找到结束的 ---
        end_match = re.search(r'\n---\s*\n', content[3:])
        if end_match:
            # 替换现有的 YAML
            content = yaml_template + content[3 + end_match.end():]
            print(f"  ✅ {filename} 替换 YAML Front Matter")
            return content
    
    # 找到第一个 # 标题
    match = re.search(r'^#\s+', content, re.MULTILINE)
    if match:
        # 在标题前插入 YAML
        content = yaml_template + content
        print(f"  ✅ {filename} 添加 YAML Front Matter")
    else:
        print(f"  ⚠️  {filename} 未找到标题，无法插入 YAML")
    
    return content


def add_dependency_section(content: str, filename: str) -> str:
    """添加依赖标准章节"""
    if "## 依赖标准" in content:
        print(f"  ⏭️  {filename} 已有依赖标准章节，跳过")
        return content
    
    # 在第一个 ## 章节前插入依赖标准
    # 跳过 YAML Front Matter 后的第一个章节
    lines = content.split('\n')
    insert_pos = -1
    in_yaml = False
    yaml_ended = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---' and not yaml_ended:
            if in_yaml:
                yaml_ended = True
            else:
                in_yaml = True
            continue
        
        if yaml_ended and line.startswith('## '):
            insert_pos = i
            break
    
    if insert_pos > 0:
        lines.insert(insert_pos, DEPENDENCY_SECTION.strip())
        content = '\n'.join(lines)
        print(f"  ✅ {filename} 添加依赖标准章节")
    else:
        print(f"  ⚠️  {filename} 未找到合适位置插入依赖标准")
    
    return content


def fix_code_blocks(content: str, filename: str) -> str:
    """修复代码块语言标识"""
    fixed_count = 0
    
    # 匹配无语言标识的代码块开始标记
    def replace_code_block(match):
        nonlocal fixed_count
        # 检查前一行内容判断代码块类型
        before_text = content[:match.start()].split('\n')[-5:]  # 前5行
        before_text_str = '\n'.join(before_text).lower()
        
        # 根据上下文判断代码块类型
        if 'python' in before_text_str or 'class ' in before_text_str or 'def ' in before_text_str:
            fixed_count += 1
            return '```python'
        elif 'json' in before_text_str or '{' in before_text_str:
            fixed_count += 1
            return '```json'
        elif 'sql' in before_text_str or 'table' in before_text_str or 'select' in before_text_str:
            fixed_count += 1
            return '```sql'
        elif 'mermaid' in before_text_str or 'sequencediagram' in before_text_str:
            fixed_count += 1
            return '```mermaid'
        elif '┌' in before_text_str or '│' in before_text_str or '└' in before_text_str:
            fixed_count += 1
            return '```text'
        else:
            # 默认使用 text
            fixed_count += 1
            return '```text'
    
    # 替换所有独立的 ``` (不在行尾有语言标识的)
    content = re.sub(r'^```$', replace_code_block, content, flags=re.MULTILINE)
    
    if fixed_count > 0:
        print(f"  ✅ {filename} 修复 {fixed_count} 个代码块")
    else:
        print(f"  ⏭️  {filename} 无需修复代码块")
    
    return content


def process_file(file_path: Path):
    """处理单个文件"""
    print(f"\n📝 处理文件: {file_path.name}")
    
    # 读取文件
    content = file_path.read_text(encoding='utf-8')
    
    # 应用修复
    content = add_yaml_front_matter(content, file_path.name)
    content = add_dependency_section(content, file_path.name)
    content = fix_code_blocks(content, file_path.name)
    
    # 写回文件
    file_path.write_text(content, encoding='utf-8')
    print(f"💾 保存完成")


def main():
    print("🔧 开始批量修复 inventory-management 模块文档格式\n")
    print(f"📁 文档目录: {DOCS_DIR}")
    print("=" * 60)
    
    # 要处理的文件列表
    files_to_process = [
        "design.md",
        "overview.md", 
        "README.md",
        "requirements.md",
        "implementation.md",
        "api-spec.md",
        "api-implementation.md"
    ]
    
    for filename in files_to_process:
        file_path = DOCS_DIR / filename
        if file_path.exists():
            process_file(file_path)
        else:
            print(f"\n⚠️  文件不存在: {filename}")
    
    print("\n" + "=" * 60)
    print("✅ 所有文档格式修复完成！")
    print("\n🔍 建议运行验证工具确认:")
    print("   .\\tools\\validate_standards.ps1 -Action full -DocPath \"docs/design/modules/inventory-management\"")


if __name__ == "__main__":
    main()
