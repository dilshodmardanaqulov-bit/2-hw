from django.db import models


class Enemy(models.Model):
    name = models.CharField(max_length=100)
    health = models.IntegerField()
    attack_power = models.IntegerField()
    description = models.TextField()
    
    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=[
        ('potion', 'Potion'),
        ('weapon', 'Weapon'),
        ('shield', 'Shield'),
        ('treasure', 'Treasure'),
    ])
    effect_value = models.IntegerField(default=0)
    description = models.TextField()
    
    def __str__(self):
        return self.name
