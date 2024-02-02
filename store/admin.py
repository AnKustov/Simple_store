from decimal import Decimal, ROUND_DOWN
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget
import csv
from .models import *
from .forms import *
from .custom_filters import *
from orders.models import *
from statistic.models import *
from rangefilter.filter import DateRangeFilter
from import_export import resources


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget},
    }
    list_display = ('title', 'short_content', 'photo')

    def short_content(self, obj):
        return obj.content[:150] if len(obj.content) > 150 else obj.content
    short_content.short_description = 'Content'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget},
    }
    list_display = ('name', )
    list_filter = ('name', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget},
    }
    list_display = ('name', )
    list_filter = ('name', )

class ProductImageInline(admin.TabularInline): 
    model = ProductImage

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget},
        models.ManyToManyField: {'widget': FilteredSelectMultiple('Категории', is_stacked=False)},
    }
    inlines = [ProductImageInline]
    list_display = ('name', 'price', 'brand', 'category', 'subcategory')
    list_filter = ('name', 'brand', MultiCategoryFilter, 'subcategory')
    search_fields = ['name', 'price', 'brand__name', 'category__name', 'article']
    readonly_fields = ('article',)

    form = ProductForm

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        categories = Category.objects.all()
        extra_context['categories'] = categories

        return super().changelist_view(request, extra_context=extra_context)
    

    def export_products_to_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['Article', 'Name', 'Description', 'Price', 'Brand', 'Category', 'Subcategory', 'Image URL'])

        for product in queryset:
            writer.writerow([product.article, product.name, product.description, product.price, product.brand.name, product.category.name, product.subcategory.name, product.productimage_set.first().image.url])

        return response

    export_products_to_csv.short_description = 'Export selected products to CSV'
    
    actions = [export_products_to_csv]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget},
    }
    list_display = ('name', 'country')
    list_filter = ('name', 'country')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['new', 'order_number', 'user',  'status', 'processed_by', 'processed_at', 'total_cost', 'paid', 'created']
    readonly_fields = ['user', 'first_name', 'last_name','order_number', 'phone_number', 'city', 'address', 'delivery','email', 'processed_by', 'processed_at', 'total_cost', 'created']
    list_filter = ['order_number', 'status', 'paid', 'created']
    search_fields = ['order_number', 'user__username', 'phone_number']
    inlines = [OrderItemInline]

    
    def process_order(self, request, queryset):
        admin_user = request.user
        queryset.update(processed_by=admin_user, processed_at=timezone.now(), status='completed')
        self.message_user(request, f'Заказы были успешно обработаны администратором {admin_user}.')

    process_order.short_description = 'Обработать выбранные заказы'

    raw_id_fields = ['processed_by']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def format_decimal(self, value):
        formatted_value = Decimal(str(value)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        return format_html('<span style="white-space: nowrap;">{}</span>', formatted_value)
    
    def total_cost(self, obj):
        cost = obj.items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or Decimal('0')
        return self.format_decimal(cost)
    total_cost.short_description = 'Общая стоимость'


    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'order_number', 'user', 'status', 'processed_by', 'processed_at', 'total_cost', 'paid', 'created'
        ])

        for order in queryset:
            total_cost = order.items.aggregate(total=Sum(F('product__price') * F('quantity')))['total']
            total_cost = total_cost if total_cost is not None else 0
            writer.writerow([
                order.order_number, order.user, order.status, order.processed_by,
                order.processed_at, total_cost, order.paid, order.created
            ])

        return response
    
    actions = [export_to_csv, process_order]

@admin.register(SalesStatistics)
class SalesStatisticsAdmin(admin.ModelAdmin):
    list_display = ('product', 'total_quantity','total_sales', 'share_of_total')
    readonly_fields = ('product', 'total_quantity','total_sales', 'share_of_total')
    list_filter = (
        ('product__orderitem__order__created', DateRangeFilter),
    )

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_statistics.csv"'

        writer = csv.writer(response)
        writer.writerow(['Товар', 'Количество единиц', 'Сумма продаж', 'Доля продаж %'])

        for statistic in queryset:
            writer.writerow([statistic.product, statistic.total_quantity, statistic.total_sales, statistic.share_of_total])

        return response

    actions = [export_to_csv]


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'new')
    list_filter = ('name', 'new')
    readonly_fields = ['name', 'message', 'created_at']


admin.site.site_title = "Адмін-панель магазину"
admin.site.site_header = "Адмін-панель магазину"

