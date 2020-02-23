from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.http import request
from django.urls import reverse_lazy
from django.utils import timezone

from .models import User, Reservation, CarInstance, Car, Model, Brand, Opinion


class CarInstanceForm(forms.ModelForm):
    year_of_production = forms.CharField()

    class Meta:
        model = CarInstance
        fields = ['year_of_production']


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('brand', 'model',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'].queryset = Model.objects.none()
        self.fields['brand'].label = "Marka"
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = Model.objects.filter(brand_id=brand_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset


class DateTimeInput(forms.DateTimeInput):
    input_type = 'date'

def validate_price(price):
    if price < 0:
        raise ValidationError("Kwota nie może być ujemna")

def validate_date(date):
    if date < timezone.now().date():
        raise ValidationError("Wybrana data nie może być z przeszłości")

class AddOpinionForm(forms.ModelForm):
    opinion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea ', 'placeholder': 'Zostaw opinie'}), required=True)
    
    class Meta:
        model = Opinion
        fields = ['opinion']


class EditCarForm(forms.ModelForm):
  
    CAR_STATUS = (
        ('W naprawie', 'W naprawie'),
        ('U właściciela', 'U właściciela'),
        ('Gotowy do odbioru', 'Gotowy do odbioru'),
    )

    timing_gear_range = forms.IntegerField(min_value=0,required=False)
    technical_review_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'input', 'id': 'review-field'}),required=False)
    status = forms.ChoiceField(choices=CAR_STATUS)

    class Meta:
        model = CarInstance
        fields = ['timing_gear_range', 'technical_review_date', 'status']
    
    def __init__(self, *args, **kwargs):
        super(EditCarForm, self).__init__(*args, **kwargs)
        self.fields['timing_gear_range'].label = "Przebieg wymiany rozrządu"
        self.fields['technical_review_date'].label = "Data ostatniego przeglądu"
        for key in self.fields:
            self.fields[key].required = False


class ReservationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # using kwargs
        self._user = kwargs.pop('user')
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields['car_instance'].queryset = CarInstance.objects.filter(owner=self._user)

    datetime_from = forms.DateField(
        widget=DateTimeInput(
            attrs={'class': 'input', 'id': 'reserve-field', 'placeholder': 'YYYY-MM-DD '}),
        validators=[validate_date])
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea ', 'id': 'reserve-field', 'placeholder': 'Podaj opis'}))
    car_instance = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'input ', 'id': 'reserve-field'}),
                                          queryset=None, empty_label='Wybierz auto')

    class Meta:
        model = Reservation
        fields = ['datetime_from', 'description', 'car_instance', ]


class EditReservationForm(forms.ModelForm):
  
    datetime_from = forms.DateField(
        widget=DateTimeInput(attrs={'class': 'input', 'id': 'reserve-field'}), validators=[validate_date])
    car_instance = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'input ', 'id': 'reserve-field'}),
                                          queryset=None, empty_label='Wybierz auto')

    class Meta:
        model = Reservation
        fields = ['datetime_from', 'description', 'car_instance']

    
    def __init__(self, *args, **kwargs):
        super(EditReservationForm, self).__init__(*args, **kwargs)
        self.fields['car_instance'].queryset = CarInstance.objects.filter(owner=self.instance.user)
        self.fields['datetime_from'].label = "Zmień datę rezerwacji"
        self.fields['description'].label = "Opis"
        self.fields['car_instance'].label = "Zmień auto"
        for key in self.fields:
            self.fields[key].required = False

class AcceptReservationForm(forms.ModelForm):
    datetime_to = forms.DateField(
        widget=DateTimeInput(
            attrs={'class': 'input', 'id': 'reserve-field', 'placeholder': 'YYYY-MM-DD '}),
        validators=[validate_date])

    class Meta:
       model = Reservation
       fields = ['datetime_to']     

class EndReservationForm(forms.ModelForm):
    price = forms.IntegerField(validators=[validate_price])
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea ', 'placeholder': 'Zostaw komentarz'}), required=False)
    

    class Meta:
       model = Reservation
       fields = ['price', 'comment'] 


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'password': forms.PasswordInput(),
        }
        fields = ['username', 'password', 'email']

    # Don't want to modify blank setting inside models (doing so will break normal validation in admin site)
    # The redefined constructor won't harm any functionality.
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Opcjonalnie.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Opcjonalnie.')
    email = forms.EmailField(max_length=254, help_text='Obowiązkowe.')
    is_staff = forms.CheckboxInput()
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2','is_staff')

