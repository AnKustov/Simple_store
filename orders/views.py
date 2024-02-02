from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import F
from orders.models import *
from .models import *
from statistic.models import *
from .forms import OrderCreateForm
from cart.cart import Cart
from store.sms_utils import send_sms


def order_create(request):
    categories = Category.objects.all()
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False) 
            if request.user.is_authenticated:  # Проверка авторизации пользователя
                order.user = request.user
          
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
                
            # message = f"{order.first_name}, Ваш заказ успешно создан. Номер заказа: {order.order_number}. Наш менеджер свяжется с Вами в ближайшее время"
            # message = f"...."

            # send_sms(order.phone_number, message)
            # очистка корзины
            cart.clear()

            return redirect(reverse('orders:order_created'))
    else:
        form = OrderCreateForm()
    return render(request, 'create.html',
                  {'cart': cart, 'form': form, 'categories': categories})


def order_created_view(request):
    categories = Category.objects.all()
    order = Order.objects.latest('created')
    return render(request, 'created.html', {'order': order, 'categories': categories})

