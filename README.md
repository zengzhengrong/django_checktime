# Build Setup

```
git clone https://github.com/zengzhengrong/django_checktime.git

cd ./django_checktime

pipenv install or source /path/to/ENV/bin/activate
pip install -r ./requirements.txt
cd ./src

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser
...
...
...

python manage.py  runserver
```

# Features

- Allow check-in and check-out
- Check-out Set Delay
- Only allow check-in and check-out on the same day
- Check-in or check-out password form validation
- Search for previous history
- User Authentication 

# Settings Conf
Set delay (min) default 1min
```
TIME_DELTA_MIN = 1
```
Checkin not use password validation (default True)
```
PASS_CHECKIN = True
```
Only once time in same day (default False)
```
CHECK_IN_TODAY = False
```
Check required password (default True)
Set false ,mean both not required
```
CHECK_REQUIRED_PASSWORD = True
```
One of activity need validation,you also can set like this (checkin required ,another not required):
```
CHECK_REQUIRED_PASSWORD = {'checkin':True,'checkout':False}
```
Per page number of history(default 8) ,range from 0-10 and Multiple of 2
```
PER_PAGE_NUMBER = 8
```
