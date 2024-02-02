from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from store.models import *
from statistic.models import *


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='order_history', verbose_name="Покупатель")
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20,verbose_name="Номер телефона")
    address = models.CharField(max_length=150, verbose_name="Адрес")
    order_number = models.PositiveIntegerField(unique=True, verbose_name="Номер заказа", default=0)
    city = models.CharField(max_length=50, verbose_name="Город")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    paid = models.BooleanField(default=False, verbose_name="Оплачено")
    status = models.CharField(max_length=50, choices=[('pending', 'Ожидание'), ('completed', 'Завершено')], default='Ожидание')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_orders', verbose_name="Обработал")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата обработки")
    new = models.BooleanField(default=True, verbose_name="Новый заказ")
    delivery = models.CharField(max_length=150 ,null=True, verbose_name="Способ доставки")

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-order_number').first()
            if last_order:
                self.order_number = last_order.order_number + 1
            else:
                self.order_number = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.status} - {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = 'Товар в заказ'
        verbose_name_plural = 'Товары в заказ'

    def __str__(self):
        return '{}'.format(self.id)


    def get_cost(self):
        return self.price * self.quantity
    

@receiver(post_save, sender=OrderItem)
def update_sales_statistics(sender, instance, **kwargs):
    total_sales = OrderItem.objects.aggregate(total_sales=models.Sum(models.F('price') * models.F('quantity')))['total_sales'] or 0
    total_quantity = OrderItem.objects.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
    products = Product.objects.all()
    for product in products:
        product_quantity = product.orderitem_set.aggregate(product_quantity=models.Sum('quantity'))['product_quantity'] or 0  # Рассчитываем количество проданных единиц товара
        product_sales = product.orderitem_set.aggregate(product_sales=models.Sum(models.F('price') * models.F('quantity')))['product_sales'] or 0  # Рассчитываем сумму продаж продукта
        share_of_total = (product_sales / total_sales) * 100 if total_sales > 0 else 0  # Рассчитываем долю продаж продукта
        sales_statistic, created = SalesStatistics.objects.get_or_create(product=product)
        sales_statistic.total_sales = product_sales
        sales_statistic.total_quantity = product_quantity  # Обновляем поле с количеством проданных единиц для каждого продукта
        sales_statistic.share_of_total = share_of_total  # Обновляем поле с долей
        sales_statistic.save()
    

@receiver(post_save, sender=Order)
def mark_order_as_new(sender, instance, created, **kwargs):
    if created:
        instance.new = True
        instance.save()