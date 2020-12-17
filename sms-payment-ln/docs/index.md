# sms-payment-ln

[![Build Status](https://travis-ci.org/y-martinez/sms-payment-ln.svg?branch=master)](https://travis-ci.org/y-martinez/sms-payment-ln)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Payment system with Lightning Network. Check out the project's [documentation](http://y-martinez.github.io/sms-payment-ln/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Initialize the project

Start the dev server for local development:

```bash
docker-compose up
```

Create a superuser to login to the admin:

```bash
docker-compose run --rm web ./manage.py createsuperuser
```
