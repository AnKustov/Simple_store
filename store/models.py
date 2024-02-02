from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from autoslug import AutoSlugField
from django_ckeditor_5.fields import CKEditor5Field
import random


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок посту")
    content=CKEditor5Field('Зміст посту', config_name='extends')
    pub_date = models.DateTimeField(default=timezone.now, verbose_name="Дата публикації")
    photo = models.ImageField(upload_to='post_photos/', blank=True, null=True, verbose_name="Фотографія")
    photos = models.ManyToManyField('Photo', related_name='photo', verbose_name="Фотографії"),

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Стаття'
        verbose_name_plural = 'Статті'


class FeedbackMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Им'я користувача")
    message = models.TextField(verbose_name='Повідомлення')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Створено')
    new = models.BooleanField(default=True, verbose_name='Нове')

    def __str__(self):
        return f"Message from {self.name} at {self.created_at}"
    
    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'


class Brand(models.Model):
    name = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to='images/', null=True, verbose_name="Зображення")
    country = models.CharField(max_length=100)
    description=CKEditor5Field('Описание', config_name='extends')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name ='Бренд'
        verbose_name_plural = 'Бренди'


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)  
    description=CKEditor5Field('Описание', config_name='extends')
    image = models.ImageField(upload_to='images/', null=True, verbose_name="Зображення")
    slug = AutoSlugField(populate_from='name', unique=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='Категорія'
        verbose_name_plural = 'Категорії'


class Subcategory(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Назва підкатегорії")
    description=CKEditor5Field('Описание', config_name='extends')
    image = models.ImageField(upload_to='images/', null=True, verbose_name="Зображення підкатегорії")
    slug = AutoSlugField(populate_from='name', unique=True, default='')
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="Батьківська категорія")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Підкатегорія'
        verbose_name_plural = 'Підкатегорії'

            
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    description=CKEditor5Field('Описание', config_name='extends')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True,verbose_name="Підкатегорія")
    slug = AutoSlugField(populate_from='name', unique=True, default='') 
    article = models.PositiveIntegerField(unique=True, verbose_name="Артикул")

    def __str__(self):
        return f"{self.name} - {self.article}"
    
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'


def generate_article():
    return random.randint(100000, 999999)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')


@receiver(pre_save, sender=Product)
def set_article(sender, instance, **kwargs):
    if instance._state.adding:  # Проверка, что это новый товар
        instance.article = generate_article()

@receiver(post_save, sender=FeedbackMessage)
def mark_as_new(sender, instance, created, **kwargs):
    if created:
        instance.new = True
        instance.save()

