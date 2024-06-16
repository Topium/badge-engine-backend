from os import environ
MYSQL_USER=environ.get('MYSQL_USER')
MYSQL_PASSWORD=environ.get('MYSQL_PASSWORD')
MYSQL_HOST=environ.get('MYSQL_HOST')
MYSQL_DB=environ.get('MYSQL_DB')
JWT_SECRET_KEY=environ.get('JWT_SECRET_KEY')