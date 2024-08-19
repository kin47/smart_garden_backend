from django.db import models

# Create your models here.
class Store(models.Model):
    class Meta:
        db_table = 'store'
        managed = True
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self) -> str:
        return self.name