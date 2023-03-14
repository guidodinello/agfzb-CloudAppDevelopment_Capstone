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


# <HINT> Create a plain Python class `DealerReview` to hold review data
