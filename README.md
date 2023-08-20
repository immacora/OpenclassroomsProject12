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

### Active environment and Install dependencies (Windows 11)
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

```sh
Create a new PostgreSQL database and replace the settings with your own (settings.py file).

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "YourDBname",
        "USER": "YourUserName",
        "PASSWORD": "YourDBpassword",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
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

### First Login
* email : adminTEST@email.com
* password : 123456789!

Recommendations

Use the test admin employee account to create a new admin employee then delete the test employee account.

### Account particularity

The deletion of a user is linked to that of the employee. You must remove an employee to remove his linked user.


## Postman Documentation

https://documenter.getpostman.com/view/24942161/2s9XxvSufo



### Run tests

`py manage.py test`


### Run flake8 report

`flake8 --format=html --htmldir=flake-report`
