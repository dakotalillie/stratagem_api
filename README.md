# Stratagem API

## Setup

This project requires that you have [Docker](https://docs.docker.com/v17.12/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

1. Install [pipenv](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)
2. Run `python -m pipenv install`. This will create a virtual environment and a `Pipfile.lock` file
3. Copy `env/db.env.sample` to `env/db.env` and set appropriate values for the variables within
4. Run `docker-compose up -d`

## Common Tasks

- To open a shell within the virtual environment, run `python -m pipenv shell`

This app is configured to work with PostgreSQL. To get started with it, you'll
need to add a new file at stratagem_api/config.py, and create a new dictionary
in that file called DATABASE_CONFIG. You can then fill this dictionary up with
the appropriate settings for your installation of PostgreSQL. A good tutorial
for this process can be found [here](https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation/).

## For Later

In docker, you need to run the following in order to run mysqlclient:

```
sudo apt-get install python3.7-dev libmysqlclient-dev
```