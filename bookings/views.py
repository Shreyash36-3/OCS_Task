from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from .models import Room, Booking
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    # If the user is already logged in, don't make them log in again!
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        return redirect('/book/')

    if request.method == "POST":
        # Get what the user typed in the form
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Django checks if this is a real user in the database
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user) # This logs them in safely
            
            # The Routing Logic: Admin vs Normal User
            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('/book/')
        else:
            # Login failed
            return render(request, 'bookings/login.html', {'error': 'Invalid username or password.'})

    # If they just visited the page, show them the blank form
    return render(request, 'bookings/login.html')

def custom_logout_view(request):
    logout(request)
    return redirect('/')

def process_booking_request(user, room_id, req_date, req_start, req_end, req_purpose, req_participants):
    # 1. Authorization Check
    if not user.is_authenticated:
        raise ValidationError("You must be logged in to book a room.")

    # 2. Prevent Race Conditions (The Pro Move)
    with transaction.atomic():
        room = get_object_or_404(Room.objects.select_for_update(), id=room_id)

        # 3. Capacity Check
        if req_participants > room.seating_capacity:
            raise ValidationError(f"Error: Room capacity is {room.seating_capacity}.")

        # 4. The Time Conflict Check
        overlapping_bookings = Booking.objects.filter(
            room=room,
            date=req_date,
            start_time__lt=req_end,  # Existing starts before new ends
            end_time__gt=req_start   # Existing ends after new starts
        )

        if overlapping_bookings.exists():
            raise ValidationError("Conflict: This room is already booked during this time.")

        # 5. If it passes all checks, create the booking!
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
    # Grabs every booking, ordered by date and time
    schedule = Booking.objects.all().order_by('date', 'start_time')
    
    context = {
        'bookings': schedule
    }
    
    return render(request, 'bookings/all_bookings.html', context)   

@login_required(login_url='/')
def book_room_view(request):
    context = {}

    if request.method == "POST":
        # Check which button the user clicked (Search vs Book)
        action = request.POST.get('action')

        if action == 'search':
            # 1. Extract the search criteria
            req_date = request.POST.get('date')
            req_start = request.POST.get('start_time')
            req_end = request.POST.get('end_time')
            req_purpose = request.POST.get('purpose')
            
            try:
                req_participants = int(request.POST.get('participants', 1))
            except ValueError:
                req_participants = 1

            # 2. Find rooms with conflicting bookings
            conflicting_bookings = Booking.objects.filter(
                date=req_date,
                start_time__lt=req_end,
                end_time__gt=req_start
            ).values_list('room_id', flat=True)

            # 3. Filter rooms: Must have enough capacity AND not be in the conflicting list
            available_rooms = Room.objects.filter(
                seating_capacity__gte=req_participants
            ).exclude(id__in=conflicting_bookings)

            # 4. Pass the available rooms and the original search data back to the template
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
                # Call the bulletproof engine using the selected room and carried-over data
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

    # Render the HTML page
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