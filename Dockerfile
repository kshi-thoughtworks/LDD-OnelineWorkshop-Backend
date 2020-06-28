FROM python:3.7
RUN mkdir -p /usr/src/appy
ARG USER=user
ARG PW=pwd
ENV LDD_DB_USER=$USER
ENV LDD_DB_PASSWORD=$PW
WORKDIR /usr/src/app
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt
RUN rm -rf /usr/src/app
COPY . /usr/src/app
RUN date '+%F %H:%M:%S' > /usr/src/app/version
RUN chmod +x ./start.sh
CMD [ "sh", "./start.sh"]
