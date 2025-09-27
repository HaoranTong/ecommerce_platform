#!/usr/bin/env python3
"""
AI协作标准L0区段同步脚本
====================================
用途：
  - 自动从ai-collaboration-standards.md中提取<!-- L0-START -->与<!-- L0-END -->之间的内容
  - 同步生成ai-collaboration-standards-l0.md，供AI高效加载L0上下文
使用场景：
  - 每次更新AI协作标准文档后，运行本脚本同步L0区段
  - AI启动任务时只需加载L0文档即可
用法：
  python tools/sync_ai_collab_l0_section.py
"""
import re
import sys

SRC = 'docs/standards/ai-collaboration-standards.md'
DST = 'docs/standards/ai-collaboration-standards-l0.md'

try:
    with open(SRC, encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f'读取源文件失败: {e}')
    sys.exit(1)

match = re.search(r'<!-- L0-START -->(.*?)<!-- L0-END -->', content, re.DOTALL)
if not match:
    print('未找到L0区段标记，请检查源文件格式。')
    sys.exit(2)

l0_content = match.group(1).strip()

header = (
    '# AI协作开发标准L0上下文（自动同步生成）\n\n'
    '> 本文档由tools/sync_ai_collab_l0_section.py自动生成。\n'
    '> 仅包含AI启动任务时需加载的核心流程、关键规则、目录与主线。\n'
    '> 修改请在ai-collaboration-standards.md的<!-- L0-START -->与<!-- L0-END -->区段内进行。\n\n'
    '<!-- 以下内容自动同步自ai-collaboration-standards.md L0区段 -->\n\n'
)

with open(DST, 'w', encoding='utf-8') as f:
    f.write(header)
    f.write(l0_content)
    f.write('\n')

print(f'L0区段已同步到 {DST}')
