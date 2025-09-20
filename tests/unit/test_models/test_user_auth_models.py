"""
User_Auth 模块数据模型测试

测试类型: 单元测试 - 模型字段、约束、关系验证
数据策略: Mock对象，无数据库依赖
生成时间: 2025-09-20 23:28:32

符合标准: [CHECK:TEST-001] [CHECK:DEV-009]
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from decimal import Decimal

# 测试工厂导入
from tests.factories.test_data_factory import StandardTestDataFactory


class TestPermissionModel:
    """Permission模型测试类"""
    
    def setup_method(self):
        """测试准备"""
        self.mock_permission = Mock()
        
    def test_id_field_validation(self):
        """测试id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'id') == valid_data['id']
        
        # 测试字段类型
        field_value = getattr(instance, 'id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'id': invalid_value})
    def test_id_required_field(self):
        """测试id字段必填约束"""
        factory = PermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_name_field_validation(self):
        """测试name字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'name': f'unique_name_{datetime.now().microsecond}'}
        instance = factory(**valid_data)
        assert getattr(instance, 'name') == valid_data['name']
        
        # 测试字段类型
        field_value = getattr(instance, 'name')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段name类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'name': invalid_value})
    def test_name_unique_constraint(self):
        """测试name字段唯一约束"""
        factory = PermissionFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'name': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'name': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_name_required_field(self):
        """测试name字段必填约束"""
        factory = PermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'name': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('name', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'name': ''})
    def test_resource_field_validation(self):
        """测试resource字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'resource': 'test_resource'}
        instance = factory(**valid_data)
        assert getattr(instance, 'resource') == valid_data['resource']
        
        # 测试字段类型
        field_value = getattr(instance, 'resource')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段resource类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'resource': invalid_value})
    def test_resource_required_field(self):
        """测试resource字段必填约束"""
        factory = PermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'resource': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('resource', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'resource': ''})
    def test_action_field_validation(self):
        """测试action字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'action': 'test_action'}
        instance = factory(**valid_data)
        assert getattr(instance, 'action') == valid_data['action']
        
        # 测试字段类型
        field_value = getattr(instance, 'action')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段action类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'action': invalid_value})
    def test_action_required_field(self):
        """测试action字段必填约束"""
        factory = PermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'action': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('action', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'action': ''})
    def test_description_field_validation(self):
        """测试description字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'description': 'test_description'}
        instance = factory(**valid_data)
        assert getattr(instance, 'description') == valid_data['description']
        
        # 测试字段类型
        field_value = getattr(instance, 'description')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段description类型验证失败"
    def test_created_at_field_validation(self):
        """测试created_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'created_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'created_at') == valid_data['created_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'created_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段created_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'created_at': invalid_value})
    def test_created_at_required_field(self):
        """测试created_at字段必填约束"""
        factory = PermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'created_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_updated_at_field_validation(self):
        """测试updated_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = PermissionFactory
        
        # 测试有效值
        valid_data = {'updated_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'updated_at') == valid_data['updated_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'updated_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段updated_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'updated_at': invalid_value})
    def test_updated_at_required_field(self):
        """测试updated_at字段必填约束"""
        factory = PermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'updated_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_primary_key_constraints(self):
        """测试主键约束"""
        factory = PermissionFactory
        primary_keys = ['id']
        
        # 创建实例并验证主键
        instance = factory()
        for pk_field in primary_keys:
            pk_value = getattr(instance, pk_field)
            assert pk_value is not None, f"主键字段{pk_field}不能为空"
            
        # 测试主键唯一性（如果不是自增ID）
        if len(primary_keys) == 1 and primary_keys[0] != 'id':
            pk_field = primary_keys[0]
            instance1 = factory()
            pk_value = getattr(instance1, pk_field)
            
            # 尝试创建相同主键的实例应该失败
            with pytest.raises((IntegrityError, ValidationError)):
                instance2 = factory(**{pk_field: pk_value})
    def test_model_creation_with_required_fields(self):
        """测试模型创建 - 必填字段验证"""
        factory = PermissionFactory
        
        # 测试使用工厂创建完整实例
        instance = factory()
        assert instance is not None
        
        # 验证必填字段都有值
        required_fields = ['name', 'resource', 'action', 'created_at', 'updated_at']
        for field_name in required_fields:
            field_value = getattr(instance, field_name)
            assert field_value is not None, f"必填字段{field_name}不能为空"
            
        # 测试创建最小化实例（仅必填字段）
        minimal_data = {}
        minimal_data['name'] = 'test_name'
        minimal_data['resource'] = 'test_resource'
        minimal_data['action'] = 'test_action'
        
        if minimal_data:
            minimal_instance = factory(**minimal_data)
            assert minimal_instance is not None
    def test_model_string_representation(self):
        """测试模型字符串表示方法"""
        factory = PermissionFactory
        instance = factory()
        
        # 测试__str__方法
        str_repr = str(instance)
        assert str_repr is not None
        assert len(str_repr) > 0
        assert isinstance(str_repr, str)
        
        # 测试__repr__方法
        repr_str = repr(instance)
        assert repr_str is not None
        assert 'Permission' in repr_str or str(instance.id) in repr_str
    def test_role_permissions_relationship(self):
        """测试role_permissions关系 - one-to-many到RolePermission"""
        factory = PermissionFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'role_permissions'), f"关系属性role_permissions不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'role_permissions')
        # one-to-many关系应该是列表或集合  
        assert hasattr(relationship_value, '__iter__') or relationship_value is None
        
        # 测试关系数据访问
        # 测试集合关系的访问
        if relationship_value is not None:
            # 验证可以迭代
            try:
                list(relationship_value)
            except Exception as e:
                pytest.fail(f"关系role_permissions迭代失败: {e}")



class TestRoleModel:
    """Role模型测试类"""
    
    def setup_method(self):
        """测试准备"""
        self.mock_role = Mock()
        
    def test_id_field_validation(self):
        """测试id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = RoleFactory
        
        # 测试有效值
        valid_data = {'id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'id') == valid_data['id']
        
        # 测试字段类型
        field_value = getattr(instance, 'id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'id': invalid_value})
    def test_id_required_field(self):
        """测试id字段必填约束"""
        factory = RoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_name_field_validation(self):
        """测试name字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = RoleFactory
        
        # 测试有效值
        valid_data = {'name': f'unique_name_{datetime.now().microsecond}'}
        instance = factory(**valid_data)
        assert getattr(instance, 'name') == valid_data['name']
        
        # 测试字段类型
        field_value = getattr(instance, 'name')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段name类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'name': invalid_value})
    def test_name_unique_constraint(self):
        """测试name字段唯一约束"""
        factory = RoleFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'name': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'name': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_name_required_field(self):
        """测试name字段必填约束"""
        factory = RoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'name': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('name', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'name': ''})
    def test_description_field_validation(self):
        """测试description字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = RoleFactory
        
        # 测试有效值
        valid_data = {'description': 'test_description'}
        instance = factory(**valid_data)
        assert getattr(instance, 'description') == valid_data['description']
        
        # 测试字段类型
        field_value = getattr(instance, 'description')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段description类型验证失败"
    def test_level_field_validation(self):
        """测试level字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = RoleFactory
        
        # 测试有效值
        valid_data = {'level': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'level') == valid_data['level']
        
        # 测试字段类型
        field_value = getattr(instance, 'level')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段level类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'level': invalid_value})
    def test_level_required_field(self):
        """测试level字段必填约束"""
        factory = RoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'level': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_created_at_field_validation(self):
        """测试created_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = RoleFactory
        
        # 测试有效值
        valid_data = {'created_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'created_at') == valid_data['created_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'created_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段created_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'created_at': invalid_value})
    def test_created_at_required_field(self):
        """测试created_at字段必填约束"""
        factory = RoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'created_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_updated_at_field_validation(self):
        """测试updated_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = RoleFactory
        
        # 测试有效值
        valid_data = {'updated_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'updated_at') == valid_data['updated_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'updated_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段updated_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'updated_at': invalid_value})
    def test_updated_at_required_field(self):
        """测试updated_at字段必填约束"""
        factory = RoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'updated_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_primary_key_constraints(self):
        """测试主键约束"""
        factory = RoleFactory
        primary_keys = ['id']
        
        # 创建实例并验证主键
        instance = factory()
        for pk_field in primary_keys:
            pk_value = getattr(instance, pk_field)
            assert pk_value is not None, f"主键字段{pk_field}不能为空"
            
        # 测试主键唯一性（如果不是自增ID）
        if len(primary_keys) == 1 and primary_keys[0] != 'id':
            pk_field = primary_keys[0]
            instance1 = factory()
            pk_value = getattr(instance1, pk_field)
            
            # 尝试创建相同主键的实例应该失败
            with pytest.raises((IntegrityError, ValidationError)):
                instance2 = factory(**{pk_field: pk_value})
    def test_model_creation_with_required_fields(self):
        """测试模型创建 - 必填字段验证"""
        factory = RoleFactory
        
        # 测试使用工厂创建完整实例
        instance = factory()
        assert instance is not None
        
        # 验证必填字段都有值
        required_fields = ['name', 'level', 'created_at', 'updated_at']
        for field_name in required_fields:
            field_value = getattr(instance, field_name)
            assert field_value is not None, f"必填字段{field_name}不能为空"
            
        # 测试创建最小化实例（仅必填字段）
        minimal_data = {}
        minimal_data['name'] = 'test_name'
        minimal_data['level'] = 123
        
        if minimal_data:
            minimal_instance = factory(**minimal_data)
            assert minimal_instance is not None
    def test_model_string_representation(self):
        """测试模型字符串表示方法"""
        factory = RoleFactory
        instance = factory()
        
        # 测试__str__方法
        str_repr = str(instance)
        assert str_repr is not None
        assert len(str_repr) > 0
        assert isinstance(str_repr, str)
        
        # 测试__repr__方法
        repr_str = repr(instance)
        assert repr_str is not None
        assert 'Role' in repr_str or str(instance.id) in repr_str
    def test_role_permissions_relationship(self):
        """测试role_permissions关系 - one-to-many到RolePermission"""
        factory = RoleFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'role_permissions'), f"关系属性role_permissions不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'role_permissions')
        # one-to-many关系应该是列表或集合  
        assert hasattr(relationship_value, '__iter__') or relationship_value is None
        
        # 测试关系数据访问
        # 测试集合关系的访问
        if relationship_value is not None:
            # 验证可以迭代
            try:
                list(relationship_value)
            except Exception as e:
                pytest.fail(f"关系role_permissions迭代失败: {e}")
    def test_user_roles_relationship(self):
        """测试user_roles关系 - one-to-many到UserRole"""
        factory = RoleFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'user_roles'), f"关系属性user_roles不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'user_roles')
        # one-to-many关系应该是列表或集合  
        assert hasattr(relationship_value, '__iter__') or relationship_value is None
        
        # 测试关系数据访问
        # 测试集合关系的访问
        if relationship_value is not None:
            # 验证可以迭代
            try:
                list(relationship_value)
            except Exception as e:
                pytest.fail(f"关系user_roles迭代失败: {e}")



class TestRolePermissionModel:
    """RolePermission模型测试类"""
    
    def setup_method(self):
        """测试准备"""
        self.mock_rolepermission = Mock()
        
    def test_role_id_field_validation(self):
        """测试role_id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = RolePermissionFactory
        
        # 测试有效值
        valid_data = {'role_id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'role_id') == valid_data['role_id']
        
        # 测试字段类型
        field_value = getattr(instance, 'role_id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段role_id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'role_id': invalid_value})
    def test_role_id_required_field(self):
        """测试role_id字段必填约束"""
        factory = RolePermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'role_id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_role_id_foreign_key_constraint(self):
        """测试role_id外键约束 - 引用: roles.id"""
        # 测试有效外键关系
        roles_instance = RolesFactory() if 'Roles' in globals() else Mock(id=1)
        factory = RolePermissionFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'role_id': roles_instance.id if hasattr(roles_instance, 'id') else 1})
        assert getattr(valid_instance, 'role_id') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'role_id': 99999})  # 不存在的ID
    def test_permission_id_field_validation(self):
        """测试permission_id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = RolePermissionFactory
        
        # 测试有效值
        valid_data = {'permission_id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'permission_id') == valid_data['permission_id']
        
        # 测试字段类型
        field_value = getattr(instance, 'permission_id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段permission_id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'permission_id': invalid_value})
    def test_permission_id_required_field(self):
        """测试permission_id字段必填约束"""
        factory = RolePermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'permission_id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_permission_id_foreign_key_constraint(self):
        """测试permission_id外键约束 - 引用: permissions.id"""
        # 测试有效外键关系
        permissions_instance = PermissionsFactory() if 'Permissions' in globals() else Mock(id=1)
        factory = RolePermissionFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'permission_id': permissions_instance.id if hasattr(permissions_instance, 'id') else 1})
        assert getattr(valid_instance, 'permission_id') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'permission_id': 99999})  # 不存在的ID
    def test_granted_by_field_validation(self):
        """测试granted_by字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = RolePermissionFactory
        
        # 测试有效值
        valid_data = {'granted_by': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'granted_by') == valid_data['granted_by']
        
        # 测试字段类型
        field_value = getattr(instance, 'granted_by')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段granted_by类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'granted_by': invalid_value})
    def test_granted_by_foreign_key_constraint(self):
        """测试granted_by外键约束 - 引用: users.id"""
        # 测试有效外键关系
        users_instance = UsersFactory() if 'Users' in globals() else Mock(id=1)
        factory = RolePermissionFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'granted_by': users_instance.id if hasattr(users_instance, 'id') else 1})
        assert getattr(valid_instance, 'granted_by') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'granted_by': 99999})  # 不存在的ID
    def test_granted_at_field_validation(self):
        """测试granted_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = RolePermissionFactory
        
        # 测试有效值
        valid_data = {'granted_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'granted_at') == valid_data['granted_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'granted_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段granted_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'granted_at': invalid_value})
    def test_granted_at_required_field(self):
        """测试granted_at字段必填约束"""
        factory = RolePermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'granted_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_created_at_field_validation(self):
        """测试created_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = RolePermissionFactory
        
        # 测试有效值
        valid_data = {'created_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'created_at') == valid_data['created_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'created_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段created_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'created_at': invalid_value})
    def test_created_at_required_field(self):
        """测试created_at字段必填约束"""
        factory = RolePermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'created_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_updated_at_field_validation(self):
        """测试updated_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = RolePermissionFactory
        
        # 测试有效值
        valid_data = {'updated_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'updated_at') == valid_data['updated_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'updated_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段updated_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'updated_at': invalid_value})
    def test_updated_at_required_field(self):
        """测试updated_at字段必填约束"""
        factory = RolePermissionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'updated_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_primary_key_constraints(self):
        """测试主键约束"""
        factory = RolePermissionFactory
        primary_keys = ['role_id', 'permission_id']
        
        # 创建实例并验证主键
        instance = factory()
        for pk_field in primary_keys:
            pk_value = getattr(instance, pk_field)
            assert pk_value is not None, f"主键字段{pk_field}不能为空"
            
        # 测试主键唯一性（如果不是自增ID）
        if len(primary_keys) == 1 and primary_keys[0] != 'id':
            pk_field = primary_keys[0]
            instance1 = factory()
            pk_value = getattr(instance1, pk_field)
            
            # 尝试创建相同主键的实例应该失败
            with pytest.raises((IntegrityError, ValidationError)):
                instance2 = factory(**{pk_field: pk_value})
    def test_model_creation_with_required_fields(self):
        """测试模型创建 - 必填字段验证"""
        factory = RolePermissionFactory
        
        # 测试使用工厂创建完整实例
        instance = factory()
        assert instance is not None
        
        # 验证必填字段都有值
        required_fields = ['role_id', 'permission_id', 'granted_at', 'created_at', 'updated_at']
        for field_name in required_fields:
            field_value = getattr(instance, field_name)
            assert field_value is not None, f"必填字段{field_name}不能为空"
            
        # 测试创建最小化实例（仅必填字段）
        minimal_data = {}
        minimal_data['role_id'] = 123
        minimal_data['permission_id'] = 123
        
        if minimal_data:
            minimal_instance = factory(**minimal_data)
            assert minimal_instance is not None
    def test_model_string_representation(self):
        """测试模型字符串表示方法"""
        factory = RolePermissionFactory
        instance = factory()
        
        # 测试__str__方法
        str_repr = str(instance)
        assert str_repr is not None
        assert len(str_repr) > 0
        assert isinstance(str_repr, str)
        
        # 测试__repr__方法
        repr_str = repr(instance)
        assert repr_str is not None
        assert 'RolePermission' in repr_str or str(instance.id) in repr_str
    def test_role_relationship(self):
        """测试role关系 - one-to-one到Role"""
        factory = RolePermissionFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'role'), f"关系属性role不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'role')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')
    def test_permission_relationship(self):
        """测试permission关系 - one-to-one到Permission"""
        factory = RolePermissionFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'permission'), f"关系属性permission不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'permission')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')
    def test_granted_by_user_relationship(self):
        """测试granted_by_user关系 - one-to-one到User"""
        factory = RolePermissionFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'granted_by_user'), f"关系属性granted_by_user不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'granted_by_user')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')



class TestSessionModel:
    """Session模型测试类"""
    
    def setup_method(self):
        """测试准备"""
        self.mock_session = Mock()
        
    def test_id_field_validation(self):
        """测试id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'id') == valid_data['id']
        
        # 测试字段类型
        field_value = getattr(instance, 'id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'id': invalid_value})
    def test_id_required_field(self):
        """测试id字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_user_id_field_validation(self):
        """测试user_id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'user_id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'user_id') == valid_data['user_id']
        
        # 测试字段类型
        field_value = getattr(instance, 'user_id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段user_id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'user_id': invalid_value})
    def test_user_id_required_field(self):
        """测试user_id字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'user_id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_user_id_foreign_key_constraint(self):
        """测试user_id外键约束 - 引用: users.id"""
        # 测试有效外键关系
        users_instance = UsersFactory() if 'Users' in globals() else Mock(id=1)
        factory = SessionFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'user_id': users_instance.id if hasattr(users_instance, 'id') else 1})
        assert getattr(valid_instance, 'user_id') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'user_id': 99999})  # 不存在的ID
    def test_token_hash_field_validation(self):
        """测试token_hash字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'token_hash': f'unique_token_hash_{datetime.now().microsecond}'}
        instance = factory(**valid_data)
        assert getattr(instance, 'token_hash') == valid_data['token_hash']
        
        # 测试字段类型
        field_value = getattr(instance, 'token_hash')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段token_hash类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'token_hash': invalid_value})
    def test_token_hash_unique_constraint(self):
        """测试token_hash字段唯一约束"""
        factory = SessionFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'token_hash': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'token_hash': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_token_hash_required_field(self):
        """测试token_hash字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'token_hash': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('token_hash', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'token_hash': ''})
    def test_expires_at_field_validation(self):
        """测试expires_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'expires_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'expires_at') == valid_data['expires_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'expires_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段expires_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'expires_at': invalid_value})
    def test_expires_at_required_field(self):
        """测试expires_at字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'expires_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_last_accessed_at_field_validation(self):
        """测试last_accessed_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'last_accessed_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'last_accessed_at') == valid_data['last_accessed_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'last_accessed_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段last_accessed_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'last_accessed_at': invalid_value})
    def test_last_accessed_at_required_field(self):
        """测试last_accessed_at字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'last_accessed_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_is_active_field_validation(self):
        """测试is_active字段验证 - 类型: bool"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'is_active': True}
        instance = factory(**valid_data)
        assert getattr(instance, 'is_active') == valid_data['is_active']
        
        # 测试字段类型
        field_value = getattr(instance, 'is_active')
        expected_types = (bool)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段is_active类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_bool"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'is_active': invalid_value})
    def test_is_active_required_field(self):
        """测试is_active字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'is_active': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_ip_address_field_validation(self):
        """测试ip_address字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'ip_address': 'test_ip_address'}
        instance = factory(**valid_data)
        assert getattr(instance, 'ip_address') == valid_data['ip_address']
        
        # 测试字段类型
        field_value = getattr(instance, 'ip_address')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段ip_address类型验证失败"
    def test_user_agent_field_validation(self):
        """测试user_agent字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'user_agent': 'test_user_agent'}
        instance = factory(**valid_data)
        assert getattr(instance, 'user_agent') == valid_data['user_agent']
        
        # 测试字段类型
        field_value = getattr(instance, 'user_agent')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段user_agent类型验证失败"
    def test_created_at_field_validation(self):
        """测试created_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'created_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'created_at') == valid_data['created_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'created_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段created_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'created_at': invalid_value})
    def test_created_at_required_field(self):
        """测试created_at字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'created_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_updated_at_field_validation(self):
        """测试updated_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = SessionFactory
        
        # 测试有效值
        valid_data = {'updated_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'updated_at') == valid_data['updated_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'updated_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段updated_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'updated_at': invalid_value})
    def test_updated_at_required_field(self):
        """测试updated_at字段必填约束"""
        factory = SessionFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'updated_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_primary_key_constraints(self):
        """测试主键约束"""
        factory = SessionFactory
        primary_keys = ['id']
        
        # 创建实例并验证主键
        instance = factory()
        for pk_field in primary_keys:
            pk_value = getattr(instance, pk_field)
            assert pk_value is not None, f"主键字段{pk_field}不能为空"
            
        # 测试主键唯一性（如果不是自增ID）
        if len(primary_keys) == 1 and primary_keys[0] != 'id':
            pk_field = primary_keys[0]
            instance1 = factory()
            pk_value = getattr(instance1, pk_field)
            
            # 尝试创建相同主键的实例应该失败
            with pytest.raises((IntegrityError, ValidationError)):
                instance2 = factory(**{pk_field: pk_value})
    def test_model_creation_with_required_fields(self):
        """测试模型创建 - 必填字段验证"""
        factory = SessionFactory
        
        # 测试使用工厂创建完整实例
        instance = factory()
        assert instance is not None
        
        # 验证必填字段都有值
        required_fields = ['user_id', 'token_hash', 'expires_at', 'last_accessed_at', 'is_active', 'created_at', 'updated_at']
        for field_name in required_fields:
            field_value = getattr(instance, field_name)
            assert field_value is not None, f"必填字段{field_name}不能为空"
            
        # 测试创建最小化实例（仅必填字段）
        minimal_data = {}
        minimal_data['user_id'] = 123
        minimal_data['token_hash'] = 'test_token_hash'
        
        if minimal_data:
            minimal_instance = factory(**minimal_data)
            assert minimal_instance is not None
    def test_model_string_representation(self):
        """测试模型字符串表示方法"""
        factory = SessionFactory
        instance = factory()
        
        # 测试__str__方法
        str_repr = str(instance)
        assert str_repr is not None
        assert len(str_repr) > 0
        assert isinstance(str_repr, str)
        
        # 测试__repr__方法
        repr_str = repr(instance)
        assert repr_str is not None
        assert 'Session' in repr_str or str(instance.id) in repr_str
    def test_user_relationship(self):
        """测试user关系 - one-to-one到User"""
        factory = SessionFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'user'), f"关系属性user不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'user')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')



class TestUserModel:
    """User模型测试类"""
    
    def setup_method(self):
        """测试准备"""
        self.mock_user = Mock()
        
    def test_id_field_validation(self):
        """测试id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'id') == valid_data['id']
        
        # 测试字段类型
        field_value = getattr(instance, 'id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'id': invalid_value})
    def test_id_required_field(self):
        """测试id字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_username_field_validation(self):
        """测试username字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'username': f'unique_username_{datetime.now().microsecond}'}
        instance = factory(**valid_data)
        assert getattr(instance, 'username') == valid_data['username']
        
        # 测试字段类型
        field_value = getattr(instance, 'username')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段username类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'username': invalid_value})
    def test_username_unique_constraint(self):
        """测试username字段唯一约束"""
        factory = UserFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'username': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'username': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_username_required_field(self):
        """测试username字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'username': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('username', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'username': ''})
    def test_email_field_validation(self):
        """测试email字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'email': 'test@example.com'}
        instance = factory(**valid_data)
        assert getattr(instance, 'email') == valid_data['email']
        
        # 测试字段类型
        field_value = getattr(instance, 'email')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段email类型验证失败"
        
        # 测试无效值
        invalid_values = ['123', '""', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'email': invalid_value})
    def test_email_unique_constraint(self):
        """测试email字段唯一约束"""
        factory = UserFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'email': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'email': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_email_required_field(self):
        """测试email字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'email': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('email', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'email': ''})
    def test_password_hash_field_validation(self):
        """测试password_hash字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'password_hash': 'hashed_password_123'}
        instance = factory(**valid_data)
        assert getattr(instance, 'password_hash') == valid_data['password_hash']
        
        # 测试字段类型
        field_value = getattr(instance, 'password_hash')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段password_hash类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'password_hash': invalid_value})
    def test_password_hash_required_field(self):
        """测试password_hash字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'password_hash': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('password_hash', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'password_hash': ''})
    def test_is_active_field_validation(self):
        """测试is_active字段验证 - 类型: bool"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'is_active': True}
        instance = factory(**valid_data)
        assert getattr(instance, 'is_active') == valid_data['is_active']
        
        # 测试字段类型
        field_value = getattr(instance, 'is_active')
        expected_types = (bool)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段is_active类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_bool"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'is_active': invalid_value})
    def test_is_active_required_field(self):
        """测试is_active字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'is_active': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_status_field_validation(self):
        """测试status字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'status': 'test_status'}
        instance = factory(**valid_data)
        assert getattr(instance, 'status') == valid_data['status']
        
        # 测试字段类型
        field_value = getattr(instance, 'status')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段status类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'status': invalid_value})
    def test_status_required_field(self):
        """测试status字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'status': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('status', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'status': ''})
    def test_email_verified_field_validation(self):
        """测试email_verified字段验证 - 类型: bool"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'email_verified': True}
        instance = factory(**valid_data)
        assert getattr(instance, 'email_verified') == valid_data['email_verified']
        
        # 测试字段类型
        field_value = getattr(instance, 'email_verified')
        expected_types = (bool)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段email_verified类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_bool"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'email_verified': invalid_value})
    def test_email_verified_required_field(self):
        """测试email_verified字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'email_verified': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_phone_verified_field_validation(self):
        """测试phone_verified字段验证 - 类型: bool"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'phone_verified': True}
        instance = factory(**valid_data)
        assert getattr(instance, 'phone_verified') == valid_data['phone_verified']
        
        # 测试字段类型
        field_value = getattr(instance, 'phone_verified')
        expected_types = (bool)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段phone_verified类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_bool"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'phone_verified': invalid_value})
    def test_phone_verified_required_field(self):
        """测试phone_verified字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'phone_verified': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_two_factor_enabled_field_validation(self):
        """测试two_factor_enabled字段验证 - 类型: bool"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'two_factor_enabled': True}
        instance = factory(**valid_data)
        assert getattr(instance, 'two_factor_enabled') == valid_data['two_factor_enabled']
        
        # 测试字段类型
        field_value = getattr(instance, 'two_factor_enabled')
        expected_types = (bool)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段two_factor_enabled类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_bool"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'two_factor_enabled': invalid_value})
    def test_two_factor_enabled_required_field(self):
        """测试two_factor_enabled字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'two_factor_enabled': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_failed_login_attempts_field_validation(self):
        """测试failed_login_attempts字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'failed_login_attempts': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'failed_login_attempts') == valid_data['failed_login_attempts']
        
        # 测试字段类型
        field_value = getattr(instance, 'failed_login_attempts')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段failed_login_attempts类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'failed_login_attempts': invalid_value})
    def test_failed_login_attempts_required_field(self):
        """测试failed_login_attempts字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'failed_login_attempts': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_locked_until_field_validation(self):
        """测试locked_until字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'locked_until': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'locked_until') == valid_data['locked_until']
        
        # 测试字段类型
        field_value = getattr(instance, 'locked_until')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段locked_until类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'locked_until': invalid_value})
    def test_last_login_at_field_validation(self):
        """测试last_login_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'last_login_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'last_login_at') == valid_data['last_login_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'last_login_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段last_login_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'last_login_at': invalid_value})
    def test_phone_field_validation(self):
        """测试phone字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'phone': '13800138000'}
        instance = factory(**valid_data)
        assert getattr(instance, 'phone') == valid_data['phone']
        
        # 测试字段类型
        field_value = getattr(instance, 'phone')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段phone类型验证失败"
    def test_real_name_field_validation(self):
        """测试real_name字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'real_name': 'test_real_name'}
        instance = factory(**valid_data)
        assert getattr(instance, 'real_name') == valid_data['real_name']
        
        # 测试字段类型
        field_value = getattr(instance, 'real_name')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段real_name类型验证失败"
    def test_role_field_validation(self):
        """测试role字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'role': 'test_role'}
        instance = factory(**valid_data)
        assert getattr(instance, 'role') == valid_data['role']
        
        # 测试字段类型
        field_value = getattr(instance, 'role')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段role类型验证失败"
        
        # 测试无效值
        invalid_values = ['None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'role': invalid_value})
    def test_role_required_field(self):
        """测试role字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'role': None})
            
        # 测试空字符串（如果是字符串字段）
        if isinstance('role', str):
            with pytest.raises((ValueError, ValidationError)):
                instance = factory(**{'role': ''})
    def test_wx_openid_field_validation(self):
        """测试wx_openid字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'wx_openid': f'unique_wx_openid_{datetime.now().microsecond}'}
        instance = factory(**valid_data)
        assert getattr(instance, 'wx_openid') == valid_data['wx_openid']
        
        # 测试字段类型
        field_value = getattr(instance, 'wx_openid')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段wx_openid类型验证失败"
    def test_wx_openid_unique_constraint(self):
        """测试wx_openid字段唯一约束"""
        factory = UserFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'wx_openid': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'wx_openid': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_wx_unionid_field_validation(self):
        """测试wx_unionid字段验证 - 类型: str"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'wx_unionid': f'unique_wx_unionid_{datetime.now().microsecond}'}
        instance = factory(**valid_data)
        assert getattr(instance, 'wx_unionid') == valid_data['wx_unionid']
        
        # 测试字段类型
        field_value = getattr(instance, 'wx_unionid')
        expected_types = (str)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段wx_unionid类型验证失败"
    def test_wx_unionid_unique_constraint(self):
        """测试wx_unionid字段唯一约束"""
        factory = UserFactory
        
        # 创建第一个实例
        value = "unique_test_value_123"
        instance1 = factory(**{'wx_unionid': value})
        
        # 尝试创建相同值的第二个实例应该失败
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            instance2 = factory(**{'wx_unionid': value})
            # 如果使用数据库，需要提交来触发约束检查
            if hasattr(exc_info, 'session'):
                exc_info.session.commit()
                
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    def test_created_at_field_validation(self):
        """测试created_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'created_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'created_at') == valid_data['created_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'created_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段created_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'created_at': invalid_value})
    def test_created_at_required_field(self):
        """测试created_at字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'created_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_updated_at_field_validation(self):
        """测试updated_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'updated_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'updated_at') == valid_data['updated_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'updated_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段updated_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'updated_at': invalid_value})
    def test_updated_at_required_field(self):
        """测试updated_at字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'updated_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_is_deleted_field_validation(self):
        """测试is_deleted字段验证 - 类型: bool"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'is_deleted': True}
        instance = factory(**valid_data)
        assert getattr(instance, 'is_deleted') == valid_data['is_deleted']
        
        # 测试字段类型
        field_value = getattr(instance, 'is_deleted')
        expected_types = (bool)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段is_deleted类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_bool"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'is_deleted': invalid_value})
    def test_is_deleted_required_field(self):
        """测试is_deleted字段必填约束"""
        factory = UserFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'is_deleted': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_deleted_at_field_validation(self):
        """测试deleted_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserFactory
        
        # 测试有效值
        valid_data = {'deleted_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'deleted_at') == valid_data['deleted_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'deleted_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段deleted_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'deleted_at': invalid_value})
    def test_primary_key_constraints(self):
        """测试主键约束"""
        factory = UserFactory
        primary_keys = ['id']
        
        # 创建实例并验证主键
        instance = factory()
        for pk_field in primary_keys:
            pk_value = getattr(instance, pk_field)
            assert pk_value is not None, f"主键字段{pk_field}不能为空"
            
        # 测试主键唯一性（如果不是自增ID）
        if len(primary_keys) == 1 and primary_keys[0] != 'id':
            pk_field = primary_keys[0]
            instance1 = factory()
            pk_value = getattr(instance1, pk_field)
            
            # 尝试创建相同主键的实例应该失败
            with pytest.raises((IntegrityError, ValidationError)):
                instance2 = factory(**{pk_field: pk_value})
    def test_model_creation_with_required_fields(self):
        """测试模型创建 - 必填字段验证"""
        factory = UserFactory
        
        # 测试使用工厂创建完整实例
        instance = factory()
        assert instance is not None
        
        # 验证必填字段都有值
        required_fields = ['username', 'email', 'password_hash', 'is_active', 'status', 'email_verified', 'phone_verified', 'two_factor_enabled', 'failed_login_attempts', 'role', 'created_at', 'updated_at', 'is_deleted']
        for field_name in required_fields:
            field_value = getattr(instance, field_name)
            assert field_value is not None, f"必填字段{field_name}不能为空"
            
        # 测试创建最小化实例（仅必填字段）
        minimal_data = {}
        minimal_data['username'] = 'test_username'
        minimal_data['email'] = 'test_email'
        minimal_data['password_hash'] = 'test_password_hash'
        
        if minimal_data:
            minimal_instance = factory(**minimal_data)
            assert minimal_instance is not None
    def test_model_string_representation(self):
        """测试模型字符串表示方法"""
        factory = UserFactory
        instance = factory()
        
        # 测试__str__方法
        str_repr = str(instance)
        assert str_repr is not None
        assert len(str_repr) > 0
        assert isinstance(str_repr, str)
        
        # 测试__repr__方法
        repr_str = repr(instance)
        assert repr_str is not None
        assert 'User' in repr_str or str(instance.id) in repr_str
    def test_user_roles_relationship(self):
        """测试user_roles关系 - one-to-many到UserRole"""
        factory = UserFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'user_roles'), f"关系属性user_roles不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'user_roles')
        # one-to-many关系应该是列表或集合  
        assert hasattr(relationship_value, '__iter__') or relationship_value is None
        
        # 测试关系数据访问
        # 测试集合关系的访问
        if relationship_value is not None:
            # 验证可以迭代
            try:
                list(relationship_value)
            except Exception as e:
                pytest.fail(f"关系user_roles迭代失败: {e}")
    def test_sessions_relationship(self):
        """测试sessions关系 - one-to-many到Session"""
        factory = UserFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'sessions'), f"关系属性sessions不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'sessions')
        # one-to-many关系应该是列表或集合  
        assert hasattr(relationship_value, '__iter__') or relationship_value is None
        
        # 测试关系数据访问
        # 测试集合关系的访问
        if relationship_value is not None:
            # 验证可以迭代
            try:
                list(relationship_value)
            except Exception as e:
                pytest.fail(f"关系sessions迭代失败: {e}")



class TestUserRoleModel:
    """UserRole模型测试类"""
    
    def setup_method(self):
        """测试准备"""
        self.mock_userrole = Mock()
        
    def test_user_id_field_validation(self):
        """测试user_id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = UserRoleFactory
        
        # 测试有效值
        valid_data = {'user_id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'user_id') == valid_data['user_id']
        
        # 测试字段类型
        field_value = getattr(instance, 'user_id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段user_id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'user_id': invalid_value})
    def test_user_id_required_field(self):
        """测试user_id字段必填约束"""
        factory = UserRoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'user_id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_user_id_foreign_key_constraint(self):
        """测试user_id外键约束 - 引用: users.id"""
        # 测试有效外键关系
        users_instance = UsersFactory() if 'Users' in globals() else Mock(id=1)
        factory = UserRoleFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'user_id': users_instance.id if hasattr(users_instance, 'id') else 1})
        assert getattr(valid_instance, 'user_id') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'user_id': 99999})  # 不存在的ID
    def test_role_id_field_validation(self):
        """测试role_id字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = UserRoleFactory
        
        # 测试有效值
        valid_data = {'role_id': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'role_id') == valid_data['role_id']
        
        # 测试字段类型
        field_value = getattr(instance, 'role_id')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段role_id类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"', 'None']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'role_id': invalid_value})
    def test_role_id_required_field(self):
        """测试role_id字段必填约束"""
        factory = UserRoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'role_id': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_role_id_foreign_key_constraint(self):
        """测试role_id外键约束 - 引用: roles.id"""
        # 测试有效外键关系
        roles_instance = RolesFactory() if 'Roles' in globals() else Mock(id=1)
        factory = UserRoleFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'role_id': roles_instance.id if hasattr(roles_instance, 'id') else 1})
        assert getattr(valid_instance, 'role_id') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'role_id': 99999})  # 不存在的ID
    def test_assigned_by_field_validation(self):
        """测试assigned_by字段验证 - 类型: int"""
        # 使用智能工厂创建测试数据
        factory = UserRoleFactory
        
        # 测试有效值
        valid_data = {'assigned_by': 123}
        instance = factory(**valid_data)
        assert getattr(instance, 'assigned_by') == valid_data['assigned_by']
        
        # 测试字段类型
        field_value = getattr(instance, 'assigned_by')
        expected_types = (int)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段assigned_by类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_int"']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'assigned_by': invalid_value})
    def test_assigned_by_foreign_key_constraint(self):
        """测试assigned_by外键约束 - 引用: users.id"""
        # 测试有效外键关系
        users_instance = UsersFactory() if 'Users' in globals() else Mock(id=1)
        factory = UserRoleFactory
        
        # 使用有效外键创建实例
        valid_instance = factory(**{'assigned_by': users_instance.id if hasattr(users_instance, 'id') else 1})
        assert getattr(valid_instance, 'assigned_by') is not None
        
        # 测试无效外键应该失败
        with pytest.raises((IntegrityError, ValueError, ValidationError)):
            invalid_instance = factory(**{'assigned_by': 99999})  # 不存在的ID
    def test_assigned_at_field_validation(self):
        """测试assigned_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserRoleFactory
        
        # 测试有效值
        valid_data = {'assigned_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'assigned_at') == valid_data['assigned_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'assigned_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段assigned_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'assigned_at': invalid_value})
    def test_assigned_at_required_field(self):
        """测试assigned_at字段必填约束"""
        factory = UserRoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'assigned_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_created_at_field_validation(self):
        """测试created_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserRoleFactory
        
        # 测试有效值
        valid_data = {'created_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'created_at') == valid_data['created_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'created_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段created_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'created_at': invalid_value})
    def test_created_at_required_field(self):
        """测试created_at字段必填约束"""
        factory = UserRoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'created_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_updated_at_field_validation(self):
        """测试updated_at字段验证 - 类型: datetime"""
        # 使用智能工厂创建测试数据
        factory = UserRoleFactory
        
        # 测试有效值
        valid_data = {'updated_at': datetime.now()}
        instance = factory(**valid_data)
        assert getattr(instance, 'updated_at') == valid_data['updated_at']
        
        # 测试字段类型
        field_value = getattr(instance, 'updated_at')
        expected_types = (datetime)
        if field_value is not None:
            assert isinstance(field_value, expected_types), f"字段updated_at类型验证失败"
        
        # 测试无效值
        invalid_values = ['"invalid_datetime"', '123']
        for invalid_value in invalid_values:
            with pytest.raises((ValueError, TypeError, ValidationError)) as exc_info:
                factory(**{'updated_at': invalid_value})
    def test_updated_at_required_field(self):
        """测试updated_at字段必填约束"""
        factory = UserRoleFactory
        
        # 测试None值应该失败
        with pytest.raises((ValueError, TypeError, IntegrityError, ValidationError)):
            instance = factory(**{'updated_at': None})
            
        # 测试空字符串（如果是字符串字段）
        # 非字符串字段，跳过空字符串测试
    def test_primary_key_constraints(self):
        """测试主键约束"""
        factory = UserRoleFactory
        primary_keys = ['user_id', 'role_id']
        
        # 创建实例并验证主键
        instance = factory()
        for pk_field in primary_keys:
            pk_value = getattr(instance, pk_field)
            assert pk_value is not None, f"主键字段{pk_field}不能为空"
            
        # 测试主键唯一性（如果不是自增ID）
        if len(primary_keys) == 1 and primary_keys[0] != 'id':
            pk_field = primary_keys[0]
            instance1 = factory()
            pk_value = getattr(instance1, pk_field)
            
            # 尝试创建相同主键的实例应该失败
            with pytest.raises((IntegrityError, ValidationError)):
                instance2 = factory(**{pk_field: pk_value})
    def test_model_creation_with_required_fields(self):
        """测试模型创建 - 必填字段验证"""
        factory = UserRoleFactory
        
        # 测试使用工厂创建完整实例
        instance = factory()
        assert instance is not None
        
        # 验证必填字段都有值
        required_fields = ['user_id', 'role_id', 'assigned_at', 'created_at', 'updated_at']
        for field_name in required_fields:
            field_value = getattr(instance, field_name)
            assert field_value is not None, f"必填字段{field_name}不能为空"
            
        # 测试创建最小化实例（仅必填字段）
        minimal_data = {}
        minimal_data['user_id'] = 123
        minimal_data['role_id'] = 123
        
        if minimal_data:
            minimal_instance = factory(**minimal_data)
            assert minimal_instance is not None
    def test_model_string_representation(self):
        """测试模型字符串表示方法"""
        factory = UserRoleFactory
        instance = factory()
        
        # 测试__str__方法
        str_repr = str(instance)
        assert str_repr is not None
        assert len(str_repr) > 0
        assert isinstance(str_repr, str)
        
        # 测试__repr__方法
        repr_str = repr(instance)
        assert repr_str is not None
        assert 'UserRole' in repr_str or str(instance.id) in repr_str
    def test_user_relationship(self):
        """测试user关系 - one-to-one到User"""
        factory = UserRoleFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'user'), f"关系属性user不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'user')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')
    def test_role_relationship(self):
        """测试role关系 - one-to-one到Role"""
        factory = UserRoleFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'role'), f"关系属性role不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'role')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')
    def test_assigned_by_user_relationship(self):
        """测试assigned_by_user关系 - one-to-one到User"""
        factory = UserRoleFactory
        
        # 创建主实例
        instance = factory()
        
        # 验证关系属性存在
        assert hasattr(instance, 'assigned_by_user'), f"关系属性assigned_by_user不存在"
        
        # 测试关系类型
        relationship_value = getattr(instance, 'assigned_by_user')
        # many-to-one或one-to-one关系应该是单个对象或None
        assert relationship_value is None or hasattr(relationship_value, 'id')
        
        # 测试关系数据访问
        # 测试单对象关系的访问
        if relationship_value is not None:
            # 验证关系对象有基本属性
            assert hasattr(relationship_value, 'id') or hasattr(relationship_value, '__dict__')
