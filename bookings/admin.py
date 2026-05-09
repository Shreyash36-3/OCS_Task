from django.contrib import admin
from .models import Room,Booking
from django.contrib.auth.models import Group

admin.site.unregister(Group)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'block_name', 'seating_capacity')
    search_fields = ('room_name', 'block_name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'date', 'start_time', 'end_time', 'purpose')
    list_filter = ('date', 'purpose')
