from django.db import models
from django.contrib.auth.models import User # This imports Django's built-in User model

# 1. The Room Model
class Room(models.Model):
    block_name = models.CharField(max_length=50) # e.g., "A", "C", "LHC" [cite: 39]
    room_name = models.CharField(max_length=50) # e.g., "LHC-04" [cite: 40]
    seating_capacity = models.IntegerField() # [cite: 41]
    is_available = models.BooleanField(default=True) # [cite: 42]

    # This makes the room show up with a readable name in the admin panel
    def __str__(self):
        return f"{self.block_name} Block - {self.room_name} (Capacity: {self.seating_capacity})"

# 2. The Booking Model
class Booking(models.Model):
    # Defining the only allowed purposes based on your requirements [cite: 19, 20, 21]
    PURPOSE_CHOICES = [
        ('OA', 'Online Assessment'),
        ('Interview', 'Interview'),
        ('PPT', 'Pre-Placement Talk'),
    ]

    # ForeignKeys link this booking to a specific User and a specific Room
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expected_participants = models.IntegerField()

    def __str__(self):
        return f"{self.room.room_name} booked by {self.user.username} on {self.date}"