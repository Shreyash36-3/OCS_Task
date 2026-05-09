from django.db import models
from django.contrib.auth.models import User # This imports Django's built-in User model

#The Room Model
class Room(models.Model):
    block_name = models.CharField(max_length=50) 
    room_name = models.CharField(max_length=50) 
    seating_capacity = models.IntegerField() 
    is_available = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.block_name} Block - {self.room_name} (Capacity: {self.seating_capacity})"

#The Booking Model
class Booking(models.Model):
    
    PURPOSE_CHOICES = [
        ('OA', 'Online Assessment'),
        ('Interview', 'Interview'),
        ('PPT', 'Pre-Placement Talk'),
    ]

    # ForeignKeys
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expected_participants = models.IntegerField()

    def __str__(self):
        return f"{self.room.room_name} booked by {self.user.username} on {self.date}"