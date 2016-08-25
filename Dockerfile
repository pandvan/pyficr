FROM python:3.5.1-onbuild
EXPOSE 5000
CMD [ "/bin/sh", "./runInDocker.sh"]
