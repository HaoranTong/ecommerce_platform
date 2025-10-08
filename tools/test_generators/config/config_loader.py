"""
配置加载器 - 测试生成器配置管理

职责:
- 加载test_generator_config.json配置文件
- 提供默认配置备用机制
- 配置验证和错误处理

版本: v1.0
"""
import json
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """配置加载器"""
    
    # 默认配置（备用）
    DEFAULT_CONFIG = {
        "project_structure": {
            "project_root": ".",
            "modules_path": "app/modules",
            "models_file": "models.py",
            "service_file": "service.py",
            "router_file": "router.py",
            "tests_path": "tests",
            "factories_path": "tests/factories"
        },
        "test_distributions": {
            "unit": 0.70,
            "integration": 0.20,
            "e2e": 0.06,
            "smoke": 0.02,
            "specialized": 0.02
        },
        "test_paths": {
            "unit_models": "tests/unit/test_models",
            "unit_services": "tests/unit/test_services",
            "unit_standalone": "tests/unit",
            "integration": "tests/integration",
            "e2e": "tests/e2e",
            "smoke": "tests/smoke",
            "performance": "tests/performance",
            "factories": "tests/factories"
        },
        "database_config": {
            "unit_test_fixture": "unit_test_db",
            "integration_test_fixture": "mysql_integration_db",
            "e2e_test_fixture": "api_client"
        }
    }
    
    def __init__(self, project_root: Path):
        """初始化配置加载器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        # 新位置
        config_path = Path(__file__).parent / "test_generator_config.json"
        
        # 兼容旧位置（如果新位置不存在）
        if not config_path.exists():
            config_path = self.project_root / "tools" / "test_generator_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                print(f"✅ 配置文件加载成功: {config_path}")
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            print("⚠️ 配置文件不存在，使用默认配置")
            self.config = self.DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键（支持点号分隔的嵌套键，如 "database_config.unit_test_fixture"）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            完整配置字典
        """
        return self.config.copy()
