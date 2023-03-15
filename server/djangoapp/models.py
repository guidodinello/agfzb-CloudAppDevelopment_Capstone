from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model 
class CarMake(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    # - Any other fields you would like to include in car make model
    def __str__(self):
        """method to print a car make object"""
        return self.name


# <HINT> Create a Car Model model 
class CarModel(models.Model):
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
# - Name
    name = models.CharField(max_length=200)
# - Dealer id, used to refer a dealer created in cloudant database
    dealerId = models.IntegerField()
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
    TYPE_CHOICES = [ 
        ('sedan', 'Sedan'), 
        ('suv', 'SUV'), 
        ('pickup', 'Pickup'),
        ('roadster', 'Roadster'),
        ('coupe', 'Coupe'),
        ('hatchback', 'Hatchback'),
        ('minivan', 'Minivan'),
        ('supercar', 'Supercar'), 
    ]
    type = models.CharField( null=False, max_length=20, choices=TYPE_CHOICES)
# - Year (DateField)
    year = models.DateField()
# - Any other fields you would like to include in car model
    def __str__(self):
        """ method to print a car make object """
        return str(self.make) + self.type + self.name



# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, id, city, state, st, address, zip, lat, long, short_name, full_name):
        # Dealer id
        self.id = id
        # Dealer city
        self.city = city
        # Dealer state
        self.state = state
        # Dealer state abbreviation
        self.st = st
        # Dealer address
        self.address = address
        # Dealer zip
        self.zip = zip
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer Full Name
        self.full_name = full_name

    def __str__(self):
        return "Dealer name: " + self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview():

    def __init__(self, review, dealership, id, name, purchase, purchase_date, make, model, year, sentiment):
        self.review = review
        self.dealership = dealership
        self.id = id
        self.name = name
        self.sentiment = sentiment
        if purchase:
            self.purchase = True
            self.purchase_date = purchase_date
            self.make = make
            self.model = model
            self.year = year

    def __str__(self):
        return f"\
            For dealer: {self.name}\
            Review: {self.review}\
            Sentiment: {self.sentiment}"