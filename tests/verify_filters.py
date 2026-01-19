
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from uuid import uuid4

# Add project root to python path
sys.path.append(os.getcwd())

from app.main import app
from app.api.dependencies.auth import get_current_user
from app.models.users import User
from app.db.session import get_db

class TestFilterMigration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Override dependencies
        def override_get_db():
            yield MagicMock()
            
        def override_get_current_user():
            user = MagicMock(spec=User)
            user.id = uuid4()
            return user
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        cls.client = TestClient(app)
        
        # Start patches
        cls.patcher1 = patch("app.services.permission_service.check_permission", return_value=True)
        cls.patcher2 = patch("app.services.permission_service.has_any_permission", return_value=True)
        cls.mock_check_permission = cls.patcher1.start()
        cls.mock_has_any = cls.patcher2.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher1.stop()
        cls.patcher2.stop()
        app.dependency_overrides.clear()
    
    @patch("app.services.user_service.list_users")
    def test_user_filters(self, mock_list_users):
        mock_list_users.return_value = ([], 0)
        
        # Test 1: Simple filter
        response = self.client.get("/api/v1/users?full_name=Test")
        if response.status_code != 200:
            print(f"User filter failed: {response.text}")
        self.assertEqual(response.status_code, 200)
        
        # Verify args passed to service
        call_args = mock_list_users.call_args
        _, kwargs = call_args
        
        self.assertIsNone(kwargs.get("search_key"))
        self.assertIsNone(kwargs.get("search_value"))
        self.assertEqual(kwargs.get("request_params").get("full_name"), "Test")
        
        # Test 2: Multiple filters
        response = self.client.get("/api/v1/users?full_name=Test&email=example")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_list_users.call_args
        _, kwargs = call_args
        self.assertEqual(kwargs.get("request_params").get("full_name"), "Test")
        self.assertEqual(kwargs.get("request_params").get("email"), "example")

        print("✓ User API filters verified")

    @patch("app.services.role_service.get_all_roles_with_search")
    def test_role_filters(self, mock_get_roles):
        mock_get_roles.return_value = ([], 0)
        
        response = self.client.get("/api/v1/roles?name=Admin")
        if response.status_code != 200:
            print(f"Role filter failed: {response.text}")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_roles.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        self.assertIsNone(kwargs.get("search_value"))
        self.assertEqual(kwargs.get("request_params").get("name"), "Admin")
        
        print("✓ Role API filters verified")

    @patch("app.services.permission_service.get_all_permissions")
    def test_permission_filters(self, mock_get_perms):
        mock_get_perms.return_value = ([], 0)
        
        response = self.client.get("/api/v1/permissions?permission=read")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_perms.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        self.assertEqual(kwargs.get("request_params").get("permission"), "read")
        
        print("✓ Permission API filters verified")

    @patch("app.services.namespace_service.get_all_namespaces_with_search")
    def test_namespace_filters(self, mock_get_ns):
        mock_get_ns.return_value = ([], 0)
        
        response = self.client.get("/api/v1/namespaces?name=ns1")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_ns.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        self.assertEqual(kwargs.get("request_params").get("name"), "ns1")
        
        print("✓ Namespace API filters verified")

    @patch("app.services.question_service.get_all_questions")
    def test_question_filters(self, mock_get_questions):
        mock_get_questions.return_value = ([], 0)
        
        # Test 1: Simple filter
        response = self.client.get("/api/v1/questions?content=What")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_questions.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        # Debugging
        if kwargs.get("request_params").get("content") != "What":
             print(f"DEBUG: request_params={kwargs.get('request_params')}")

        self.assertEqual(kwargs.get("request_params").get("content"), "What")
        
        # Test 2: OR condition (comma separated)
        response = self.client.get("/api/v1/questions?test=id1,id2")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_questions.call_args
        _, kwargs = call_args
        self.assertEqual(kwargs.get("request_params").get("test"), "id1,id2")
        
        print("✓ Question API filters verified")

    @patch("app.services.category_service.get_all_categories_with_search")
    def test_category_filters(self, mock_get_cats):
        mock_get_cats.return_value = ([], 0)
        
        response = self.client.get("/api/v1/categories?name=Math")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_cats.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        self.assertEqual(kwargs.get("request_params").get("name"), "Math")
        
        print("✓ Category API filters verified")
    
    @patch("app.services.answer_service.get_all_answers")
    def test_answer_filters(self, mock_get_answers):
        mock_get_answers.return_value = ([], 0)
        
        response = self.client.get("/api/v1/answers?content=Yes")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_answers.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        self.assertEqual(kwargs.get("request_params").get("content"), "Yes")
        
        print("✓ Answer API filters verified")

    @patch("app.services.category_service.get_all_tests")
    def test_test_filters(self, mock_get_tests):
        mock_get_tests.return_value = ([], 0)
        
        response = self.client.get("/api/v1/tests?name=Exam")
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_get_tests.call_args
        _, kwargs = call_args
        self.assertIsNone(kwargs.get("search_key"))
        self.assertEqual(kwargs.get("request_params").get("name"), "Exam")
        
        print("✓ Test API filters verified")

if __name__ == "__main__":
    unittest.main()
