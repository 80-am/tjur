FROM python:3.7-alpine
COPY ./ /tmp
WORKDIR /tmp
RUN apk add --update curl gcc g++ libxml2-dev
RUN pip install -U pip
RUN pip install -r requirements.txt
CMD ["python", "./tjur/tjur.py"]
