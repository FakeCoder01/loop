import csv, pytz
from django.core.management.base import BaseCommand
from api.models import Restaurant, BusinessHour, RestaurantStatus
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):

        with open('data/Restaurant.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            restaurants = [
                Restaurant(store_id=row[0], timezone_str=row[1])
                for row in reader
            ]
            Restaurant.objects.bulk_create(restaurants)

        with open('data/RestaurantStatus.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            restaurant_statuses = []
            for row in reader:
                try:
                    datetime_obj = datetime.strptime(row[2].rsplit(' ', 1)[0], '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    datetime_obj = datetime.strptime(row[2].rsplit(' ', 1)[0], '%Y-%m-%d %H:%M:%S')
                timestamp = datetime_obj.replace(tzinfo=pytz.UTC)
                restaurant_statuses.append(RestaurantStatus(store_id=row[0], timestamp_utc=timestamp, status=row[1]))
            RestaurantStatus.objects.bulk_create(restaurant_statuses)


        with open('data/BusinessHour.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)

            business_hours = [
                BusinessHour(store_id=row[0], day_of_week=row[1], start_time_local=row[2], end_time_local=row[3])
                for row in reader
            ]
            BusinessHour.objects.bulk_create(business_hours)
