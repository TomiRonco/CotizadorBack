from django.db import models

# Create your models here.
class UvaValue(models.Model):
    date = models.DateField(unique=True)
    value = models.FloatField()

class DollarValue(models.Model):
    date = models.DateField(unique=True)
    buy_value = models.DecimalField(max_digits=10, decimal_places=2)
    sell_value = models.DecimalField(max_digits=10, decimal_places=2)