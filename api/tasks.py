from .models import Restaurant, RestaurantStatus, BusinessHour, Report
from celery import shared_task
import pandas as pd
import pytz, csv
from django.utils import timezone
from datetime import timedelta

def convert_to_local_timezone(timestamp, timezone_str):
    try:
        tz = pytz.timezone(timezone_str)
        return timestamp.astimezone(tz)
    except pytz.UnknownTimeZoneError:
        # edge case, if timezone_str is not present
        default_tz = pytz.timezone("America/Chicago")
        return timestamp.astimezone(default_tz)

def calculate_uptime_downtime(status_data, start_time, end_time):
    # convert start_time and end_time to Timestamp objects
    start_time = pd.Timestamp(start_time)
    end_time = pd.Timestamp(end_time)
    
    # filter data within the specified start_time and end_time
    business_hours_data = status_data[
        (status_data['timestamp_local'] >= start_time) &
        (status_data['timestamp_local'] <= end_time)
    ]
    
    # calculate uptime and downtime durations
    total_duration = (end_time - start_time).total_seconds()
    uptime_duration = business_hours_data[business_hours_data['status'] == 'active']['timestamp_local'].diff().sum().total_seconds()
    downtime_duration = total_duration - uptime_duration
    return uptime_duration, downtime_duration


@shared_task
def generate_report(report_id):

    current_timestamp = pd.Timestamp.now(tz='UTC')  # get the current timestamp in UTC

    # fetch data from the database, explicitly including 'store_id' in the columns to retrieve
    seven_days_ago = timezone.now() - timedelta(days=7)
    store_status_data = pd.DataFrame.from_records(
        RestaurantStatus.objects.filter(timestamp_utc__gte=seven_days_ago).values('store_id', 'timestamp_utc', 'status')
    )

    # check if store_status_data is empty
    if store_status_data.empty:
        report = Report.objects.get(id=report_id)
        report.status = "No data"
        report.save()
        return

    # fetch data from the database
    store_hours_data = pd.DataFrame.from_records(BusinessHour.objects.all().values())
    store_timezone_data = pd.DataFrame.from_records(Restaurant.objects.all().values())

    # create a dictionary to store business hours for each store
    business_hours_dict = {}
    for row in store_hours_data.itertuples():
        store_id = row.store_id
        day_of_week = row.day_of_week
        start_time_local = row.start_time_local
        end_time_local = row.end_time_local
        if store_id not in business_hours_dict:
            business_hours_dict[store_id] = {}
        business_hours_dict[store_id][day_of_week] = (start_time_local, end_time_local)

    report = Report.objects.get(id=report_id)

    report_data = []
    # loop through each store to calculate the report data
    for store_id in store_status_data['store_id'].unique():
        store_data = store_status_data[store_status_data['store_id'] == store_id]

        # get the timezone for the store if available, otherwise use a default timezone
        timezone_row = store_timezone_data[store_timezone_data['store_id'] == store_id]
        if timezone_row.empty:
            # if timezone data not available, use  America/Chicago
            timezone_str = "America/Chicago"
        else:
            timezone_str = timezone_row['timezone_str'].iloc[0]

        # convert the timestamp to the store's local timezone
        store_data['timestamp_local'] = pd.to_datetime(store_data['timestamp_utc']).dt.tz_convert(timezone_str)

        # get business hours for the store from the dictionary
        current_day = current_timestamp.day_of_week
        business_start, business_end = business_hours_dict.get(store_id, {}).get(current_day, (None, None))

        # if business hours are not available, assume the store is open 24*7
        if business_start is None or business_end is None:
            business_start = pd.Timestamp.min.time()
            business_end = pd.Timestamp.max.time()

        # convert business_start and business_end to Timestamp objects
        business_start = pd.Timestamp.combine(current_timestamp.date(), business_start)
        business_end = pd.Timestamp.combine(current_timestamp.date(), business_end)

        # calculate uptime and downtime for the last hour, last day, and last week
        uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(store_data, current_timestamp - pd.DateOffset(hours=1), current_timestamp)
        uptime_last_day, downtime_last_day = calculate_uptime_downtime(store_data, current_timestamp - pd.DateOffset(days=1), current_timestamp)
        uptime_last_week, downtime_last_week = calculate_uptime_downtime(store_data, current_timestamp - pd.DateOffset(days=7), current_timestamp)


        report_data.append({
            'store_id': store_id,
            'uptime_last_hour': int(uptime_last_hour) // 60,  # minutes
            'uptime_last_day': int(uptime_last_day) // 3600,  # hours
            'uptime_last_week': int(uptime_last_week) // 3600,
            'downtime_last_hour': int(downtime_last_hour) // 60,
            'downtime_last_day': int(downtime_last_day) // 3600,
            'downtime_last_week': int(downtime_last_week) // 3600
        })
    
    file_path = f'static/reports/{report_id}.csv'
    with open(file_path, mode='w', newline='') as csv_file:
        fieldnames = ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week',
                      'downtime_last_hour', 'downtime_last_day', 'downtime_last_week']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for row in report_data:
            writer.writerow(row)

    report.status = "Done"
    report.save()
