## Loop Assignment

1. Install python dependencies
```
pip install -r requirements.txt
```

2. Run migartions
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

3. Copy the CSV files to the data folder. Then import the data by running
```
python manage.py import_data
```

4. Run Celery [change the BROKER_URL in settings.py to Redis/RabbitMQ server]
```
celery -A loop worker --loglevel=info
```

5. Run the django server
```
python manage.py runserver
```

Telegram : <a href="https://t.me/hitkolkata" title="Telegram ID">@hitkolkata</a>