from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only allow authenticated users to proceed
        if not request.user.is_authenticated:
            return False

        # Allow read-only methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write methods (POST, PUT, PATCH, DELETE), check the owner
        return obj.owner == request.user