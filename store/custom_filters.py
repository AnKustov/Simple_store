from django.contrib import admin
from django.utils.translation import gettext as _
from django.db.models import Q
from .models import *

class MultiCategoryFilter(admin.SimpleListFilter):
    title = _('Категории')
    parameter_name = 'categories'

    def lookups(self, request, model_admin):
        categories = Category.objects.all()
        return [(str(category.id), category.name) for category in categories]

    def queryset(self, request, queryset):
        selected_categories = request.GET.getlist('categories')
        if selected_categories:
            q_objects = Q()
            for category_id in selected_categories:
                q_objects |= Q(category__id=category_id)
            return queryset.filter(q_objects)
        return queryset    

