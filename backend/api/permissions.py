from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его автору.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить только чтение для всех
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Разрешить изменение только автору
        return obj.author == request.user
