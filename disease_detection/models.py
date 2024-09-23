from django.db import models
from authentication.models import User

# Create your models here.
class Tree(models.Model):
    class Meta:
        db_table = 'tree'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    class Meta:
        db_table = 'disease'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    tree_id = models.ForeignKey(Tree, on_delete=models.CASCADE, db_column='tree_id')
    disease_name = models.CharField(max_length=255, db_column='disease_name')
    treatment = models.TextField(db_column='treatment')
    reference = models.TextField(db_column='reference')
    
    def __str__(self):
        return self.name
    
class PredictHistory(models.Model):
    class Meta:
        db_table = 'predict_history'
        managed = False
    
    id = models.AutoField(primary_key=True, db_column='id', unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    disease_id = models.ForeignKey(Disease, on_delete=models.CASCADE, db_column='disease_id')
    image = models.CharField(max_length=255, db_column='image')
    send_at = models.DateTimeField(db_column='send_at')