from todos.models import Todo
import django_filters

class TodoFilter(django_filters.FilterSet):
    class Meta:
        model = Todo
        fields = {
            'title': ['exact', 'icontains', 'startswith'],
            'description': ['icontains', 'startswith'],
            'completed': ['exact']
        }