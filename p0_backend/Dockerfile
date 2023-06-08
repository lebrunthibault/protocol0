# -- Base image --
#FROM mcr.microsoft.com/windows-cssc/python3.7.2nanoserver:ltsc2022 as base
#mcr.microsoft.com/windows-cssc/python3.7.2servercore:ltsc2022
FROM python:3.7-windowsservercore-1809 as base

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade --user pip
RUN pip install poetry

# make RUN exit with 0 to avoid error
RUN powershell -c "poetry install; exit 0"


# -- Core --
FROM base as core

#COPY . /app/

WORKDIR /app


# -- Development --
FROM core as development

# Un-privileged user running the application

#ENTRYPOINT ["powershell.exe"]
#CMD = ["python.exe"]