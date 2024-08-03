from django.db import models

class Carousel(models.Model):
    #A carousel for the main page

    title = models.CharField(max_length=50, default='Carousel Title')
    image_url = models.URLField(max_length=200)
    background_color = models.CharField(max_length=50, default='#000000')
    alt = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Card(models.Model):
    #A card for the main page

    title = models.CharField(max_length=50)
    image_url = models.URLField(max_length=200)
    alt = models.CharField(max_length=100)
    url = models.URLField(max_length=100)

    def __str__(self):
        return self.title
