from django.urls import path, include
from django.contrib.auth import views as auth_views
from .models import *
from .views import *
from store.admin import *


urlpatterns = [
    #АДМИНКА
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    
    #КОНТЕНТ
    path('', main, name='main'),
    path('about-project/', about_project, name='about_project'),
    path('brands/', brand_list, name='brand_list'),
    path('brands/<int:brand_id>/', brand_detail, name='brand_detail'),
    # path('categories/', category_list, name='category_list'),
    path('categories/<slug:category_slug>/subcategories/', subcategory_list, name='subcategory_list'),
    path('categories/<slug:slug>/', category_detail, name='category_detail'),
    path('subcategories/<slug:slug>/', subcategory_detail, name='subcategory_detail'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('posts/', post_list, name='post_list'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('feedback/', feedback_view, name='feedback'),
    path('search/', search_results, name='search_results'),

    
    #АДМИН ПАНЕЛЬ
    path('upload_csv/', upload_csv, name='upload_csv'),

    # ПОЛЬЗОВАТЕЛЬ
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('profile/change_password/', change_password, name='change_password'),
    ]