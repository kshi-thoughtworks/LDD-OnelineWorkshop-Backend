cp deploy/prod.settings.py server/settings.py
source ../.env
echo "user and pwd:"
echo ${LDD_DB_USER}
echo ${LDD_DB_PASSWORD}
docker build --build-arg USER=${LDD_DB_USER} --build-arg PW=${LDD_DB_PASSWORD} -t ldd-app .
docker image prune
