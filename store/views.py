import random
import requests
import csv
import tempfile
from decimal import Decimal
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.conf import settings
from django.http import JsonResponse
from .models import *
from .forms import *
from cart.forms import *
from orders.models import *


cart_session_id = settings.CART_SESSION_ID

def main(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    all_products = list(Product.objects.all())
    num_available_products = len(all_products)
    num_random_products = min(num_available_products, 12)
    latest_posts = Post.objects.order_by('-pub_date')[:3]
    random_products = random.sample(all_products, num_random_products)

    context = {
        'categories': categories,
        'brands': brands,
        'random_products': random_products,
        'latest_posts': latest_posts
    }

    return render(request, 'main.html', context)

def footer_category_list(request):
    categories = Category.objects.all()
    return render(request, 'footer_category_list.html', {'categories': categories})


def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'brand_list.html', {'brands': brands})


def brand_detail(request, brand_id):
    categories = Category.objects.all()
    brand = get_object_or_404(Brand, id=brand_id)
    products = Product.objects.filter(brand=brand)
    items_per_page = 24
    paginator = Paginator(products, items_per_page)    
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)


    return render(request, 'brand_detail.html', {'brand': brand, 'products': products, 'categories': categories})


def about_project(request):
    categories = Category.objects.all()
    return render(request, 'about_project.html', {'categories': categories})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def subcategory_list(request, category_slug):
    subcategories = Subcategory.objects.filter(parent_category__slug=category_slug)
    return render(request, 'subcategory_list.html', {'subcategories': subcategories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    categories = Category.objects.all()
    products = Product.objects.filter(category=category)
    items_per_page = 24
    paginator = Paginator(products, items_per_page)    
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'category_detail.html', {'category': category, 'categories': categories,'products': products})


def subcategory_detail(request, slug):
    categories = Category.objects.all()
    subcategory = get_object_or_404(Subcategory, slug=slug)
    products = Product.objects.filter(subcategory=subcategory)
    items_per_page = 24
    paginator = Paginator(products, items_per_page)    
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'subcategory_detail.html', {'subcategory': subcategory, 'products': products, 'categories': categories})


def product_detail(request, slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product, slug=slug)
    cart_product_form = CartAddProductForm()
    return render(request, 'product_detail.html', {'product': product, 'categories': categories,'cart_product_form': cart_product_form})


def post_list(request):
    categories = Category.objects.all()
    posts = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(posts, 3) 

    page = request.GET.get('page')
    try:
        paginated_posts = paginator.page(page)
    except PageNotAnInteger:
        paginated_posts = paginator.page(1)
    except EmptyPage:
        paginated_posts = paginator.page(paginator.num_pages)

    return render(request, 'post_list.html', {'paginated_posts': paginated_posts, 'categories': categories})


def post_detail(request, post_id):
    categories = Category.objects.all()
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post, 'categories': categories})


def feedback_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            message = form.cleaned_data['message']

            feedback_message = FeedbackMessage(name=name, message=message)
            feedback_message.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = FeedbackForm()
    return render(request, 'feedback_form.html', {'form': form, 'categories': categories})


def search_results(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    query = request.GET.get('q', '').strip()

    if query:
        products = Product.objects.filter(
            Q(name__iregex=rf'{query}') | Q(article__iregex=rf'{query}')
        )

    items_per_page = 24
    paginator = Paginator(products, items_per_page)    
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'search_results.html', {'products': products, 'query': query, 'categories': categories})


# ПОЛЬЗОВАТЕЛЬ
def register(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form, 'categories': categories})


def user_login(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')  
        else:
            messages.error(request, 'Неправильное имя пользователя или пароль.')
    return render(request, 'login.html', {'categories': categories})


@login_required
def user_logout(request):
    logout(request)
    return redirect('main') 


@login_required
def profile(request):
    categories = Category.objects.all()
    user = request.user
    orders = Order.objects.filter(user=user)
    
    total_order_amount = Decimal('0')
    order_total = Decimal('0')
    for order in orders:
        order_total = order.items.annotate(
                    item_total=ExpressionWrapper(F('product__price') * F('quantity'), 
                    output_field=DecimalField())
                    ).aggregate(total=Sum('item_total'))['total'] or Decimal('0')

        # Добавляем стоимость заказа к total_order_amount
        total_order_amount += order_total

        # Добавляем order_total к каждому заказу
        order.order_total = order_total

    # общая сумма сохраняется в сессии
    request.session['total_order_amount'] = str(total_order_amount)

    context = {'user': user, 
               'orders': orders,
               'order_total': order_total,
               'total_order_amount': total_order_amount,
               'categories': categories}

    return render(request, 'profile.html', context) 


@login_required
def order_detail(request, order_id):
    categories = Category.objects.all()
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_total = order.items.annotate(
        item_total=ExpressionWrapper(F('product__price') * F('quantity'), output_field=DecimalField())
    ).aggregate(total=Sum('item_total'))['total'] or Decimal('0')

    product_slugs = [item.product.slug for item in order.items.all()]

    
    context = {
        'order': order,
        'order_total': order_total,
        'categories': categories,
        'product_slugs': product_slugs,
    }
    
    return render(request, 'order_detail.html', context)

@login_required
def change_password(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль успешно изменен!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form, 'categories': categories})


#**************************АДМИН ПАНЕЛЬ**************************

# ЗАГРУЗКА ТОВАРОВ НА САЙТ
def handle_uploaded_file(file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    for chunk in file.chunks():
        temp_file.write(chunk)
    temp_file.close()

    import_products_from_csv(temp_file.name)


def import_products_from_csv(file):
    with open(file, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            brand_name = row['Brand']
            category_name = row['Category']
            try:
                brand, created = Brand.objects.get_or_create(name=brand_name)
            except Brand.DoesNotExist:
                brand = Brand(name=brand_name)
                brand.save()

            try:
                category, created = Category.objects.get_or_create(name=category_name)
            except Category.DoesNotExist:
                category = Category(name=category_name)
                category.save()

            subcategory_name = row['Subcategory']
            if subcategory_name:
                try:
                    subcategory, created = Subcategory.objects.get_or_create(
                        name=subcategory_name,
                        parent_category=category)
                except Subcategory.DoesNotExist:
                    subcategory = Subcategory(name=subcategory_name)
                    subcategory.save()
            else:
                subcategory = None 

            product = Product(
                name=row['Name'],
                description=row['Description'],
                price=row['Price'],
                brand=brand, 
                category=category,  
                subcategory=subcategory,  
                article=row['Article'],
            )
            product.save()
            
            # Создаем объекты ProductImage для каждого URL-адреса изображения
            for i in range(3):
                image_url_column_name = f'image_url_{i}'
                image_url = row.get(image_url_column_name)
                if image_url:
                    response = requests.get(image_url)
                    image_content = ContentFile(response.content)
                    product_image = ProductImage(product=product)
                    product_image.image.save(image_url.split("/")[-1], image_content)
                    product_image.save()


def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            handle_uploaded_file(csv_file)
            return redirect('main')
    else:
        form = CSVUploadForm()
    return render(request, 'admin/upload_csv.html', {'form': form})

