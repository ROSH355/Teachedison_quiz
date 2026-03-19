"""
Custom permission classes — reusable guards for any view.

Usage in any view:
    @permission_classes([IsAdminUser])
    or
    permission_classes = [IsAdminUser]
"""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to users with role='admin'.
    Different from Django's is_staff — this is our app-level role.
    """
    message = 'Access restricted to admin users only.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission.
    Allows access if the user owns the object OR is an admin.

    Usage: check in get_object() views
    """
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        # obj must have a 'user' or 'created_by' attribute
        owner = getattr(obj, 'user', None) or getattr(obj, 'created_by', None)
        return owner == request.user