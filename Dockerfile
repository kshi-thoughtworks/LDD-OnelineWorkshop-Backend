FROM python:3.7
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt
RUN rm -rf /usr/src/app
COPY . /usr/src/app
RUN date '+%F %H:%M:%S' > /usr/src/app/version
RUN chmod +x ./start.sh
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8088"]
