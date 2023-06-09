from django.shortcuts import render

from .models import ShippingAddress, Order, OrderItem
from cart.cart import Cart

from django.http import JsonResponse

# Create your views here.

def checkout(request):
    
    if request.user.is_authenticated:
        try:
            # Authenticate user with shipping information
            shipping_address = ShippingAddress.objects.get(id=request.user.id)
            context = {'shipping': shipping_address}
            return render(request, 'payment/checkout.html', context)
        except:
            return render(request, 'payment/checkout.html')
    
    
    return render(request, 'payment/checkout.html')


def complete_order(request):
    if request.POST.get('action') == 'post':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        
        # style user shipping address
        shipping_address = (address1 + "\n" + address2 + "\n" + city + "\n" + state + "\n" + zipcode + "\n")
        
        # shopping cart information
        cart = Cart(request)
        
        #get the total price of items
        total_cost = cart.get_total()
        
        '''
            order variation:
            1) Create order -> Account user WITH + WITHOUT shipping information
            2) Create order -> Guest user without account
        '''
        # create order -> authenticated user WITH + WITHOUT shipping information
        if request.user.is_authenticated:
            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address, ammount_paid=total_cost, user=request.user)
            
            order_id = order.pk
            
            for item in cart:
                OrderItem.objects.create(order_id=order_id, product=item['product'], quantity=item['qty'], price=item['price'], user=request.user)
        
        else:
            
            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address, ammount_paid=total_cost, user=request.user)
            
            order_id = order.pk
            
            for item in cart:
                OrderItem.objects.create(order_id=order_id, product=item['product'], quantity=item['qty'], price=item['price'])
        
        order_success = True
        response = JsonResponse({'success': order_success})
        return response
            
        

def payment_success(request):
    
    # clear shopping cart
    
    for key in list(request.session.keys()):
        del request.session[key]
        
    return render(request, 'payment/payment-success.html')

def payment_failed(request):
    return render(request, 'payment/payment-failed.html')
    