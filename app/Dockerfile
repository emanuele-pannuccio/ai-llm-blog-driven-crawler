FROM python:3.12-bullseye
WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . /app/

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
#
ENTRYPOINT [ "/entrypoint.sh" ]