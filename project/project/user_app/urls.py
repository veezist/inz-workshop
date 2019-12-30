from django.urls import path, include
from . import views
from .models import CarInstance


urlpatterns = [
    path('', views.index, name='index'),
    path('editprofile/', views.edit_profile, name='edit_profile'),
    path('deleteaccount/', views.user_delete_view, name='user_delete'),
    path('reservation/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.reservations_list, name='reservations_list'),
    path('reservations/edit/<str:pk>', views.edit_reservation, name='edit_reservation'),
    path('cancelreservation/<str:pk>/', views.reservation_delete_view, name='reservation-delete'),
    path('mycars/', views.UserCarsListView.as_view(), name='my-cars'),
    path('addcars/', views.CarCreateView.as_view(), name='add_cars'),
    path('deletecar/<str:pk>/', views.car_delete_view, name='car-delete'),
    path('addcar/', views.add_car_part_2, name='add_car_instance'),
    path('ajax/load-cars/', views.load_cars, name='ajax_load_cars'),
    path('car/<str:pk>/', views.CarDetailView.as_view(), name='car-detail'),
]

