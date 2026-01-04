import os, json
import uuid
import random
import razorpay
# from weasyprint import CSS, HTML  # Commented out - requires GTK libraries on Windows
from products.models import *
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from home.models import ShippingAddress
from django.contrib.auth.models import User
from django.template.loader import get_template
from accounts.models import Profile, Cart, CartItem, Order, OrderItem
from base.emails import send_account_activation_email, send_otp_email
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect, render, get_object_or_404
from accounts.forms import UserUpdateForm, UserProfileForm, ShippingAddressForm, CustomPasswordChangeForm
from django.utils import timezone
from datetime import timedelta


# Create your views here.


def login_page(request):
    next_url = request.GET.get('next')  # Default to 'index' if 'next' is not provided
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Find user by email
        user_obj = User.objects.filter(email=email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found!')
            return HttpResponseRedirect(request.path_info)

        # Check if email is verified
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Please verify your email first!')
            return redirect('verify_otp', email=email)

        # then authenticate user
        user = authenticate(username=user_obj[0].username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login Successful.')
            
            # Check if the next URL is safe
            if url_has_allowed_host_and_scheme(url=next_url, allowed_hosts=request.get_host()):
                return redirect(next_url)
            else:
                return redirect('index')

        messages.warning(request, 'Invalid credentials.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def generate_otp():
    return str(random.randint(100000, 999999))


def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists!')
            return HttpResponseRedirect(request.path_info)

        # Create username from email (before @)
        username = email.split('@')[0]
        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create user
        user_obj = User.objects.create(
            username=username, first_name=first_name, last_name=last_name, email=email)
        user_obj.set_password(password)
        user_obj.save()

        # Generate OTP
        otp = generate_otp()
        profile = Profile.objects.get(user=user_obj)
        profile.otp = otp
        profile.otp_created_at = timezone.now()
        profile.save()

        # Send OTP email
        try:
            send_otp_email(email, otp, first_name)
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_otp', email=email)
        except Exception as e:
            messages.warning(request, f"Error sending email. Please try again.")
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')


def verify_otp(request, email):
    try:
        user = User.objects.get(email=email)
        profile = user.profile
    except User.DoesNotExist:
        messages.error(request, 'User not found!')
        return redirect('register')

    if profile.is_email_verified:
        messages.info(request, 'Email already verified. Please login.')
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        # Check if OTP is expired (10 minutes)
        if profile.otp_created_at:
            time_diff = timezone.now() - profile.otp_created_at
            if time_diff > timedelta(minutes=10):
                messages.error(request, 'OTP has expired. Please request a new one.')
                return HttpResponseRedirect(request.path_info)
        
        if profile.otp == entered_otp:
            profile.is_email_verified = True
            profile.otp = None
            profile.otp_created_at = None
            profile.save()
            messages.success(request, 'Email verified successfully! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/verify_otp.html', {'email': email})


def resend_otp(request, email):
    try:
        user = User.objects.get(email=email)
        profile = user.profile
    except User.DoesNotExist:
        messages.error(request, 'User not found!')
        return redirect('register')

    if profile.is_email_verified:
        messages.info(request, 'Email already verified.')
        return redirect('login')

    # Generate new OTP
    otp = generate_otp()
    profile.otp = otp
    profile.otp_created_at = timezone.now()
    profile.save()

    try:
        send_otp_email(email, otp, user.first_name)
        messages.success(request, 'New OTP sent to your email.')
    except Exception as e:
        messages.error(request, 'Error sending OTP. Please try again.')

    return redirect('verify_otp', email=email)

    return render(request, 'accounts/register.html')


@login_required
def user_logout(request):
    logout(request)
    messages.warning(request, "Logged Out Successfully!")
    return redirect('index')


def activate_email_account(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Account verification successful.')
        return redirect('login')
    except Exception as e:
        return HttpResponse('Invalid email token.')





@login_required
def add_to_cart(request, uid):
    try:
        variant = request.GET.get('size')
        if not variant:
            messages.error(request, 'Please select a size variant!')
            return redirect(request.META.get('HTTP_REFERER'))
        
        product = get_object_or_404(Product, uid=uid)

        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
        size_variant = get_object_or_404(SizeVariant, size_name=variant)

        # Check if the cart item already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, size_variant=size_variant)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, 'Item added to cart successfully.')

    except Exception as e:
        print(e)
        messages.error(request, 'Error adding item to cart.')

    return redirect(reverse('cart'))


@login_required
def cart(request):
    cart_obj = None
    payment = None
    user = request.user

    try:
        cart_obj = Cart.objects.get(is_paid=False, user=user)
    except Cart.DoesNotExist:
        # Create an empty cart for the user if one doesn't exist
        cart_obj = Cart.objects.create(user=user, is_paid=False)

    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__exact=coupon).first()

        if not coupon_obj:
            messages.warning(request, 'Invalid coupon code.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        if cart_obj and cart_obj.coupon:
            messages.warning(request, 'Coupon already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        if coupon_obj and coupon_obj.is_expired:
            messages.warning(request, 'Coupon code expired.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        if cart_obj and coupon_obj and cart_obj.get_cart_total() < coupon_obj.minimum_amount:
            messages.warning(
                request, f'Amount should be greater than {coupon_obj.minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        if cart_obj and coupon_obj:
            cart_obj.coupon = coupon_obj
            cart_obj.save()
            messages.success(request, 'Coupon applied successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Only create Razorpay order if cart has items
    if cart_obj and cart_obj.cart_items.count() > 0:
        try:
            cart_total_in_paise = int(cart_obj.get_cart_total_price_after_coupon() * 100)
            
            if cart_total_in_paise >= 100:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
                payment = client.order.create(
                    {'amount': cart_total_in_paise, 'currency': 'INR', 'payment_capture': 1})
                cart_obj.razorpay_order_id = payment['id']
                cart_obj.save()
        except Exception as e:
            print(f"Razorpay Error: {e}")
            messages.warning(request, 'Payment gateway temporarily unavailable. Please try again later.')

    context = {'cart': cart_obj, 'payment': payment, 'quantity_range': range(1, 6),}
    return render(request, 'accounts/cart.html', context)



@require_POST
@login_required
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity"))

        cart_item = CartItem.objects.get(uid=cart_item_id, cart__user=request.user, cart__is_paid=False)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def remove_cart(request, uid):
    try:
        cart_item = get_object_or_404(CartItem, uid=uid)
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')

    except Exception as e:
        print(e)
        messages.warning(request, 'Error removing item from cart.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()

    messages.success(request, 'Coupon Removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Payment success view
def success(request):
    order_id = request.GET.get('order_id')
    # cart = Cart.objects.get(razorpay_order_id = order_id)
    cart = get_object_or_404(Cart, razorpay_order_id = order_id)

    # Mark the cart as paid
    cart.is_paid = True
    cart.save()

    # Create the order after payment is confirmed
    order = create_order(cart, payment_mode="Online")

    context = {'order_id': order_id, 'order': order}
    return render(request, 'payment_success/payment_success.html', context)


# Cash on Delivery checkout view
@login_required
def cod_checkout(request):
    if request.method != 'POST':
        return redirect('cart')
    
    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
        
        if cart.cart_items.count() == 0:
            messages.warning(request, 'Your cart is empty!')
            return redirect('cart')
        
        # Generate a unique order ID for COD
        import time
        cod_order_id = f"COD_{int(time.time())}_{request.user.id}"
        cart.razorpay_order_id = cod_order_id
        cart.is_paid = True  # Mark as confirmed (payment on delivery)
        cart.save()
        
        # Create the order with COD payment mode
        order = create_order(cart, payment_mode="COD")
        
        messages.success(request, 'Order placed successfully! Pay when you receive your order.')
        return render(request, 'payment_success/payment_success.html', {
            'order_id': cod_order_id,
            'order': order,
            'payment_mode': 'COD'
        })
        
    except Cart.DoesNotExist:
        messages.error(request, 'Cart not found!')
        return redirect('cart')
    except Exception as e:
        print(f"COD Error: {e}")
        messages.error(request, 'Error processing order. Please try again.')
        return redirect('cart')


# HTML to PDF Conversion
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)

    # Path to the staticfiles directory
    static_root = settings.STATIC_ROOT
    
    # List all CSS files you need, now collected in STATIC_ROOT
    css_files = [
        os.path.join(static_root, 'css', 'bootstrap.css'),
        os.path.join(static_root, 'css', 'responsive.css'),
        os.path.join(static_root, 'css', 'ui.css'),
    ]

    # Create CSS objects for each file
    css_objects = [CSS(filename=css_file) for css_file in css_files]

    # Convert HTML to PDF with all CSS stylesheets applied
    pdf_file = HTML(string=html).write_pdf(stylesheets=css_objects)
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{context_dict["order"].order_id}.pdf"'

    return response



def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.order_items.all()

    context = {
        'order': order,
        'order_items': order_items,
    }

    pdf = render_to_pdf('accounts/order_pdf_generate.html', context)
    if pdf:
        return pdf
    return HttpResponse("Error generating PDF", status=400)



@login_required
def profile_view(request, username):
    user_name = get_object_or_404(User, username=username)
    user = request.user
    profile = user.profile

    user_form = UserUpdateForm(instance=user)
    profile_form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'user_name' : user_name,
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def update_shipping_address(request):
    shipping_address = ShippingAddress.objects.filter(
        user=request.user, current_address=True).first()

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.current_address = True
            shipping_address.save()

            messages.success(request, "The Address Has Been Successfully Saved/Updated!")
            
            form = ShippingAddressForm()
        else:
            form = ShippingAddressForm(request.POST, instance=shipping_address)
    else:
        form = ShippingAddressForm(instance=shipping_address)

    return render(request, 'accounts/shipping_address_form.html', {'form': form})


# Order history view
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'accounts/order_history.html', {'orders': orders})


# Create an order view
def create_order(cart, payment_mode="Online"):
    payment_status = "Paid" if payment_mode == "Online" else "Pending (COD)"
    
    order, created = Order.objects.get_or_create(
        user=cart.user,
        order_id=cart.razorpay_order_id,
        payment_status=payment_status,
        shipping_address=cart.user.profile.shipping_address,
        payment_mode=payment_mode,
        order_total_price=cart.get_cart_total(),
        coupon=cart.coupon,
        grand_total=cart.get_cart_total_price_after_coupon(),
    )

    # Create OrderItem instances for each item in the cart
    cart_items = CartItem.objects.filter(cart=cart)
    for cart_item in cart_items:
        OrderItem.objects.get_or_create(
            order=order,
            product=cart_item.product,
            size_variant=cart_item.size_variant,
            color_variant=cart_item.color_variant,
            quantity=cart_item.quantity,
            product_price=cart_item.get_product_price()
        )

    return order


# Order Details view
@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
        'order_total_price': sum(item.get_total_price() for item in order_items),
        'coupon_discount': order.coupon.discount_amount if order.coupon else 0,
        'grand_total': order.get_order_total_price()
    }
    return render(request, 'accounts/order_details.html', context)


# Delete user account feature
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('index')