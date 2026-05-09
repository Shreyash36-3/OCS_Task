from django.urls import path
from . import views
urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.custom_dashboard_view, name='custom_dashboard'),
    path('book/', views.book_room_view, name='book_room'),
    path('logout/', views.custom_logout_view, name='custom_logout'),
    path('schedule/', views.all_bookings_view, name='schedule'),
]