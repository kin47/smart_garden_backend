from django.db import models

# Create your models here.
class Kit(models.Model):
    class Meta:
        db_table = 'kit'
        managed = False
    
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    name = models.CharField(db_column='name', max_length=255)
    password = models.CharField(db_column='password', max_length=255)

    def __str__(self) -> str:
        return self.name