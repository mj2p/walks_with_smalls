FROM python:3.8-slim AS base

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    TZ=Etc/UTC \
    PYTHONBUFFERED=1

RUN apt update; \
    apt upgrade -y; \
    apt install -y locales; \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen; \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone; \
    apt install -y pipenv \
        gdal-bin \
        libgdal-dev \
        python3-gdal \
        binutils \
        libproj-dev \
        gettext-base; \
    apt-get clean autoclean; \
    apt-get autoremove --yes; \
    rm -rf /var/lib/{apt,dpkg,cache,log}* /var/cache/debconf/templates.dat*; \
    mkdir -p /code

WORKDIR /code

FROM woolysammoth/walks_with_smalls:base AS prod
COPY ./ /code/
RUN pipenv sync

FROM woolysammoth/walks_with_smalls:base AS dev
RUN rm -rf /code/*
COPY Pipfile Pipfile.lock /code/
RUN pipenv sync --dev
