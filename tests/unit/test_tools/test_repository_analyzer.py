"""
RepositoryAnalyzer单元测试

测试Repository分析器是否正确解析各种Python参数模式，包括：
- 位置参数
- keyword-only参数 (Python 3.0+ PEP 3102)
- 默认参数
- 类型注解
- 混合参数模式

Created: 2025-10-15
Version: 1.0.0
"""
import ast
import pytest
from pathlib import Path
from tools.test_generators.utils.repository_analyzer import RepositoryAnalyzer


class TestRepositoryAnalyzer:
    """测试RepositoryAnalyzer的参数提取功能"""
    
    @pytest.fixture
    def analyzer(self):
        """创建RepositoryAnalyzer实例"""
        return RepositoryAnalyzer(project_root=Path.cwd())
    
    def test_extract_positional_only_parameters(self, analyzer):
        """测试提取纯位置参数"""
        code = """
class TestRepository:
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        method_node = class_node.body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        
        assert len(method_info.parameters) == 1
        assert method_info.parameters[0] == ('user_id', 'int')
    
    def test_extract_keyword_only_parameters(self, analyzer):
        """测试提取keyword-only参数（*, param）"""
        code = """
class TestRepository:
    def list_orders(self, *, user_id: Optional[int] = None, status: str = None) -> List[Order]:
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        method_node = class_node.body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        
        assert len(method_info.parameters) == 2
        assert ('user_id', 'Optional[int]') in method_info.parameters
        assert ('status', 'str') in method_info.parameters
    
    def test_extract_mixed_parameters(self, analyzer):
        """测试提取混合参数（位置 + keyword-only）"""
        code = """
class TestRepository:
    def get_order_items(self, order_id: int, *, user_id: Optional[int] = None) -> List[OrderItem]:
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        method_node = class_node.body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        
        assert len(method_info.parameters) == 2
        assert method_info.parameters[0] == ('order_id', 'int')
        assert method_info.parameters[1] == ('user_id', 'Optional[int]')
    
    def test_extract_multiple_positional_parameters(self, analyzer):
        """测试提取多个位置参数"""
        code = """
class TestRepository:
    def get_by_username_and_email(self, username: str, email: str) -> Optional[User]:
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        method_node = class_node.body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        
        assert len(method_info.parameters) == 2
        assert method_info.parameters[0] == ('username', 'str')
        assert method_info.parameters[1] == ('email', 'str')
    
    def test_skip_self_and_db_parameters(self, analyzer):
        """测试跳过self和db参数"""
        code = """
class TestRepository:
    def create(self, db: Session, entity: User) -> User:
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        method_node = class_node.body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        
        # 应该只有entity参数，self和db被过滤
        assert len(method_info.parameters) == 1
        assert method_info.parameters[0] == ('entity', 'User')
    
    def test_extract_parameters_without_type_hints(self, analyzer):
        """测试提取没有类型注解的参数"""
        code = """
class TestRepository:
    def find(self, query):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        method_node = class_node.body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        
        assert len(method_info.parameters) == 1
        assert method_info.parameters[0] == ('query', 'Any')
    
    def test_analyze_order_management_repository(self, analyzer):
        """集成测试：分析实际的订单模块Repository"""
        repositories = analyzer.analyze_module_repositories("order_management")
        
        assert 'OrderRepository' in repositories
        repo_info = repositories['OrderRepository']
        
        # 验证关键方法的参数提取
        method_dict = {m.name: m for m in repo_info.methods}
        
        # 测试get_order_items方法（混合参数）
        if 'get_order_items' in method_dict:
            method = method_dict['get_order_items']
            param_names = [p[0] for p in method.parameters]
            assert 'order_id' in param_names  # 位置参数
            assert 'user_id' in param_names   # keyword-only参数
        
        # 测试list_orders方法（全keyword-only参数）
        if 'list_orders' in method_dict:
            method = method_dict['list_orders']
            param_names = [p[0] for p in method.parameters]
            assert 'user_id' in param_names
            assert 'status' in param_names
            assert 'skip' in param_names
            assert 'limit' in param_names
    
    def test_analyze_user_auth_repository(self, analyzer):
        """回归测试：确保前3个模块仍然工作"""
        repositories = analyzer.analyze_module_repositories("user_auth")
        
        assert len(repositories) > 0
        
        # 验证所有Repository的方法都有参数信息
        for repo_name, repo_info in repositories.items():
            for method in repo_info.methods:
                assert method.parameters is not None
                assert isinstance(method.parameters, list)


class TestRepositoryAnalyzerMethodClassification:
    """测试Repository方法分类功能"""
    
    @pytest.fixture
    def analyzer(self):
        return RepositoryAnalyzer(project_root=Path.cwd())
    
    def test_classify_create_method(self, analyzer):
        """测试识别create方法"""
        code = """
class TestRepository:
    def create_user(self, user: User) -> User:
        pass
"""
        tree = ast.parse(code)
        method_node = tree.body[0].body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        assert method_info.method_type == 'create'
    
    def test_classify_read_method(self, analyzer):
        """测试识别read方法"""
        code = """
class TestRepository:
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
"""
        tree = ast.parse(code)
        method_node = tree.body[0].body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        assert method_info.method_type == 'read'
    
    def test_classify_list_method(self, analyzer):
        """测试识别list方法"""
        code = """
class TestRepository:
    def list_users(self) -> List[User]:
        pass
"""
        tree = ast.parse(code)
        method_node = tree.body[0].body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        assert method_info.method_type == 'list'
    
    def test_classify_update_method(self, analyzer):
        """测试识别update方法"""
        code = """
class TestRepository:
    def update_user(self, user: User) -> User:
        pass
"""
        tree = ast.parse(code)
        method_node = tree.body[0].body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        assert method_info.method_type == 'update'
    
    def test_classify_delete_method(self, analyzer):
        """测试识别delete方法"""
        code = """
class TestRepository:
    def delete_user(self, user_id: int) -> None:
        pass
"""
        tree = ast.parse(code)
        method_node = tree.body[0].body[0]
        
        method_info = analyzer._analyze_repository_method(method_node, "TestRepository", "test")
        assert method_info.method_type == 'delete'
