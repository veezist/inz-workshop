from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.http import request
from django.urls import reverse_lazy
from django.utils import timezone

from .models import User, Reservation, CarInstance, Car, Model, Brand


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

        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = Model.objects.filter(brand_id=brand_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset


class DateTimeInput(forms.DateTimeInput):
    input_type = 'date'


def validate_date(date):
    if date < timezone.now().date():
        raise ValidationError("Wybrana data nie może być z przeszłości")


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

    class Meta:
        model = Reservation

        fields = ['datetime_from', 'description', 'car_instance']

    # Don't want to modify blank setting inside models (doing so will break normal validation in admin site)
    # The redefined constructor won't harm any functionality.
    def __init__(self, *args, **kwargs):
        super(EditReservationForm, self).__init__(*args, **kwargs)
        self.fields['datetime_from'].label = ""
        self.fields['description'].label = "Opis"
        self.fields['car_instance'].label = "Zmień auto"
        for key in self.fields:
            self.fields[key].required = False


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
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
