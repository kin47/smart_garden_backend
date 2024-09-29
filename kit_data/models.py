from django.db import models

# Create your models here.
class KitData(models.Model):
    class Meta:
        db_table = 'kit_data'
        managed = True
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    temperature = models.FloatField(db_column='temperature')
    humidity = models.FloatField(db_column='humidity')
    soil_moisture = models.FloatField(db_column='soil_moisture')
    light = models.FloatField(db_column='light')
    time = models.DateTimeField(db_column='time')
    
    def __str__(self):
        return f"{self.time}: {self.temperature}℃ - {self.humidity}% - {self.soil_moisture}% - {self.light}lux"