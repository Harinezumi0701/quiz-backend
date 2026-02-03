# app/constants/permissions.py
"""
Permission constants for RBAC system.
Format: <namespace>::<action>
"""

# Permission Namespaces (match API endpoint prefixes)
PERMISSION_NAMESPACE_CATEGORIES = "categories"
PERMISSION_NAMESPACE_ROLES = "roles"
PERMISSION_NAMESPACE_USERS = "users"
PERMISSION_NAMESPACE_QUESTIONS = "questions"
PERMISSION_NAMESPACE_TESTS = "tests"
PERMISSION_NAMESPACE_ANSWERS = "answers"
PERMISSION_NAMESPACE_SUBMISSIONS = "submissions"
PERMISSION_NAMESPACE_NAMESPACES = "namespaces"
PERMISSION_NAMESPACE_DASHBOARD = "dashboard"
PERMISSION_NAMESPACE_USER_TESTS = "user_tests"
PERMISSION_NAMESPACE_PROFILE = "profile"

# Permission Actions
PERMISSION_ACTION_READ = "read"
PERMISSION_ACTION_CREATE = "create"
PERMISSION_ACTION_UPDATE = "update"
PERMISSION_ACTION_DELETE = "delete"
PERMISSION_ACTION_UPLOAD = "upload"

# Wildcard permissions
PERMISSION_WILDCARD_ALL = "*::*"

# Default permissions for new users (users without a role)
DEFAULT_USER_PERMISSIONS = [
    f"{PERMISSION_NAMESPACE_CATEGORIES}::read",
    f"{PERMISSION_NAMESPACE_TESTS}::read",
    f"{PERMISSION_NAMESPACE_QUESTIONS}::read",
    f"{PERMISSION_NAMESPACE_DASHBOARD}::read",
    f"{PERMISSION_NAMESPACE_USER_TESTS}::read",
    f"{PERMISSION_NAMESPACE_PROFILE}::read",
    f"{PERMISSION_NAMESPACE_PROFILE}::update",
]
