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

# Permission Actions
PERMISSION_ACTION_READ = "read"
PERMISSION_ACTION_CREATE = "create"
PERMISSION_ACTION_UPDATE = "update"
PERMISSION_ACTION_DELETE = "delete"

# Wildcard permissions
PERMISSION_WILDCARD_ALL = "*::*"
