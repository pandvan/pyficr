FROM python:3.5.1-onbuild
EXPOSE 5000
CMD [ "python", "./pyficr/app.py"]

