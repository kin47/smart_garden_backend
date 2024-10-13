from django.db import models
from authentication.models import User

# Create your models here.
class Chat(models.Model):
    class Meta:
        db_table = 'chat'
        managed = True
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    message = models.TextField(db_column='message')
    time = models.DateTimeField(db_column='time')
    sender = models.BooleanField(db_column='sender', default=False)
    is_user_read = models.BooleanField(db_column='is_user_read', default=False)
    is_admin_read = models.BooleanField(db_column='is_admin_read', default=False)
    
    def __str__(self):
        return f"{self.user.name} - {self.title}"