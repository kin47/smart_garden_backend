from django.db import models

# Create your models here.
class Kit(models.Model):
    class Meta:
        db_table = 'kit'
        managed = False
    
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    name = models.CharField(db_column='name', max_length=255)
    password = models.CharField(db_column='password', max_length=255)
    is_auto_pump = models.BooleanField(db_column='is_auto_pump')
    is_auto_light = models.BooleanField(db_column='is_auto_light')
    light_threshold = models.IntegerField(db_column='light_threshold')
    pump_threshold = models.IntegerField(db_column='pump_threshold')
    
    def __str__(self) -> str:
        return self.name
    
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