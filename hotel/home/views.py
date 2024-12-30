from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate , login
from .models import Amenities , Hotel , HotelBooking
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


# Create your views here.



def home(request):
    amenities_objs = Amenities.objects.all()
    hotels_objs = Hotel.objects.all()

    sort = request.GET.get('sort')
    search = request.GET.get('search')
    amenities = request.GET.getlist('amenities')
    if sort:
        if sort == 'price-asc':
            hotels_objs = hotels_objs.order_by('hotel_price')
        elif sort == 'price-dsc':
            hotels_objs = hotels_objs.order_by('-hotel_price')
    
    if search:
        hotels_objs = hotels_objs.filter(
            Q(hotel_name__icontains = search)|
            Q(description__icontains = search))
        
    if len(amenities):
                hotels_objs = hotels_objs.filter(amenities__amenity_name__in = amenities).distinct()

       
    context = {
        'amenities_objs' : amenities_objs, 'hotels_objs' : hotels_objs, 'sort' : sort, 'search' : search, 'amenities' : amenities,
        'current_page': 'home'
    }
    return render(request , 'home.html', context)


def check_booking(start_date  , end_date ,uid , room_count):
    qs = HotelBooking.objects.filter(
        start_date__lte=start_date,
        end_date__gte=end_date,
        hotel__uid = uid
        )
    
    if len(qs) >= room_count:
        return False
    
    return True


def hotel_detail(request,uid):
    hotel_obj = Hotel.objects.get(uid = uid)

    if request.method == 'POST':
        checkin = request.POST.get('checkin')
        checkout= request.POST.get('checkout')
        hotel = Hotel.objects.get(uid = uid)
        if not check_booking(checkin ,checkout  , uid , hotel.room_count):
            messages.warning(request, 'Hotel is already booked in these dates ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        HotelBooking.objects.create(hotel=hotel , user = request.user , start_date=checkin
        , end_date = checkout , booking_type  = 'Pre Paid')
        
        messages.success(request, 'Your booking has been saved')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

        
    
    return render(request , 'hotel_detail.html' ,{
        'hotels_obj' :hotel_obj,
        'current_page': 'hotels'
    })     


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user_obj = authenticate(username=username , password=password)
        if not user_obj:
            messages.warning(request, 'Invalid password ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        login(request , user_obj)
        return redirect('home')

        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'login.html', {
        'current_page': 'login'  # Add this line
    })


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username)

        if user_obj.exists():
            messages.warning(request, "Username already exists")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user = User.objects.create(username = username)
        user.set_password(password)
        user.save() 
        return redirect('home')
    return render(request, 'register.html', {
        'current_page': 'register'  # Add this line
    })

def contact_page(request):
    return render(request, 'contact.html', {
        'current_page': 'contact'  # Add this line
    })

def about_page(request):
    return render(request, 'about.html', {
        'current_page': 'about'  # Add this line
    })

def hotels(request):
    hotels_objs = Hotel.objects.all()
    return render(request, 'hotels.html', {
        'hotels_objs' : hotels_objs,
        'current_page': 'hotels'  # Add this line

    })

@login_required(login_url='login_page')
def profile_page(request):
    # Get all bookings for the current logged-in user
    user_bookings = HotelBooking.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'bookings': user_bookings,
        'current_page': 'profile'
    })



def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


