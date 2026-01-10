from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import *


# Customize Admin Site Header
admin.site.site_header = "BuyNest Shoes Admin"
admin.site.site_title = "BuyNest Shoes Admin Portal"
admin.site.index_title = "Welcome to BuyNest Shoes Administration"


class ProductImageInlineForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
        widgets = {
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
                'style': 'width: 100%;'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        image_url = cleaned_data.get('image_url')
        
        if not image and not image_url:
            raise forms.ValidationError("Please provide either an image file or an image URL.")
        
        return cleaned_data


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageInlineForm
    extra = 3
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"
    fields = ['image', 'image_url', 'image_preview_inline']
    readonly_fields = ['image_preview_inline']
    
    def image_preview_inline(self, obj):
        url = obj.get_image_url() if obj.pk else None
        if url:
            return format_html('<img src="{}" width="80" height="80" style="border-radius: 8px; object-fit: cover;" />', url)
        return "No Preview"
    image_preview_inline.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'slug', 'category_image_preview', 'product_count']
    search_fields = ['category_name', 'slug']
    prepopulated_fields = {'slug': ('category_name',)}
    list_per_page = 20
    
    fieldsets = (
        ('Category Information', {
            'fields': ('category_name', 'slug'),
            'description': 'Enter the category details below. The slug will be auto-generated from the name.'
        }),
        ('Category Image', {
            'fields': ('category_image', 'category_image_url'),
            'description': '<strong>Choose ONE option:</strong><br>• Upload an image file from your computer, OR<br>• Paste an image URL from the web'
        }),
    )
    
    def category_image_preview(self, obj):
        url = obj.get_image_url()
        if url:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />', url)
        return "No Image"
    category_image_preview.short_description = "Preview"
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'price', 'newest_product', 'image_preview', 'created_at']
    list_filter = ['category', 'newest_product', 'created_at']
    search_fields = ['product_name', 'product_desription', 'slug']
    prepopulated_fields = {'slug': ('product_name',)}
    list_editable = ['newest_product', 'price']
    list_per_page = 20
    date_hierarchy = 'created_at'
    inlines = [ProductImageInline]
    filter_horizontal = ['color_variant', 'size_variant']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'slug', 'category'),
            'description': 'Enter the basic product information.'
        }),
        ('Pricing', {
            'fields': ('price',),
            'description': 'Set the product price in INR (₹).'
        }),
        ('Description', {
            'fields': ('product_desription',),
            'classes': ('wide',),
        }),
        ('Variants', {
            'fields': ('color_variant', 'size_variant'),
            'description': 'Select available color and size variants for this shoe.',
            'classes': ('collapse',),
        }),
        ('Display Options', {
            'fields': ('newest_product', 'parent'),
            'description': 'Configure display options.',
            'classes': ('collapse',),
        }),
    )
    
    def image_preview(self, obj):
        first_image = obj.product_images.first()
        if first_image:
            url = first_image.get_image_url()
            if url:
                return format_html('<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />', url)
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_source', 'image_preview']
    list_filter = ['product']
    search_fields = ['product__product_name']
    
    fieldsets = (
        ('Product', {
            'fields': ('product',),
        }),
        ('Image Source (Choose ONE)', {
            'fields': ('image', 'image_url'),
            'description': '<strong>Option 1:</strong> Upload an image file from your computer<br><strong>Option 2:</strong> Paste an image URL from the web'
        }),
    )
    
    def image_source(self, obj):
        if obj.image:
            return format_html('<span style="color: #0d9488;"><i class="fas fa-upload"></i> Uploaded File</span>')
        elif obj.image_url:
            return format_html('<span style="color: #06b6d4;"><i class="fas fa-link"></i> External URL</span>')
        return "No Image"
    image_source.short_description = "Source"
    
    def image_preview(self, obj):
        url = obj.get_image_url()
        if url:
            return format_html('<img src="{}" width="80" height="80" style="border-radius: 8px; object-fit: cover;" />', url)
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'color_preview', 'price', 'product_count']
    search_fields = ['color_name']
    list_editable = ['price']
    
    fieldsets = (
        ('Color Information', {
            'fields': ('color_name', 'price'),
            'description': 'Enter color name and additional price (if any) for this color variant.'
        }),
    )
    
    def color_preview(self, obj):
        return format_html('<span style="display: inline-block; width: 25px; height: 25px; background-color: {}; border-radius: 50%; border: 2px solid #ddd;"></span>', obj.color_name.lower())
    color_preview.short_description = "Color"
    
    def product_count(self, obj):
        from products.models import Product
        return Product.objects.filter(color_variant=obj).count()
    product_count.short_description = "Used in Products"


@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price', 'order', 'product_count']
    search_fields = ['size_name']
    list_editable = ['price', 'order']
    ordering = ['order']
    
    fieldsets = (
        ('Size Information', {
            'fields': ('size_name', 'price', 'order'),
            'description': 'Enter size name, additional price, and display order. Lower order numbers appear first.'
        }),
    )
    
    def product_count(self, obj):
        from products.models import Product
        return Product.objects.filter(size_variant=obj).count()
    product_count.short_description = "Used in Products"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', 'discount_amount', 'minimum_amount', 'is_expired', 'usage_count']
    search_fields = ['coupon_code']
    list_filter = ['is_expired']
    list_editable = ['is_expired', 'discount_amount']
    
    fieldsets = (
        ('Coupon Details', {
            'fields': ('coupon_code', 'discount_amount'),
            'description': 'Create a new coupon code with discount amount.'
        }),
        ('Restrictions', {
            'fields': ('minimum_amount', 'is_expired'),
            'description': 'Set minimum order amount and expiry status.',
        }),
    )
    
    def usage_count(self, obj):
        return obj.cart_set.count()
    usage_count.short_description = "Times Used"


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'stars_display', 'short_review', 'date_added']
    list_filter = ['stars', 'date_added']
    search_fields = ['product__product_name', 'user__username', 'content']
    readonly_fields = ['user', 'product', 'stars', 'content', 'date_added']
    date_hierarchy = 'date_added'
    
    def stars_display(self, obj):
        stars = '★' * obj.stars + '☆' * (5 - obj.stars)
        return format_html('<span style="color: #f59e0b; font-size: 16px;">{}</span>', stars)
    stars_display.short_description = "Rating"
    
    def short_review(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return "-"
    short_review.short_description = "Review"


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'size_variant', 'added_on']
    list_filter = ['added_on']
    search_fields = ['user__username', 'product__product_name']
    date_hierarchy = 'added_on'