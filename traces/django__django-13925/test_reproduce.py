from django.db import models

class Entity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)

class User(Entity):
    email = models.EmailField()