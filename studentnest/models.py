from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=2, choices=(('',''), ('M', 'Male'), ('F', 'Female')), default='', blank=True)
    age = models.IntegerField(null=True, blank=True)
    profile_images = models.ImageField(upload_to='profile-images', default='profile-images/profile-image-default.png', blank=True)
    university = models.CharField(max_length=100, default='', blank=True)
    major = models.CharField(max_length=100, default='', blank=True)
    is_publisher = models.BooleanField(default=False)
    last_applied = models.DateTimeField(default="1970-01-01T00:00+00:00")


class Property(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    type = models.CharField(max_length=10, choices=(('HOUSE', 'House'), ('APARTMENT', 'Apartment'), ('TOWNHOUSE', 'Townhouse')))
    min_bedroom_num = models.IntegerField(default=0)
    max_bedroom_num = models.IntegerField(default=0)
    description = models.TextField(max_length=1000)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.000000)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.000000)
    street = models.CharField(max_length=30)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=5)
    contact_person = models.CharField(max_length=20)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    publisher = models.ForeignKey(User)

    @property
    def reviews(self):
        return Review.objects.filter(property=self).order_by("-post_time")

    @property
    def highest_vote_review(self):
        return Review.objects.filter(property=self).order_by("-votes")[:1].get()

    @property
    def counts(self):
        return Review.objects.filter(property=self).count()

    @property
    def image_url(self):
        return "%s"%(reverse('studentnest:photo',args=[self.pk]))

    @property
    def keywords(self):
        return PropertyKeywords.objects.filter(property=self)

class PropertyKeywords(models.Model):
    property = models.ForeignKey(Property)
    keyword = models.CharField(max_length=30)
    count = models.IntegerField()


class PropertyImage(models.Model):
    property = models.ForeignKey(Property)
    property_image = models.ImageField(upload_to='property-images', default='property-images/property-image-default.png', blank=True)
    upload_time = models.DateTimeField(default="1970-01-01T00:00+00:00")


class Review(models.Model):
    author = models.ForeignKey(User)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    votes = models.IntegerField(default=0)
    content = models.TextField(max_length=500)
    post_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    property = models.ForeignKey(Property)
