from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage

from store.views.user_views import jwt_encode, jwt_decode, auth_admin
from store.models import User, Product, Category, CarouselImage, Order
import json

##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
#######################>>>>>>>>>>>>>>>>>>>>>> Admin Management API's <<<<<<<<<<<<<<<<<<<<<<<<<#############################
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
@csrf_exempt
def admin_login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    data = json.loads(request.body)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'message': 'Missing email or password.'}, status=400)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=400)
    
    user = authenticate(request, username=user.email, password=password)

    if user is not None:
        if user.is_staff:
            login(request, user)
            token = jwt_encode(user.email)
            return JsonResponse({'success': True, 'message': 'Login successful.', 'email': email, 'token': token}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'You do not have admin access.'}, status=403)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=400)
    
    
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
#######################>>>>>>>>>>>>>>>>>>>>>> User Management API's <<<<<<<<<<<<<<<<<<<<<<<<<##############################
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
@csrf_exempt
def users_list(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication Header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token.'}, status=401)
        
        users = User.objects.filter(is_customer=True)
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone_number': user.phone_number,
                'date_of_birth': user.dob,
                'marital_status': user.marital_status,
                'two_factor': user.two_factor,
                'login_by' : user.login_by,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            })
        return JsonResponse({'success': True, 'message': 'Users retrieved successfully.', 'user_list': user_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
        
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
#####################>>>>>>>>>>>>>>>>>>>>>> Product Management API's <<<<<<<<<<<<<<<<<<<<<<<<<############################
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
@csrf_exempt
def add_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        discount_price = request.POST.get('discount_price', '').strip()
        video_url = request.POST.get('video_url', '').strip()
        attributes = request.POST.get('attributes', '').strip()
        is_featured = request.POST.get('is_featured', 'false').strip().lower() == 'true'
        rating = float(request.POST.get('rating', 0.0))
        brand = request.POST.get('brand', '').strip()
        stock = request.POST.get('stock', '').strip()
        category_id = request.POST.get('category_id', '').strip()
        images = request.FILES.getlist('image')
        
        required_fields = ['name', 'description', 'price', 'stock', 'category_id']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)

        products_image_paths = []

        for image in images:
            image_path = default_storage.save(f'products/{image.name}', image)
            products_image_paths.append(image_path)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            video_url=video_url,
            attributes=attributes,
            is_featured=is_featured,
            rating=rating,
            brand=brand,
            stock=stock,
            category=category,
            image=products_image_paths
        )
        
        return JsonResponse({'success': True, 'message': 'Product added successfully.', 'product_id': product.id}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        required_fields = ['product_id', 'name', 'description', 'price', 'discount_price', 'video_url', 'attributes', 'is_featured', 'rating', 'brand', 'stock', 'category_id']
        missing_fields = [field for field in required_fields if field not in request.POST]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
        
        try:
            product_id = request.POST.get('product_id', '').strip()
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        
        product.name = request.POST.get('name', product.name).strip()
        product.description = request.POST.get('description', product.description).strip()
        product.price = request.POST.get('price', product.price).strip()
        product.discount_price = request.POST.get('discount_price', product.discount_price).strip()
        product.video_url = request.POST.get('video_url', product.video_url).strip()
        product.attributes = request.POST.get('attributes', product.attributes)
        product.is_featured = request.POST.get('is_featured', product.is_featured) == 'True'
        product.rating = request.POST.get('rating', product.rating)
        product.brand = request.POST.get('brand', product.brand).strip()
        product.stock = request.POST.get('stock', product.stock).strip()
        product.category_id = request.POST.get('category_id', product.category_id).strip()
        images = request.FILES.getlist('image')
        products_image_paths = []

        if images:
            for image in images:
                image_path = default_storage.save(f'products/{image.name}', image)
                products_image_paths.append(image_path)
            product.image = products_image_paths
        product.save()
        
        return JsonResponse({'success': True, 'message': 'Product updated successfully.', 'product_id': product.id}, status=200)
 
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def delete_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        try:
            product_id = request.POST.get('product_id', '').strip()
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'success': True, 'message': 'Product deleted successfully.'}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def list_products(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        products = Product.objects.all().values(
            'id', 
            'name', 
            'description', 
            'price', 
            'discount_price',
            'stock', 
            'category__name', 
            'image',
            'video_url',
            'attributes',
            'is_featured',
            'rating',
            'brand',
            'meta_keywords',
            'meta_description'
        )
        products_list = list(products)
        
        return JsonResponse({'success': True, 'products': products_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
    
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
#####################>>>>>>>>>>>>>>>>>>>>>> Category Management API's <<<<<<<<<<<<<<<<<<<<<<<<<############################
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
@csrf_exempt
def add_category(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication Header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token.'}, status=401)
        
        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')

        missing_fields = []
        if not category_name:
            missing_fields.append('category_name')
        if not description:
            missing_fields.append('description')
        if not image:
            missing_fields.append('image')
        
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
        
        category = Category.objects.create(
            name=category_name,
            description=description,
            image=image
        )
        
        return JsonResponse({'success': True, 'message': 'Category added successfully.', 'category_id': category.id}, status=201)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
        
@csrf_exempt
def update_category(request, category_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST. '}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'sucess': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        category = Category.objects.get(id=category_id)
        
        if not category:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        name = request.POST.get('name', category.name).strip()
        description = request.POST.get('description', category.description).strip()
        image = request.POST.get('image', category.image)
        
        category.name = name
        category.description = description
        if image:
            category.image = image
        category.save()
        
        return JsonResponse({'success': True, 'message': 'Category updated successfully.', 'category_id': category.id}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def delete_category(request):
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use DELETE.'}, status=405)
        
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        data = json.loads(request.body)
        category_id = data.get('category_id', '')
        category = Category.objects.get(id=category_id)
        
        if not category:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        category.delete()
        
        return JsonResponse({'success': True, 'message': 'Category deleted successfully.'}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def list_categories(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        categories = Category.objects.all().values('id', 'name', 'description', 'image')
        categories_list = list(categories)
        
        return JsonResponse({'success': True, 'categories': categories_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
#####################>>>>>>>>>>>>>>>>>>>>>> Carousel Management API's <<<<<<<<<<<<<<<<<<<<<<<<<############################
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
@csrf_exempt
def add_carousel_image(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        product_id = request.POST.get('product_id')
        product = None
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
        image = request.FILES.get('image')
        if not image:
            return JsonResponse({'success': False, 'message': 'Image is required.'}, status=400)
        
        title = request.POST.get('title', '')
        caption = request.POST.get('caption', '')
        alt_text = request.POST.get('alt_text', '')
        external_link = request.POST.get('external_link', '')
        hover_text = request.POST.get('hover_text', '')

        carousel_image = CarouselImage.objects.create(
            product=product,
            image=image,
            title=title,
            caption=caption,
            alt_text=alt_text,
            external_link=external_link,
            hover_text=hover_text
        )

        return JsonResponse({'success': True, 'message': 'Carousel image added successfully.', 'carousel_image_id': carousel_image.id},status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_carousel_image(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        carousel_image_id = request.POST.get('carousel_image_id')
        if not carousel_image_id:
            return JsonResponse({'success': False, 'message': 'Carousel image ID is required.'}, status=400)
        
        try:
            carousel_image = CarouselImage.objects.get(id=carousel_image_id)
        except CarouselImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Carousel image not found.'}, status=404)
        
        if 'product_id' in request.POST:
            product_id = request.POST.get('product_id')
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    carousel_image.product = product
                except Product.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        else:
            carousel_image.product = None

        if 'image' in request.FILES:
            carousel_image.image = request.FILES.get('image')
        
        title = request.POST.get('title', '')
        caption = request.POST.get('caption', '')
        alt_text = request.POST.get('alt_text', '')
        external_link = request.POST.get('external_link', '')
        hover_text = request.POST.get('hover_text', '')

        carousel_image.title = title
        carousel_image.caption = caption
        carousel_image.alt_text = alt_text
        carousel_image.external_link = external_link
        carousel_image.hover_text = hover_text
        carousel_image.save()

        return JsonResponse({'success': True, 'message': 'Carousel image updated successfully.', 'carousel_image_id': carousel_image.id},status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def delete_carousel_image(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        carousel_image_id = request.POST.get('carousel_image_id')
        if not carousel_image_id:
            return JsonResponse({'success': False, 'message': 'Carousel image ID is required.'}, status=400)
        
        try:
            carousel_image = CarouselImage.objects.get(id=carousel_image_id)
        except CarouselImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Carousel image not found.'}, status=404)
        
        carousel_image.delete()

        return JsonResponse({'success': True, 'message': 'Carousel image deleted successfully.'},status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def list_carousel_images(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        carousel_images = CarouselImage.objects.all().values('id', 'product__name', 'product__id', 'image', 'title', 'caption', 'alt_text', 'external_link', 'hover_text')
        carousel_images_list = list(carousel_images)
        
        return JsonResponse({'success': True, 'carousel_images': carousel_images_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def list_carousel_images_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        carousel_images = CarouselImage.objects.all().order_by('display_order').values('id', 'product__name', 'product__id', 'image', 'title', 'caption', 'alt_text', 'external_link', 'hover_text')
        carousel_images_list = list(carousel_images)

        return JsonResponse({'success': True, 'carousel_images': carousel_images_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def get_carousel_image(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        carousel_image_id = request.POST.get('carousel_image_id')
        if not carousel_image_id:
            return JsonResponse({'success': False, 'message': 'Carousel Image ID is required.'}, status=400)
        
        carousel_image = CarouselImage.objects.get(id=carousel_image_id).values('id', 'product__name', 'product__id', 'image', 'title', 'caption', 'alt_text', 'external_link', 'hover_text')

        return JsonResponse({'success': True, 'message': 'Carousel image retrieved successfully.', 'carousel_image': carousel_image}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def increment_carousel_image_click_count(request, carousel_image_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    try:
        carousel_image = CarouselImage.objects.get(id=carousel_image_id)
        carousel_image.click_count += 1
        carousel_image.save()
        return JsonResponse({'success': True, 'message': 'Click count incremented successfully.'}, status=200)
    except CarouselImage.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Carousel image not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################
########################>>>>>>>>>>>>>>>>>>>>>> Order Management API's <<<<<<<<<<<<<<<<<<<<<<<<<############################
##################################>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<##################################

@csrf_exempt
def list_orders(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication Header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token.'}, status=401)
        
        orders = Order.objects.all().values(
            'id',
            'user__first_name',
            'user__last_name',
            'total_price',
            'discount_amount',
            'is_gift',
            'status',
            'payment_status',
            'payment_method',
            'created_at'
            )
        
        orders_list = list(orders)
        
        return JsonResponse({'success': True, 'message': 'Orders retrieved successfully.', 'orders': orders_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)