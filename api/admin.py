from django.contrib import admin
from .models import Restaurant, RestaurantStatus, BusinessHour, Report
# Register your models here.

admin.site.register(Restaurant)
admin.site.register(BusinessHour)
admin.site.register(RestaurantStatus)
admin.site.register(Report)
