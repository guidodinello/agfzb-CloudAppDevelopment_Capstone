from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.db import IntegrityError
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_by_id, post_request, get_dealer_by_id

from .config_reader import ConfigReader
CONFIG = ConfigReader.getInstance().read_config()

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('djangoapp:index'))
        else:
            context['message'] = "Invalid username or password."
    return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        try:
            user = User.objects.create_user(username=username, 
                                            first_name=first_name, 
                                            last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")

        except IntegrityError:
            return render(request, 'djangoapp/registration.html', 
                        context={'message' : "User already exists."})

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', 
               context={"dealerships": get_dealers_from_cf()})

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {
            "reviews": get_dealer_reviews_by_id(dealer_id=dealer_id), 
            "dealer_id": dealer_id,
            "dealer_name": get_dealer_by_id(dealer_id)[0].full_name,
        }
        return render(request, 'djangoapp/dealer_details.html', context=context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    # only authenticated users can post reviews
    if not request.user.is_authenticated:
        return redirect(reverse('djangoapp:login'))
    
    if request.method == "GET":
        cars = CarModel.objects.filter(dealerId=dealer_id)
        print("CARS", cars)
        context = { 
            "dealer_id": dealer_id,
            "dealer_name": get_dealer_by_id(dealer_id)[0].full_name,
            "cars" : cars
        }
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        print("request POST data ", request.POST)
        id = hash(datetime.utcnow().isoformat())^hash(dealer_id)
        form = request.POST
        review = {
            "id": hash(datetime.utcnow().isoformat())^hash(dealer_id)^hash(form['username']),
            "name": form['username'],
            "dealership": dealer_id,
            "review": form['content'],
            "purchase": True if form['purchasecheck'] == 'on' else False,
        }
        if review['purchase']:
            car = CarModel.objects.get(id=form['car_id'][0])

            print("CAR MAKE", car.make.name)
            print("CAR MODEL", car.name)
            print("CAR YEAR", car.year)

            review['purchase_date'] = form['purchasedate']
            review['car_make'] = car.make.name
            review['car_model'] = car.name
            review['car_year'] = car.year.strftime("%Y")

        response = post_request(f"{CONFIG['API_ENDPOINT']}{CONFIG['POST_REVIEW']}", json_payload=review, dealerId=dealer_id)

        print(response.content)

        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)