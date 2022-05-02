from pyexpat import model
from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    ACTIVE_CHOICES = (
    ("Active", "Active"),
    ("Inactive", "InActive"),

    )
    
    name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    joineddate  = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20,choices = ACTIVE_CHOICES,default = 'Active')
    loginkey = models.CharField(null=True,blank=True,max_length=20)
    def __str__(self):
        return f"{self.name }"

class order(models.Model):
    
    customer = models.ForeignKey('Customer',on_delete=models.CASCADE)
    ordertag = models.IntegerField()
    race = models.CharField(max_length=500)
    orderdetail = models.CharField(max_length=2000)
    total = models.CharField(max_length=100)
    orderdate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.customer.name }"