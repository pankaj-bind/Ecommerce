from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Cart, CartItem, Order, OrderItem


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_image_preview', 'phone_display', 'has_shipping_address']
    search_fields = ['user__username', 'user__email', 'bio']
    list_filter = ['user__date_joined']
    readonly_fields = ['profile_image_preview_large']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',),
            'description': 'The linked user account.'
        }),
        ('Profile Details', {
            'fields': ('profile_image', 'profile_image_preview_large', 'bio'),
            'description': 'Upload a profile picture and add a bio.'
        }),
        ('Shipping Information', {
            'fields': ('shipping_address',),
            'description': 'Enter the default shipping address for this user.',
        }),
    )
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover; border: 2px solid #6366f1;" />', obj.profile_image.url)
        return format_html('<span style="display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 50%; background: #f1f5f9; color: #64748b;">👤</span>')
    profile_image_preview.short_description = "Avatar"
    
    def profile_image_preview_large(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 12px; object-fit: cover;" />', obj.profile_image.url)
        return "No Image Uploaded"
    profile_image_preview_large.short_description = "Current Image"
    
    def phone_display(self, obj):
        return obj.shipping_address[:20] + '...' if obj.shipping_address and len(obj.shipping_address) > 20 else (obj.shipping_address or 'Not Set')
    phone_display.short_description = "Address"
    
    def has_shipping_address(self, obj):
        if obj.shipping_address:
            return format_html('<span style="color: #10b981;">✓ Yes</span>')
        return format_html('<span style="color: #ef4444;">✗ No</span>')
    has_shipping_address.short_description = "Has Address"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'size_variant', 'quantity', 'item_total']
    can_delete = True
    
    def item_total(self, obj):
        return format_html('₹{}', obj.get_product_price())
    item_total.short_description = "Total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'user', 'coupon_display', 'items_count', 'cart_total_display', 'is_paid']
    list_filter = ['is_paid', 'coupon']
    search_fields = ['user__username', 'user__email', 'razorpay_order_id']
    readonly_fields = ['cart_total_display', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_payment_signature']
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'is_paid'),
            'description': 'Basic cart information.'
        }),
        ('Discount', {
            'fields': ('coupon',),
            'description': 'Apply a coupon code to this cart.',
        }),
        ('Payment Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_payment_signature'),
            'description': 'Razorpay payment information (read-only).',
            'classes': ('collapse',),
        }),
    )
    
    def cart_id(self, obj):
        return format_html('<code style="background: #f1f5f9; padding: 2px 8px; border-radius: 4px;">{}</code>', str(obj.uid)[:8])
    cart_id.short_description = "Cart ID"
    
    def coupon_display(self, obj):
        if obj.coupon:
            return format_html('<span style="background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>', obj.coupon.coupon_code)
        return '-'
    coupon_display.short_description = "Coupon"
    
    def items_count(self, obj):
        count = obj.cart_items.count()
        return format_html('<span style="background: #6366f1; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px;">{} items</span>', count)
    items_count.short_description = "Items"
    
    def cart_total_display(self, obj):
        return format_html('<strong style="color: #6366f1;">₹{}</strong>', obj.get_cart_total())
    cart_total_display.short_description = "Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart_user', 'size_variant', 'quantity', 'price_display']
    list_filter = ['size_variant']
    search_fields = ['product__product_name', 'cart__user__username']
    
    def cart_user(self, obj):
        return obj.cart.user.username if obj.cart.user else 'Anonymous'
    cart_user.short_description = "Customer"
    
    def price_display(self, obj):
        return format_html('<strong>₹{}</strong>', obj.get_product_price())
    price_display.short_description = "Price"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'size_variant', 'quantity', 'product_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'order_date', 'items_count', 'order_total_display', 'status_badge']
    list_filter = ['order_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['order_total_display', 'order_date']
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'order_date'),
            'description': 'Order details.'
        }),
        ('Order Summary', {
            'fields': ('order_total_price',),
        }),
    )
    
    def order_id(self, obj):
        return format_html('<code style="background: #fef3c7; padding: 2px 8px; border-radius: 4px; color: #92400e;">ORD-{}</code>', str(obj.uid)[:8].upper())
    order_id.short_description = "Order ID"
    
    def items_count(self, obj):
        count = obj.order_items.count()
        return format_html('<span style="background: #e0e7ff; color: #3730a3; padding: 2px 10px; border-radius: 12px; font-size: 12px;">{} items</span>', count)
    items_count.short_description = "Items"
    
    def order_total_display(self, obj):
        return format_html('<strong style="color: #059669; font-size: 16px;">₹{}</strong>', obj.order_total_price)
    order_total_display.short_description = "Total"
    
    def status_badge(self, obj):
        return format_html('<span style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 12px; font-size: 12px;">✓ Completed</span>')
    status_badge.short_description = "Status"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'product', 'size_variant', 'quantity', 'price_display']
    list_filter = ['order__order_date']
    search_fields = ['product__product_name', 'order__user__username']
    
    def order_id(self, obj):
        return format_html('<code>ORD-{}</code>', str(obj.order.uid)[:8].upper())
    order_id.short_description = "Order"
    
    def price_display(self, obj):
        return format_html('<strong>₹{}</strong>', obj.product_price)
    price_display.short_description = "Price"