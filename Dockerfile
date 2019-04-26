FROM python:3.7

WORKDIR /usr/src/app

RUN python -m pip install pipenv --user

COPY . .
ENV PATH=/root/.local/bin:$PATH
RUN pipenv install

CMD ./bin/start_docker.sh
