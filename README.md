# OpenclassroomsProject12
Backend REST API for Epic Events CRM app.
The project is defined in the specifications (documentation directory).

<p align="center">
  <img src="img/logo_light.png#gh-light-mode-only" alt="logo-light" />
  <img src="img/logo_dark.png#gh-dark-mode-only" alt="logo-dark" />
</p>

### Tech & Tools
<p align="center">
  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.11.4-blue?style=for-the-badge&logo=python&logoColor=FFD43B" alt="python-badge">
  </a>
  <a href="https://www.djangoproject.com">
    <img src="https://img.shields.io/badge/Django-4.2.4-092E20?style=for-the-badge&logo=django&logoColor=green" alt="django-badge">
  </a>
    <a href="https://www.django-rest-framework.org/">
    <img src="https://img.shields.io/badge/DRF-3.14-ff1709?style=for-the-badge&logo=django&logoColor=white" alt="drf-badge">
  </a>
  </a>
    <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-15.3-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="postgresql-badge">
  </a>
  <a href="https://documenter.getpostman.com/view/24942161/2s9XxvSufo">
    <img src="https://img.shields.io/badge/Postman-Docs-f06732?style=for-the-badge&logo=postman&logoColor=white" alt="postman-badge">
  </a>
  <a href="https://code.visualstudio.com/">
    <img src="https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?&style=for-the-badge&logo=visual-studio-code&logoColor=white" alt="vscode-badge">
  </a>
</p>

### Clone Project
```sh
git clone https://github.com/immacora/OpenclassroomsProject12
```
```sh
cd OpenclassroomsProject12
```

### Active environment and Install dependencies using pip (Windows 11)
```sh
py -m venv .venv
```
```sh
.venv\Scripts\activate
```
```sh
pip install -r requirements.txt
```

### Create PostgreSQL database
Install [PostgreSQL 15.3](https://www.postgresql.org/download/).

[Create a new PostgreSQL database](https://www.postgresqltutorial.com/postgresql-getting-started/connect-to-postgresql-database/) for the project.

### Settings and Environment Variables
Create a .env file in the project's root folder.
Paste all the following variables with your own values

```sh
# django
SECRET_KEY=YourSecretKey
ALLOWED_HOSTS=YourAllowedHosts # test production: *
CORS_ALLOWED_ORIGINS=YourAllowedHTTP # ex: http://localhost:8000
CSRF_TRUSTED_ORIGINS=YourTrustedHTTP # ex: http://localhost:8000

# postgresql
POSTGRES_DB_NAME=YourDBname
POSTGRES_USER=YourUserName
POSTGRES_PASSWORD=YourDBpassword
POSTGRES_PORT=YourPort # ex: 5432

# simplejwt
ACCESS_TOKEN_LIFETIME=NumberOfLifetimeMinutes # ex: 5
REFRESH_TOKEN_LIFETIME=NumberOfLifetimeDays # ex: 1
```

### Project Setup and Run

```sh
py manage.py makemigrations accounts
py manage.py makemigrations locations
py manage.py makemigrations clients
py manage.py makemigrations contracts
py manage.py makemigrations events
```

```sh
py manage.py migrate
```

```sh
py manage.py loaddata employees.json
```

```sh
py manage.py runserver
```

### Login
* email : adminTEST@email.com
* password : 123456789!

### Account particularity

In the API, the creation, update and deletion of a user are linked to that of the employee. You must perform these actions via the employee account.


## Postman Documentation

https://documenter.getpostman.com/view/24942161/2s9XxvSufo



### Run tests

`pytest`


### Generate flake8 report

`flake8 --format=html --htmldir=flake-report`
