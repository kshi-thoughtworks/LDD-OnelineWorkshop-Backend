cp deploy/prod.settings.py server/settings.py
docker build -t ldd-app .
docker image prune
