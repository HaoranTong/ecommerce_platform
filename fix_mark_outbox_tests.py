"""批量修复mark_outbox_*测试的脚本"""
import re

file_path = "tests/unit/test_repositories/test_member_system_repositories.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 修复 mark_outbox_sending tests
# Pattern 1: minimal_fields和full_fields - 修复entity构造和调用
patterns = [
    # mark_outbox_sending_full_fields
    (
        r'(# 准备依赖实体: MemberProfile.*?memberprofile = MemberProfileFactory\.create.*?\n)        # 构造被测实体: MemberEventOutbox - 填充所有字段\n        entity = MemberEventOutbox\(\n            event_type="完整测试",\n            payload="完整测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            delivered_at=datetime\.now\(\),\n            retry_count=10,\n            last_error="完整测试",\n            member_id=memberprofile\.id\n        \)\n        \n        # 执行Repository方法\n        result = EventRepository\(unit_test_db\)\.mark_outbox_sending\(entity\)',
        r'''\1        # 构造被测实体: MemberEventOutbox - 填充所有字段
        entity = MemberEventOutbox(
            event_type="完整测试",
            payload={"test": "complete_data"},
            status="pending",
            available_at=datetime.now(),
            retry_count=0,
            member_id=memberprofile.id
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = EventRepository(unit_test_db).mark_outbox_sending(entity)
        unit_test_db.commit()'''
    ),
    # mark_outbox_sending_transaction_commit
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        \n        # 构造被测实体: MemberEventOutbox - 填充所有字段\n        entity = MemberEventOutbox\(\n            event_type="完整测试",\n            payload="完整测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            delivered_at=datetime\.now\(\),\n            retry_count=10,\n            last_error="完整测试",\n            member_id=memberprofile\.id\n        \)\n        \n        result = EventRepository\(unit_test_db\)\.mark_outbox_sending\(entity\)',
        r'''\1        
        # 构造被测实体: MemberEventOutbox - 填充所有字段
        entity = MemberEventOutbox(
            event_type="完整测试",
            payload={"test": "data"},
            status="pending",
            available_at=datetime.now(),
            retry_count=0,
            member_id=memberprofile.id
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        result = EventRepository(unit_test_db).mark_outbox_sending(entity)
        unit_test_db.commit()'''
    ),
    # mark_outbox_sent_minimal_fields
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        # 构造被测实体: MemberEventOutbox - 只填必填字段\n        entity = MemberEventOutbox\(\n            event_type="测试",\n            payload="测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            retry_count=10\n        \)\n        \n        # 执行Repository方法\n        result = EventRepository\(unit_test_db\)\.mark_outbox_sent\(entity\)',
        r'''\1        # 构造被测实体: MemberEventOutbox - 只填必填字段
        entity = MemberEventOutbox(
            event_type="测试",
            payload={"test": "data"},
            status="sending",
            available_at=datetime.now(),
            retry_count=0
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = EventRepository(unit_test_db).mark_outbox_sent(entity)
        unit_test_db.commit()'''
    ),
    # mark_outbox_sent_full_fields
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        \n        # 构造被测实体: MemberEventOutbox - 填充所有字段\n        entity = MemberEventOutbox\(\n            event_type="完整测试",\n            payload="完整测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            delivered_at=datetime\.now\(\),\n            retry_count=10,\n            last_error="完整测试",\n            member_id=memberprofile\.id\n        \)\n        \n        # 执行Repository方法\n        result = EventRepository\(unit_test_db\)\.mark_outbox_sent\(entity\)',
        r'''\1        
        # 构造被测实体: MemberEventOutbox - 填充所有字段
        entity = MemberEventOutbox(
            event_type="完整测试",
            payload={"test": "complete_data"},
            status="sending",
            available_at=datetime.now(),
            retry_count=0,
            member_id=memberprofile.id
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = EventRepository(unit_test_db).mark_outbox_sent(entity)
        unit_test_db.commit()'''
    ),
    # mark_outbox_sent_transaction_commit
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        \n        # 构造被测实体: MemberEventOutbox - 填充所有字段\n        entity = MemberEventOutbox\(\n            event_type="完整测试",\n            payload="完整测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            delivered_at=datetime\.now\(\),\n            retry_count=10,\n            last_error="完整测试",\n            member_id=memberprofile\.id\n        \)\n        \n        result = EventRepository\(unit_test_db\)\.mark_outbox_sent\(entity\)',
        r'''\1        
        # 构造被测实体: MemberEventOutbox - 填充所有字段
        entity = MemberEventOutbox(
            event_type="完整测试",
            payload={"test": "data"},
            status="sending",
            available_at=datetime.now(),
            retry_count=0,
            member_id=memberprofile.id
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        result = EventRepository(unit_test_db).mark_outbox_sent(entity)
        unit_test_db.commit()'''
    ),
    # mark_outbox_retry_minimal_fields
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        # 构造被测实体: MemberEventOutbox - 只填必填字段\n        entity = MemberEventOutbox\(\n            event_type="测试",\n            payload="测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            retry_count=10\n        \)\n        \n        # 执行Repository方法\n        result = EventRepository\(unit_test_db\)\.mark_outbox_retry\(entity\)',
        r'''\1        # 构造被测实体: MemberEventOutbox - 只填必填字段
        entity = MemberEventOutbox(
            event_type="测试",
            payload={"test": "data"},
            status="pending",
            available_at=datetime.now(),
            retry_count=0
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = EventRepository(unit_test_db).mark_outbox_retry(entity, error="测试错误")
        unit_test_db.commit()'''
    ),
    # mark_outbox_retry_full_fields
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        \n        # 构造被测实体: MemberEventOutbox - 填充所有字段\n        entity = MemberEventOutbox\(\n            event_type="完整测试",\n            payload="完整测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            delivered_at=datetime\.now\(\),\n            retry_count=10,\n            last_error="完整测试",\n            member_id=memberprofile\.id\n        \)\n        \n        # 执行Repository方法\n        result = EventRepository\(unit_test_db\)\.mark_outbox_retry\(entity\)',
        r'''\1        
        # 构造被测实体: MemberEventOutbox - 填充所有字段
        entity = MemberEventOutbox(
            event_type="完整测试",
            payload={"test": "complete_data"},
            status="pending",
            available_at=datetime.now(),
            retry_count=2,
            last_error="之前的错误",
            member_id=memberprofile.id
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = EventRepository(unit_test_db).mark_outbox_retry(entity, error="新的错误信息")
        unit_test_db.commit()'''
    ),
    # mark_outbox_retry_transaction_commit
    (
        r'(memberprofile = MemberProfileFactory\.create.*?\n)        \n        # 构造被测实体: MemberEventOutbox - 填充所有字段\n        entity = MemberEventOutbox\(\n            event_type="完整测试",\n            payload="完整测试",\n            status="active",\n            available_at=datetime\.now\(\),\n            delivered_at=datetime\.now\(\),\n            retry_count=10,\n            last_error="完整测试",\n            member_id=memberprofile\.id\n        \)\n        \n        result = EventRepository\(unit_test_db\)\.mark_outbox_retry\(entity\)',
        r'''\1        
        # 构造被测实体: MemberEventOutbox - 填充所有字段
        entity = MemberEventOutbox(
            event_type="完整测试",
            payload={"test": "data"},
            status="pending",
            available_at=datetime.now(),
            retry_count=0,
            member_id=memberprofile.id
        )
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        result = EventRepository(unit_test_db).mark_outbox_retry(entity, error="错误信息")
        unit_test_db.commit()'''
    ),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 批量修复完成")
