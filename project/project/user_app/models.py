from __future__ import unicode_literals
from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid


class CarInstance(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    car = models.ForeignKey('Car', on_delete=models.SET_NULL, null=True)
    year_of_production = models.IntegerField()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    technical_review_date = models.DateField(blank=True, null=True)
    timing_gear_range = models.IntegerField(blank=True,null=True)
    CAR_STATUS = (
        ('W naprawie', 'W naprawie'),
        ('U właściciela', 'U właściciela'),
        ('Gotowy do odbioru', 'Gotowy do odbioru'),
    )
    status = models.CharField(
        max_length=20,
        choices=CAR_STATUS,
        blank=True,
        default='U właciciela',
        help_text='Car availability',
    )

    def __str__(self):
        return f'{self.car.brand} {self.car.model}'


class Car(models.Model):
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey('Model', on_delete=models.SET_NULL, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    def __str__(self):
        return f'{self.brand} {self.model}'


class Brand(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Model(models.Model):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class User(AbstractUser):
    reservations_made = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.username}'

class Opinion(models.Model):
    opinion = models.TextField(blank=True,null=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    staff = models.ForeignKey('User', on_delete=models.CASCADE, null=True, related_name='staffopinion')
    datetime = models.DateTimeField(auto_now_add=True)

class Reservation(models.Model):
    datetime_from = models.DateField()
    description = models.TextField()
    datetime_to = models.DateField(blank=True, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    staff = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='staff')
    car_instance = models.ForeignKey('CarInstance', on_delete=models.CASCADE, null=True)
    progress = models.IntegerField(default=-2)
    price = models.IntegerField(default=0)
    comment = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.datetime_from} {self.description}'

    def __str__(self):
        return f'{self.car.brand} {self.car.model}'
