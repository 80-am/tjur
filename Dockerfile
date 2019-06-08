FROM python:3.7-alpine
COPY ./tjur/tjur.py /
CMD ["python", "./tjur.py"]
