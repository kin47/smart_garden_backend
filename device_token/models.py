from django.db import models
from django.conf import settings
from authentication.models import User

class DeviceToken(models.Model):
    class Meta:
        db_table = 'device_token'
        managed = False
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    access_token = models.CharField(max_length=500, db_column='access_token')
    device_token = models.CharField(max_length=500, db_column='device_token')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')

    def __str__(self):
        return f"{self.device_token}"