from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from core.models import User, SystemSetting
from core.services import UserService, AuthService, SettingsService

User = get_user_model()


class UserServiceTestCase(TestCase):
    """用户服务测试"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678',
            role='employee',
            is_admin=False
        )

    def test_create_user_empty_password(self):
        """测试创建用户时空密码应该报错"""
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='newuser',
                nickname='New User',
                email='new@example.com',
                password='',
                role='employee'
            )
        self.assertIn('密码不能为空', str(context.exception))

    def test_create_user_short_password(self):
        """测试创建用户时密码太短应该报错"""
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='newuser',
                nickname='New User',
                email='new@example.com',
                password='short',
                role='employee'
            )
        self.assertIn('10', str(context.exception))

    def test_create_user_duplicate_username(self):
        """测试创建重复用户名应该报错"""
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='testuser',
                nickname='Another User',
                email='another@example.com',
                password='password123456',
                role='employee'
            )
        self.assertIn('用户名已存在', str(context.exception))

    def test_create_user_duplicate_email(self):
        """测试创建重复邮箱应该报错"""
        User.objects.create_user(
            username='user1',
            password='password123456',
            email='test@example.com'
        )
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='user2',
                nickname='User 2',
                email='test@example.com',
                password='password123456',
                role='employee'
            )
        self.assertIn('邮箱已存在', str(context.exception))

    def test_get_user_by_nonexistent_id(self):
        """测试获取不存在的用户应返回 None"""
        result = UserService.get_user_by_id(99999)
        self.assertIsNone(result)

    def test_get_user_stats(self):
        """测试获取用户统计"""
        stats = UserService.get_user_stats()
        self.assertIn('total_users', stats)
        self.assertIn('active_users', stats)
        self.assertIn('manager_users', stats)
        self.assertIn('leader_users', stats)
        self.assertIn('employee_users', stats)


class AuthServiceTestCase(TestCase):
    """认证服务测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_login_max_failures_default(self):
        """测试获取登录失败最大次数默认值"""
        max_failures = AuthService.get_login_max_failures()
        self.assertEqual(max_failures, 5)

    def test_login_lock_minutes_default(self):
        """测试获取登录锁定时间默认值"""
        lock_minutes = AuthService.get_login_lock_minutes()
        self.assertEqual(lock_minutes, 30)

    def test_get_setting_with_none_value(self):
        """测试获取不存在的设置应返回默认值"""
        value = SettingsService.get_setting('nonexistent_key', 'default_value')
        self.assertEqual(value, 'default_value')


class SettingsServiceTestCase(TestCase):
    """设置服务测试"""

    def test_get_setting_existing(self):
        """测试获取已存在的设置"""
        SettingsService.save_setting('test_key', 'test_value')
        value = SettingsService.get_setting('test_key')
        self.assertEqual(value, 'test_value')

    def test_get_setting_with_default(self):
        """测试获取不存在的设置返回默认值"""
        value = SettingsService.get_setting('nonexistent', 'default')
        self.assertEqual(value, 'default')

    def test_save_setting_updates_cache(self):
        """测试保存设置会更新缓存"""
        SettingsService.save_setting('cache_test', 'value1')
        value1 = SettingsService.get_setting('cache_test')
        self.assertEqual(value1, 'value1')
        
        SettingsService.save_setting('cache_test', 'value2')
        value2 = SettingsService.get_setting('cache_test')
        self.assertEqual(value2, 'value2')


class LoginFormTestCase(TestCase):
    """登录表单测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_login_success(self):
        """测试成功登录"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'test12345678'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials(self):
        """测试凭据错误登录失败"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)


class APITestCase(TestCase):
    """API 测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='admin12345678',
            role='manager',
            is_admin=True
        )

    def test_api_time_current_requires_login(self):
        """测试时间 API 需要登录"""
        response = self.client.get('/api/time/current/')
        self.assertEqual(response.status_code, 302)

    def test_api_time_current_authenticated(self):
        """测试登录后可以访问时间 API"""
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/time/current/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('time', response.json())

    def test_api_regions_requires_login(self):
        """测试行政区划 API 需要登录"""
        response = self.client.get('/api/regions/provinces/')
        self.assertEqual(response.status_code, 302)

    def test_api_regions_authenticated(self):
        """测试登录后可以访问行政区划 API"""
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/regions/provinces/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
