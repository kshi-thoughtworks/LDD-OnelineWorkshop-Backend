cp deploy/prod.settings.py server/settings.py
docker build --build-arg USER=${LDD_DB_USER} --build-arg PW=${LDD_DB_PASSWORD} -t ldd-app .
docker image prune
