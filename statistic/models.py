from django.db import models
from store.models import *
from orders.models import *
from django.contrib.auth.models import User  
from django.utils import timezone


# Модель для хранения данных о продажах 
class SalesStatistics(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="Товар")
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма продаж")
    total_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество единиц") 
    share_of_total = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Доля продаж %") 


    class Meta:
        verbose_name = 'Статистика продаж'
        verbose_name_plural = 'Статистика продаж'

    

    def __str__(self):
        return f"Статистика продаж для {self.product.name}"
        


