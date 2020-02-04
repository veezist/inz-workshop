from datetime import date

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import ListView, CreateView, UpdateView

from .forms import SignUpForm, EditProfileForm, ReservationForm, CarForm, CarInstanceForm, EditReservationForm
from .models import Car, CarInstance, User, Reservation, Model, Brand
import logging
import json as simplejson

logger = logging.getLogger('mylogger')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_cars = Car.objects.all().count()
    num_instances = CarInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = CarInstance.objects.filter(status__exact='a').count()
    num_old_cars = CarInstance.objects.filter(year_of_production__lte=2000).count()
    # The 'all()' is implied by default.    
    num_users = User.objects.count()

    context = {
        'num_cars': num_cars,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_users': num_users,
        'num_old_cars': num_old_cars
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


@login_required
def edit_profile(request):
    user = request.user

    data_dict = {'username': user.username, 'email': user.email}
    update_user_form = EditProfileForm(initial=data_dict, instance=user)

    path = request.path.split('/')[1]
    redirect_path = path
    path = path.title()

    context = {
        "title": "Setting",
        "update_user_form": update_user_form,
        "path": path,
        "redirect_path": redirect_path,
    }

    if request.POST:
        user_form = EditProfileForm(request.POST, instance=user)

        if user_form.is_valid():
            instance = user_form.save(commit=False)
            passwd = user_form.cleaned_data.get("password")

            if passwd:
                instance.password = make_password(password=passwd,
                                                  salt='salt', )
            instance.save()

            return redirect(reverse('my-cars'))

    return render(request, "user_app/edit_profile.html", context)


@login_required
def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            formholder = form.save(commit=False)
            formholder.user = request.user  # use your own profile here
            formholder.save()

            return redirect('reservations_list')

    else:
        logger.info("Simple 2info")
        form = ReservationForm(request.POST, request.FILES, user=request.user)
    return render(request, 'user_app/createreservation.html', {'form': form})


@login_required
def edit_reservation(request, pk):
    user = request.user

    reservation = Reservation.objects.get(pk=pk)
    data_dict = {'description': reservation.description,
                 'car_instance': reservation.car_instance,
                 'datetime_from': reservation.datetime_from}
    update_reservation_form = EditReservationForm(initial=data_dict, instance=reservation)

    path = request.path.split('/')[1]
    redirect_path = path
    path = path.title()

    context = {
        "title": "Setting",
        "reservation": reservation,
        "form": update_reservation_form,
        "path": path,
        "redirect_path": redirect_path,
    }

    if request.POST:
        reservation_form = EditReservationForm(request.POST, instance=reservation)

        if reservation_form.is_valid():
            instance = reservation_form.save(commit=False)
            instance.save()

            return redirect(reverse('reservations_list'))

    return render(request, "user_app/edit_reservation.html", context)


@login_required
def reservations_list(request):
    if request.user.is_staff:

        queryset = Reservation.objects.all().exclude(staff=False).order_by('datetime_from')
        context = {
            "queryset": queryset,
            "title": request.user,
        }

        return render(request, 'staff/reservations_list.html', context)
    else:
        queryset = Reservation.objects.filter(user=request.user).order_by('datetime_from')
        context = {
            "queryset": queryset,
            "title": request.user,
        }

        return render(request, 'user_app/reservations_list.html', context)

@login_required
def user_car_list(request):
    queryset = CarInstance.objects.filter(owner=request.user)
    queryset2 = Car.objects.all()
    context = {
        "queryset": queryset,
        "queryset2": queryset2,
        "title": request.user,
    }

    return render(request, 'user_app/carinstance_list_user.html', context)


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car
    template_name = 'user_app/carinstance_detail.html'
    context_object_name = 'car'

    def get_queryset(self):
        return Car.objects.filter()


class UserCarsListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = Car
    template_name = 'user_app/carinstance_list_user.html'
    paginate_by = 10
    context_object_name = 'cars'

    def get_queryset(self):
        return CarInstance.objects.filter(owner=self.request.user)


@login_required
def add_cars(request):
    cars = Car.objects.all()

    return render(request, 'user_app/car_form.html', {'cars': cars})


def load_cars(request):
    brand_id = request.GET.get('brand')
    models = Model.objects.filter(brand_id=brand_id).order_by('name')
    return render(request, 'user_app/car_dropdown_list_options.html', {'models': models})


class CarCreateView(LoginRequiredMixin, generic.FormView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy('add_car_instance')
    brand = Brand.objects.get(name='Ford')
    car = Car.objects.get(brand=brand)
    logger.info(car)
    template_name = 'user_app/car_form.html'

    def form_valid(self, form):
        car = form.save(commit=False)
        self.request.session['car_brand'] = car.brand.name
        self.request.session['car_model'] = car.model.name
        # Here, we would record the user's interest using the message
        # passed in form.cleaned_data['message']
        return super(CarCreateView, self).form_valid(form)


@login_required
def add_car_part_2(request):
    model = Model.objects.get(name=request.session['car_model'])
    car = Car.objects.get(model=model)
    if request.method == 'POST':

        form = CarInstanceForm(request.POST)
        if form.is_valid():
            formholder = form.save(commit=False)
            formholder.owner = request.user  # use your own profile here
            formholder.car = car
            formholder.save()

            return redirect('reservations_list')

    else:
        form = CarInstanceForm(request.POST)

    return render(request, 'user_app/carinstance_form.html', {'form': form})


@login_required()
def car_delete_view(request, pk):
    car = get_object_or_404(CarInstance, pk=pk)

    if request.method == "POST":
        car.delete()
        messages.success(request, "Car successfully deleted!")
        return redirect('my-cars')

    context = {'car': car}

    return render(request, 'user_app/car_delete_view.html', context)


@login_required()
def reservation_delete_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Reservation successfully deleted!")
        return redirect('my-cars')

    context = {'reservation': reservation}

    return render(request, 'user_app/reservation_delete_view.html', context)


@login_required()
def user_delete_view(request):
    user = request.user

    if request.method == "POST":
        user.delete()
        messages.success(request, "Usunięto konto")
        return redirect('signup')

    context = {'user': user}

    return render(request, 'user_app/user_delete_view.html', context)



