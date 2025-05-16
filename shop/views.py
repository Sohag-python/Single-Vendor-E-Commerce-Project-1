from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

def home(request):
    products = Product.objects.all().order_by('-created_at')[:10]
    return render(request, 'shop/home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('shop:cart')

@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.new_price * item.quantity for item in items)
    return render(request, 'shop/cart.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('shop:cart')

@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)
    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('shop:home')

    total_amount = sum(item.product.new_price * item.quantity for item in items)

    if request.method == 'POST':
        # Create order and order items
        order = Order.objects.create(user=request.user, total_amount=total_amount)
        for item in items:
            OrderItem.objects.create(order=order, product=item.product,
                                     quantity=item.quantity, price=item.product.new_price)
            # Update stock
            item.product.stock -= item.quantity
            item.product.save()
        items.delete()
        # Redirect to SSLCommerz payment page or mock payment success page
        # For now, just redirect success page for demo
        return redirect('shop:payment_success')

    return render(request, 'shop/checkout.html', {'items': items, 'total': total_amount})

@login_required
def payment_success(request):
    messages.success(request, "Payment successful! Thank you for your purchase.")
    return render(request, 'shop/payment_success.html')

@login_required
def payment_fail(request):
    messages.error(request, "Payment failed or cancelled.")
    return render(request, 'shop/payment_fail.html')
