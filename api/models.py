from django.db import models
import uuid
# Create your models here.


class Restaurant(models.Model):
    store_id = models.BigIntegerField(primary_key=True)
    timezone_str = models.CharField(max_length=40)
    
    def __str__(self) -> str:
        return str(self.store_id)

class BusinessHour(models.Model):
    store_id = models.BigIntegerField()
    day_of_week = models.SmallIntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    def __str__(self) -> str:
        return str(self.store_id)
    

class RestaurantStatus(models.Model):
    store_id = models.BigIntegerField()
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=8)

    def __str__(self) -> str:
        return str(self.store_id)



class Report(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateField(auto_now_add=True)

    file = models.FileField(null=True, blank=True)
    status = models.CharField(max_length=10, default="Generating")

    def __str__(self) -> str:
        return f"{str(self.created_at)} - {self.status}" 