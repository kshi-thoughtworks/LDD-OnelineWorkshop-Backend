# LDD-OnelineWorkshop

Python 3.7 is used in this project

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
A super user can view and manage all the resources in this system on admin page. For local environment, it is served on http://127.0.0.1:8000/admin/

### Deployment
As currently for the MVP on production we only have one instance, so we use Sqlite as storage for now.
```shell script
docker build -t ldd-app .
docker run -it --rm -p 8080:8080 --name djapp ldd-app:latest
```
Then access `http://[The server ip]:8080/` in the browser
