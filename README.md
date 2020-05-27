# LDD-OnelineWorkshop

### Start Local Server
```shell script
python3 manage.py runserver
```


### Database migration
```shell script
python3 manage.py migrate
```

To generate migration script for workshop application
```shell script
python3 manage.py makemigrations workshop
```

To view the SQL to be executed by the certain migrate script
```shell script
python3 manage.py sqlmigrate workshop [your migrate version]
```
For example: python3 manage.py sqlmigrate workshop 0001

### Run Python interactive terminal
```shell script
python3 manage.py shell
```

### Create Super User
```shell script
python3 manage.py createsuperuser
```
a super user can view and manage all the resources in this system on admin page. For local environment, it is serve on http://127.0.0.1:8000/admin/
