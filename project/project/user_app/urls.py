from django.urls import path, include
from . import views
from .models import CarInstance


urlpatterns = [
    path('', views.index, name='index'),
    path('editprofile/', views.edit_profile, name='edit_profile'),
    path('deleteaccount/', views.user_delete_view, name='user_delete'),
    path('opinion/add/<str:pk>', views.create_opinion, name='opinion_create'),
    path('opinion/list', views.opinion_list, name='opinion_list'),
    path('reservation/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.reservations_list, name='reservations_list'),
    path('reservations/details/<str:pk>', views.ReservationDetailView.as_view(), name='reservation-details'),
    path('reservations/edit/<str:pk>', views.edit_reservation, name='edit_reservation'),
    path('reservations/accept/<str:pk>', views.reservation_accept_view, name='accept_reservation'),
    path('reservations/end/<str:pk>', views.reservation_end_view, name='end_reservation'),
    path('reservations/delivered/<str:pk>', views.reservation_progress_view, name='progress_reservation'),
    path('reservations/cancelreservation/<str:pk>/', views.reservation_delete_view, name='reservation-delete'),
    path('mycars/', views.UserCarsListView.as_view(), name='my-cars'),
    path('addcars/', views.CarCreateView.as_view(), name='add_cars'),
    path('deletecar/<str:pk>/', views.car_delete_view, name='car-delete'),
    path('addcar/', views.add_car_part_2, name='add_car_instance'),
    path('editcar<str:pk>/', views.edit_car, name='edit_car_instance'),
    path('ajax/load-cars/', views.load_cars, name='ajax_load_cars'),
    path('car/<str:pk>/', views.CarDetailView.as_view(), name='car-detail'),
]

