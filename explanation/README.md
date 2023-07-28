<a href="#class-diagram">class-diagram</a> | <a href="#flowchart">flowchart</a> | <a href="#pseudocode">pseudocode</a>

## Class Diagram
![Class Diagram](https://raw.githubusercontent.com/FakeCoder01/loop/main/explanation/class_diagram.png)

## Flowchart
![Flowchar Diagram](https://raw.githubusercontent.com/FakeCoder01/loop/main/explanation/flowchart.png)

## Pseudocode 
```
function generate_report(report_id):
    current_timestamp = get current timestamp in UTC
    seven_days_ago = current_timestamp - 7 days

    store_status_data = fetch RestaurantStatus data from the last 7 days

    if store_status_data is empty:
        set report status as "No Data"
        exit

    store_hours_data = fetch BusinessHour data for all stores
    store_timezone_data = fetch Restaurant data for all stores

    business_hours_dict = create an empty dictionary to store business hours for each store

    for each row in store_hours_data:
        store_id = row.store_id
        day_of_week = row.day_of_week
        start_time_local = row.start_time_local
        end_time_local = row.end_time_local

        add (day_of_week, start_time_local, end_time_local) to business_hours_dict[store_id]

    report_data = create an empty list to store report data

    for each store_id in unique store IDs in store_status_data:
        store_data = filter store_status_data by store_id

        timezone_str = get the timezone string from store_timezone_data for the current store_id

        convert timestamp data in store_data to the local timezone using timezone_str

        current_day = get the day of the week for current_timestamp

        business_start, business_end = get business hours from business_hours_dict for the current store_id and current_day

        if business_start or business_end is None:
            assume store is open 24*7
            set business_start = minimum timestamp time
            set business_end = maximum timestamp time

        calculate uptime and downtime durations for the last hour, last day, and last week
        append the calculated durations and store_id to report_data

    create a CSV file named report_id.csv
    write the report_data to the CSV file
    set report status as "Done"
    END
```

```
function calculate_uptime_downtime(status_data, start_time, end_time):
    convert start_time and end_time to Timestamp objects

    business_hours_data = filter status_data within the specified start_time and end_time

    total_duration = calculate the total duration between start_time and end_time in seconds

    uptime_duration = 0
    previous_timestamp = None

    for each row in business_hours_data:
        if row['status'] is 'active':
            current_timestamp = row['timestamp_local']
            if previous_timestamp is not None:
                calculate the time difference between current_timestamp and previous_timestamp
                add the time difference to uptime_duration
            Set previous_timestamp as current_timestamp

    downtime_duration = total_duration - uptime_duration

    return uptime_duration and downtime_duration

```

