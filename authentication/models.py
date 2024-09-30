from django.db import models
from kit.models import Kit

# Create your models here.
class User(models.Model):
    class Meta:
        db_table = 'user'
        managed = False
    
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    email = models.CharField(db_column='email', unique=True, max_length=255)
    password = models.CharField(db_column='password', max_length=255)
    name = models.CharField(db_column='name', unique=True, max_length=255)
    phone_number = models.CharField(db_column='phone_number', unique=True, max_length=255)
    avatar = models.CharField(db_column='avatar', max_length=255)
    cover_image = models.CharField(db_column='cover_image', max_length=255)
    can_predict_disease = models.BooleanField(db_column='can_predict_disease', default=True)
    can_receive_noti = models.BooleanField(db_column='can_receive_noti', default=True)
    can_auto_control = models.BooleanField(db_column='can_auto_control', default=True)
    is_admin = models.BooleanField(db_column='is_admin', default=False)
    kit_id = models.ForeignKey(Kit, on_delete=models.CASCADE, db_column='kit_id')
    is_verified = models.BooleanField(db_column='is_verified', default=False)

    def __str__(self) -> str:
        return self.email
    

class UserSession(models.Model):
    class Meta:
        db_table = 'user_session'
        managed = False
    
    access_token = models.CharField(max_length=625, unique=True, db_column='access_token', primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(db_column='created_at')
    deleted_at = models.DateTimeField(db_column='deleted_at')
    
    def __str__(self) -> str:
        return self.access_token