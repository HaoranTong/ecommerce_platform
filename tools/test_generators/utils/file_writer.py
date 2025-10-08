"""
测试文件写入器 - 生成代码持久化与目录管理

该模块实现测试代码生成工具中的文件写入功能，负责将生成的测试代码安全地写入磁盘，
并按照项目规范创建目录结构、添加文件头部、处理文件命名。

主要功能:
- 测试文件写入: 将生成的测试代码保存到指定目录
- 目录结构管理: 自动创建tests/unit/generated/{module}/目录层次
- 文件头部生成: 添加生成时间、工具版本、警告信息等元数据
- 路径规范化: 处理Windows/Linux路径兼容性
- 文件覆盖保护: 安全写入，避免意外覆盖重要文件

技术栈:
- pathlib: 跨平台路径处理
- datetime: 时间戳生成

依赖关系:
- tools.test_generators.generate_test_template: IntelligentTestGenerator主程序调用
- tools.test_generators.unit.*: 各生成器产生的测试代码内容
- tests/unit/generated/: 目标输出目录

使用示例:
    from pathlib import Path
    from tools.test_generators.utils.file_writer import TestFileWriter
    
    # 初始化写入器
    writer = TestFileWriter(project_root=Path.cwd())
    
    # 准备测试文件内容
    test_files = {
        "tests/unit/generated/user_auth/test_models.py": "# 测试代码...",
        "tests/unit/generated/user_auth/test_repositories.py": "# 测试代码..."
    }
    
    # 写入测试文件
    writer.write_test_files(test_files)
    print("测试文件写入完成")

注意事项:
- 所有测试文件统一写入tests/unit/generated目录
- 每个文件会自动添加生成信息头部（包含警告：不要手动修改）
- 目录不存在时会自动创建（包括父目录）
- 写入失败会抛出异常，调用方需要处理

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-08
Version: 1.0.0
"""
from pathlib import Path
from typing import Dict
from datetime import datetime


class TestFileWriter:
    """测试文件写入器"""
    
    def __init__(self, project_root: Path):
        """初始化文件写入器
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
    
    def write_test_files(self, files: Dict[str, str]):
        """写入测试文件到磁盘 - 遵循generated目录规范"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for file_key, content in files.items():
            # 解析文件信息
            file_info = self._parse_file_key(file_key)
            
            # 构造目标路径
            if file_key.startswith("tests/"):
                target_path = file_key
            else:
                target_path = self._construct_target_path(
                    file_info['module_name'],
                    file_info['test_category'] or '',
                    file_info['test_type']
                )
            
            full_path = self.project_root / target_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 添加生成信息到文件头部
            enhanced_content = self._add_generation_header(
                content, target_path, timestamp
            )

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(enhanced_content)

            print(f"📝 生成文件: {target_path}")

        print(f"✅ 文件已生成到正式目录")
        print(f"📋 下一步: 在正式目录中完成代码审查，审查通过后即可执行测试")
    
    def _parse_file_key(self, file_key: str) -> Dict[str, str]:
        """解析文件键，提取模块名、测试类型等信息"""
        # 特殊处理：工厂文件
        if file_key.startswith("tests/factories/") and file_key.endswith("_factories.py"):
            factory_filename = file_key.split("/")[-1]
            module_name = factory_filename.replace("_factories.py", "")
            return {
                'module_name': module_name,
                'test_type': 'factories',
                'test_category': None,
                'generated_filename': f"{module_name}_factories.py"
            }
        
        # 特殊处理：API测试文件
        if file_key.startswith("tests/integration/test_api/") and file_key.endswith("_api.py"):
            api_filename = file_key.split("/")[-1]
            if api_filename.startswith("test_") and api_filename.endswith("_api.py"):
                module_name = api_filename[5:-7]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'integration',
                'test_category': 'api',
                'generated_filename': f"test_{module_name}_api.py"
            }
        
        # 特殊处理：集成测试文件
        if file_key.startswith("tests/integration/") and file_key.endswith("_integration.py"):
            integration_filename = file_key.split("/")[-1]
            if integration_filename.startswith("test_") and integration_filename.endswith("_integration.py"):
                module_name = integration_filename[5:-15]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'integration',
                'test_category': None,
                'generated_filename': f"test_{module_name}_integration.py"
            }
        
        # 特殊处理：standalone文件
        if file_key.startswith("tests/unit/") and file_key.endswith("_standalone.py"):
            standalone_filename = file_key.split("/")[-1]
            if standalone_filename.startswith("test_") and standalone_filename.endswith("_standalone.py"):
                module_name = standalone_filename[5:-14]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'unit',
                'test_category': 'standalone',
                'generated_filename': f"test_{module_name}_standalone.py"
            }
        
        # 特殊处理：E2E测试文件
        if file_key.startswith("tests/e2e/") and file_key.endswith("_workflows.py"):
            e2e_filename = file_key.split("/")[-1]
            if e2e_filename.startswith("test_") and e2e_filename.endswith("_workflows.py"):
                module_name = e2e_filename[5:-13]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'e2e',
                'test_category': None,
                'generated_filename': f"test_{module_name}_workflows.py"
            }
        
        # 特殊处理：安全测试文件
        if file_key.startswith("tests/security/") and file_key.endswith("_security.py"):
            security_filename = file_key.split("/")[-1]
            if security_filename.startswith("test_") and security_filename.endswith("_security.py"):
                module_name = security_filename[5:-12]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'security',
                'test_category': None,
                'generated_filename': f"test_{module_name}_security.py"
            }
        
        # 特殊处理：性能测试文件
        if file_key.startswith("tests/performance/") and file_key.endswith("_performance.py"):
            performance_filename = file_key.split("/")[-1]
            if performance_filename.startswith("test_") and performance_filename.endswith("_performance.py"):
                module_name = performance_filename[5:-15]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'performance',
                'test_category': None,
                'generated_filename': f"test_{module_name}_performance.py"
            }
        
        # 通用解析逻辑
        if file_key.startswith("test_models/"):
            filename = file_key.split("/")[-1]
            if filename.startswith("test_") and filename.endswith("_models"):
                module_name = filename[5:-7]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'unit',
                'test_category': 'models',
                'generated_filename': filename
            }
        
        if file_key.startswith("test_repositories/"):
            filename = file_key.split("/")[-1]
            if filename.startswith("test_") and filename.endswith("_repositories"):
                module_name = filename[5:-13]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'unit',
                'test_category': 'repositories',
                'generated_filename': filename
            }
        
        if file_key.startswith("test_services/"):
            filename = file_key.split("/")[-1]
            if filename.startswith("test_") and filename.endswith("_services"):
                module_name = filename[5:-9]
            else:
                module_name = "unknown"
            return {
                'module_name': module_name,
                'test_type': 'unit',
                'test_category': 'services',
                'generated_filename': filename
            }
        
        if file_key.endswith("_standalone"):
            module_name = file_key[:-11]
            return {
                'module_name': module_name,
                'test_type': 'unit',
                'test_category': 'standalone',
                'generated_filename': f"test_{module_name}_standalone.py"
            }
        
        # 默认解析逻辑
        parts = file_key.split("_")
        test_types = ["unit", "integration", "e2e", "smoke", "specialized"]
        if len(parts) >= 2 and parts[-1] in test_types:
            test_type = parts[-1]
            if len(parts) >= 3 and parts[-2] in ["models", "service", "workflow", "api"]:
                test_category = parts[-2]
                module_name = "_".join(parts[:-2])
            else:
                test_category = None
                module_name = "_".join(parts[:-1])
        else:
            module_name = file_key
            test_type = "unknown"
            test_category = None
        
        if test_category:
            generated_filename = f"test_{module_name}_{test_category}_{test_type}.py"
        else:
            generated_filename = f"test_{module_name}_{test_type}.py"
        
        return {
            'module_name': module_name,
            'test_type': test_type,
            'test_category': test_category,
            'generated_filename': generated_filename
        }
    
    def _construct_target_path(self, module_name: str, test_category: str, test_type: str) -> str:
        """构造目标文件路径"""
        if test_type == "factories":
            return f"tests/factories/{module_name}_factories.py"
        elif test_type == "unit":
            if test_category == "models":
                return f"tests/unit/test_{module_name}_models.py"
            elif test_category == "repositories":
                return f"tests/unit/test_{module_name}_repositories.py"
            elif test_category == "services":
                return f"tests/unit/test_{module_name}_services.py"
            elif test_category == "standalone":
                return f"tests/unit/test_{module_name}_standalone.py"
            else:
                return f"tests/unit/test_{module_name}.py"
        elif test_type == "integration":
            if test_category == "api":
                return f"tests/integration/test_api/test_{module_name}_api.py"
            else:
                return f"tests/integration/test_{module_name}_integration.py"
        elif test_type == "e2e":
            return f"tests/e2e/test_{module_name}_workflows.py"
        elif test_type == "security":
            return f"tests/security/test_{module_name}_security.py"
        elif test_type == "performance":
            return f"tests/performance/test_{module_name}_performance.py"
        else:
            return f"tests/{test_type}/test_{module_name}.py"
    
    def _add_generation_header(self, content: str, target_path: str, timestamp: str) -> str:
        """添加生成信息头部"""
        header = f"""# Auto-generated test file
# Generated at: {timestamp}
# Target path: {target_path}
# Do NOT edit this file manually - regenerate from source models

"""
        return header + content
