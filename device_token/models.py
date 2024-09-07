from django.db import models
from django.conf import settings

class DeviceToken(models.Model):
    class Meta:
        db_table = 'device_token'
        managed = False
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, db_column='token')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')

    def __str__(self):
        return f"{self.user.username} - {self.token}"