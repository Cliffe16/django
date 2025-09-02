from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=10, default='active')
    
    class Meta:
        #Specify the schema
        db_table = 'credentials"."dashboard_user'
    
class SugarPrice(models.Model):
    date = models.DateField(primary_key=True, unique=True, db_column='Date')
    amount = models.FloatField(db_column='Amount')
    rate = models.FloatField(db_column='Rate')
    
    class Meta:
        db_table = 'sugarprices"."sugarprices'
    
    def __str__(self):
        return f"{self.date}: {self.amount}"

class UploadHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    admin_username = models.CharField(max_length=150)
    filename = models.CharField(max_length=255)
    rows_added = models.IntegerField()
    
    class Meta:
        db_table = 'credentials"."uploadhistory'
