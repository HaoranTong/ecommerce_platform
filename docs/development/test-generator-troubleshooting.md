# 智能测试生成工具故障排查手册

## 🚨 紧急故障处理

### 严重问题快速修复

#### ❌ 问题：工具完全无法运行
```bash
# 立即检查
python --version  # 确保Python 3.8+
python scripts/generate_test_template.py --help  # 检查工具可用性

# 快速修复
pip install -r requirements.txt  # 重装依赖
python -c "import sys; print(sys.path)"  # 检查路径
```

#### ❌ 问题：生成的所有测试都失败
```bash
# 紧急诊断
python scripts/e2e_test_verification.py  # 端到端验证
cat docs/analysis/*validation_report*.md | head -20  # 查看错误

# 应急方案
cp tests/conftest_e2e.py tests/conftest.py  # 使用简化conftest
python -m pytest tests/factories/ -v  # 仅测试工厂类
```

## 🔧 分类故障排查

### 1. 生成阶段问题

#### 问题1.1: ModuleNotFoundError
```bash
错误: ModuleNotFoundError: No module named 'app.modules.user_auth.models'

诊断:
python -c "import app.modules.user_auth.models"

解决方案:
# 1. 检查模块路径
ls -la app/modules/user_auth/models.py

# 2. 检查__init__.py文件
touch app/__init__.py
touch app/modules/__init__.py  
touch app/modules/user_auth/__init__.py

# 3. 验证PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 问题1.2: SQLAlchemy表重定义错误
```bash
错误: Table 'users' is already defined for this MetaData instance

解决方案:
# 1. 清理Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 2. 重启Python进程
python scripts/generate_test_template.py user_auth --type unit

# 3. 如果持续出现，添加extend_existing=True
# 在models.py中：
__table_args__ = {'extend_existing': True}
```

#### 问题1.3: AST解析失败
```bash
错误: SyntaxError during AST parsing

诊断:
python -m py_compile app/modules/user_auth/models.py

解决方案:
# 1. 检查模型文件语法
python -c "import ast; ast.parse(open('app/modules/user_auth/models.py').read())"

# 2. 查找特殊字符或编码问题
file app/modules/user_auth/models.py  # 检查编码
hexdump -C app/modules/user_auth/models.py | head  # 查看BOM
```

### 2. 验证阶段问题

#### 问题2.1: pytest收集失败
```bash
错误: ImportError while loading conftest

解决方案:
# 1. 创建最小conftest
cat > tests/conftest_minimal.py << 'EOF'
import pytest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

@pytest.fixture
def mock_db():
    return None
EOF

# 2. 使用最小conftest测试
pytest --confcutdir=tests/conftest_minimal.py tests/factories/ --collect-only

# 3. 逐步添加依赖
# 确定具体缺失的依赖包
```

#### 问题2.2: Factory导入错误
```bash  
错误: ImportError: cannot import name 'UserFactory'

诊断:
python -c "exec(open('tests/factories/user_auth_factories.py').read())"

解决方案:
# 1. 检查工厂文件语法
python -m py_compile tests/factories/user_auth_factories.py

# 2. 检查导入依赖
python -c "import factory; print('Factory Boy可用')"
python -c "from app.modules.user_auth.models import User; print('模型导入成功')"

# 3. 手动测试工厂创建
python -c "
from tests.factories.user_auth_factories import UserFactory
user = UserFactory.build()  # build而非create避免数据库
print('工厂测试成功')
"
```

#### 问题2.3: 循环导入问题
```bash
错误: RecursionError: maximum recursion depth exceeded

解决方案:
# 1. 检查循环依赖
grep -r "SubFactory" tests/factories/

# 2. 手动修复循环依赖
# 编辑工厂文件，将SubFactory改为LazyFunction
user_id = factory.LazyFunction(lambda: 1)  # 而非 user=SubFactory(UserFactory)

# 3. 重新生成工厂（工具已优化循环依赖检测）
python scripts/generate_test_template.py user_auth --type unit
```

### 3. 执行阶段问题

#### 问题3.1: 数据库连接失败
```bash
错误: sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table

解决方案:
# 1. 检查测试数据库设置
python -c "
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
print('SQLite内存数据库可用')
"

# 2. 创建表结构
python -c "
from app.shared.models import Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
print('表创建成功')
"

# 3. 使用Mock数据库
# 在测试中使用Mock替代真实数据库访问
```

#### 问题3.2: 外键约束失败
```bash
错误: sqlite3.IntegrityError: FOREIGN KEY constraint failed

解决方案:
# 1. 启用SQLite外键约束
# 在conftest.py中添加：
@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    return engine

# 2. 调整工厂创建顺序
# 先创建被引用对象
user = UserFactory()
session = SessionFactory(user_id=user.id)

# 3. 使用工厂SubFactory自动处理
session = SessionFactory(user=UserFactory())
```

#### 问题3.3: 权限或文件系统问题
```bash
错误: PermissionError: [Errno 13] Permission denied

解决方案:
# 1. 检查文件权限
ls -la tests/factories/
chmod 755 tests/factories/

# 2. 检查磁盘空间
df -h

# 3. 使用临时目录
export TMPDIR=/tmp
python scripts/generate_test_template.py user_auth --type unit
```

## 📊 诊断工具和脚本

### 自动诊断脚本
```bash
#!/bin/bash
# 保存为 scripts/diagnose.sh

echo "🔍 开始智能测试工具诊断..."

# 基础环境检查
echo "📋 环境检查:"
python --version
pip list | grep -E "(pytest|factory-boy|sqlalchemy)"

# 项目结构检查  
echo "📁 项目结构检查:"
ls -la app/modules/user_auth/
ls -la tests/

# 模型导入测试
echo "🔧 模型导入测试:"
python -c "import app.modules.user_auth.models; print('✅ 模型导入成功')" 2>&1

# 工厂语法检查
echo "🏭 工厂语法检查:"
if [ -f "tests/factories/user_auth_factories.py" ]; then
    python -m py_compile tests/factories/user_auth_factories.py && echo "✅ 工厂语法正确"
else
    echo "⚠️ 工厂文件不存在"
fi

# 端到端快速验证
echo "🚀 端到端快速验证:"
timeout 30 python scripts/e2e_test_verification.py 2>&1 | head -10

echo "📊 诊断完成"
```

### 问题分类自动识别
```python
# 保存为 scripts/issue_classifier.py
import re
import sys
from pathlib import Path

def classify_error(error_msg):
    """自动分类错误类型"""
    error_patterns = {
        'import': [r'ModuleNotFoundError', r'ImportError', r'cannot import'],
        'syntax': [r'SyntaxError', r'IndentationError', r'invalid syntax'],
        'database': [r'OperationalError', r'IntegrityError', r'no such table'],
        'factory': [r'Factory.*Error', r'AttributeError.*Factory'],
        'pytest': [r'pytest.*Error', r'collection failed', r'conftest'],
        'permission': [r'PermissionError', r'Access.*denied', r'Permission denied']
    }
    
    for category, patterns in error_patterns.items():
        for pattern in patterns:
            if re.search(pattern, error_msg, re.IGNORECASE):
                return category
    return 'unknown'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        error_msg = sys.argv[1]
        category = classify_error(error_msg)
        print(f"错误类型: {category}")
        
        # 提供针对性建议
        suggestions = {
            'import': "检查模块路径和__init__.py文件",
            'syntax': "运行python -m py_compile检查语法",
            'database': "检查数据库连接和表结构",
            'factory': "验证Factory Boy配置和依赖",
            'pytest': "检查conftest.py和测试环境",
            'permission': "检查文件权限和磁盘空间"
        }
        
        print(f"建议: {suggestions.get(category, '查看完整故障排查手册')}")
```

## 🔍 深度诊断流程

### 完整诊断checklist

#### 第1步：环境验证
- [ ] Python版本 ≥ 3.8
- [ ] 必要依赖包已安装 (pytest, factory-boy, sqlalchemy)
- [ ] 项目路径正确设置
- [ ] __init__.py文件存在

#### 第2步：代码结构验证  
- [ ] 模型文件存在且语法正确
- [ ] SQLAlchemy模型定义规范
- [ ] 没有循环导入问题
- [ ] 编码格式正确 (UTF-8)

#### 第3步：生成过程验证
- [ ] 工具运行无异常
- [ ] 预期文件正确生成
- [ ] 生成代码语法正确
- [ ] 依赖导入可正常解析

#### 第4步：执行环境验证
- [ ] 测试数据库可连接
- [ ] 外键约束正确配置
- [ ] 权限和磁盘空间充足
- [ ] conftest.py配置正确

#### 第5步：端到端验证
- [ ] 完整工具链可正常运行
- [ ] 验证报告生成成功
- [ ] 质量评分达到预期
- [ ] 所有关键检查点通过

## 🆘 应急处理预案

### 生产环境问题
```bash
# 1. 立即回滚到已知工作版本
git checkout 上一个稳定版本

# 2. 使用简化模式生成
python scripts/generate_test_template.py user_auth --type unit --dry-run

# 3. 手动验证关键工厂类
python -c "from tests.factories.user_auth_factories import UserFactory; print(UserFactory.build())"
```

### 数据损坏恢复
```bash
# 1. 备份当前状态
cp -r tests/ tests_backup_$(date +%Y%m%d_%H%M%S)/

# 2. 清理损坏文件
rm -rf tests/factories/*_factories.py
rm -rf tests/unit/test_models/

# 3. 重新生成
python scripts/generate_test_template.py user_auth --type unit
```

### 依赖冲突解决
```bash
# 1. 创建隔离环境
python -m venv emergency_env
source emergency_env/bin/activate

# 2. 安装最小依赖
pip install pytest==7.4.2 factory-boy==3.3.0 sqlalchemy==2.0.21

# 3. 重新测试
python scripts/generate_test_template.py user_auth --type unit
```

## 📞 获取帮助

### 自助资源
1. **统一工具手册**: `docs/development/scripts-usage-manual.md`（第4.8章节 - generate_test_template.py）  
3. **验证报告**: `docs/analysis/*validation_report*.md`
4. **工作日志**: `docs/status/current-work-status.md`

### 问题报告格式
```markdown
## 问题描述
简要描述问题现象

## 环境信息
- Python版本: 
- 操作系统:
- 项目模块:

## 重现步骤
1. 运行命令: 
2. 预期结果:
3. 实际结果:

## 错误信息
粘贴完整的错误消息和堆栈跟踪

## 已尝试的解决方案
列出已经尝试的修复方法
```

### 检查点遵循
确保问题报告和解决方案符合以下标准：
- [CHECK:TEST-008] 测试质量验证标准
- [CHECK:DEV-009] 代码质量标准  
- [CHECK:DOC-001] 文档标准

---
*故障排查手册 v2.0 | 更新: 2025-09-20 | 遵循: [CHECK:DOC-001] [CHECK:DEV-009]*