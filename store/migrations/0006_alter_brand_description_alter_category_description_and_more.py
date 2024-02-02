# Generated by Django 4.2.5 on 2023-09-25 19:16

from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name='Описание'),
        ),
    ]
