from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from .models import Room, Booking
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    #Check if user is already logged in or not
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        return redirect('/book/')

    if request.method == "POST":
        # Get what the user chose in the form
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        #check is the user is real or not
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user) # This logs them in safely
            
            # The Routing Logic diffrent for admin and user
            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('/book/')
        else:
            # Login failed
            return render(request, 'bookings/login.html', {'error': 'Invalid username or password.'})

    return render(request, 'bookings/login.html')

def custom_logout_view(request):
    logout(request)
    return redirect('/')

def process_booking_request(user, room_id, req_date, req_start, req_end, req_purpose, req_participants):
    #Authorization Check
    if not user.is_authenticated:
        raise ValidationError("You must be logged in to book a room.")

    # Prevent Race Conditions
    with transaction.atomic():
        room = get_object_or_404(Room.objects.select_for_update(), id=room_id)

        #Capacity Check
        if req_participants > room.seating_capacity:
            raise ValidationError(f"Error: Room capacity is {room.seating_capacity}.")

        #The Time Conflict Check
        overlapping_bookings = Booking.objects.filter(
            room=room,
            date=req_date,
            start_time__lt=req_end,  # Existing starts before new ends
            end_time__gt=req_start   # Existing ends after new starts
        )

        if overlapping_bookings.exists():
            raise ValidationError("Conflict: This room is already booked during this time.")

        #If it passes all checks, create booking
        new_booking = Booking.objects.create(
            user=user,
            room=room,
            date=req_date,
            start_time=req_start,
            end_time=req_end,
            purpose=req_purpose,
            expected_participants=req_participants
        )
        
        return new_booking

@login_required(login_url='/') 
def all_bookings_view(request):
    #Grabs every booking, ordered by date and time
    schedule = Booking.objects.all().order_by('date', 'start_time')
    
    context = {
        'bookings': schedule
    }
    
    return render(request, 'bookings/all_bookings.html', context)   

@login_required(login_url='/')
def book_room_view(request):
    context = {}

    if request.method == "POST":
        # Check which button the user clicked search or book
        action = request.POST.get('action')

        if action == 'search':
            #Extract the search criteria
            req_date = request.POST.get('date')
            req_start = request.POST.get('start_time')
            req_end = request.POST.get('end_time')
            req_purpose = request.POST.get('purpose')
            
            try:
                req_participants = int(request.POST.get('participants', 1))
            except ValueError:
                req_participants = 1

            #Find rooms with conflicting bookings
            conflicting_bookings = Booking.objects.filter(
                date=req_date,
                start_time__lt=req_end,
                end_time__gt=req_start
            ).values_list('room_id', flat=True)

            #Filter rooms: Must have enough capacity AND not be in the conflicting list
            available_rooms = Room.objects.filter(
                seating_capacity__gte=req_participants
            ).exclude(id__in=conflicting_bookings)

            #Pass the available rooms and the original search data back to the template
            context.update({
                'available_rooms': available_rooms,
                'searched': True,
                'search_date': req_date,
                'search_start': req_start,
                'search_end': req_end,
                'search_participants': req_participants,
                'search_purpose': req_purpose
            })

        elif action == 'book':
            try:
                process_booking_request(
                    user=request.user,
                    room_id=request.POST.get('room_id'),
                    req_date=request.POST.get('date'),
                    req_start=request.POST.get('start_time'),
                    req_end=request.POST.get('end_time'),
                    req_purpose=request.POST.get('purpose'),
                    req_participants=int(request.POST.get('participants'))
                )
                context['success'] = "Booking confirmed successfully!"
            except ValidationError as e:
                context['error'] = e.message

    return render(request, 'bookings/book_room.html', context)

@staff_member_required(login_url='/') 
def custom_dashboard_view(request):
    all_rooms = Room.objects.all()
    all_bookings = Booking.objects.all().order_by('-date')

    context = {
        'rooms': all_rooms,
        'bookings': all_bookings
    }
    return render(request, 'bookings/custom_dashboard.html', context)