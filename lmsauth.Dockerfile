FROM ubuntu:xenial as base

# Install system requirements
RUN apt update && \
    # Global requirements
    DEBIAN_FRONTEND=noninteractive apt install -y language-pack-en git build-essential software-properties-common curl git-core libxml2-dev libxslt1-dev libmysqlclient-dev libxmlsec1-dev libfreetype6-dev libssl-dev swig gcc g++ \
    # openedx requirements
    gettext gfortran graphviz libgraphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng-dev libsqlite3-dev libxml2-dev libxmlsec1-dev libxslt1-dev ntp pkg-config python3.5 python3-pip python3-dev \
    -qy && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /edx/app/edx-platform/edx-platform

COPY ./lms/envs /edx/app/edx-platform/edx-platform/lms/envs
COPY ./requirements/lmsauth.txt /edx/app/edx-platform/edx-platform/requirements/lmsauth.txt
COPY ./common/lib/safe_lxml /edx/app/edx-platform/edx-platform/common/lib/safe_lxml
COPY ./openedx/core/djangoapps/user_authn /edx/app/edx-platform/edx-platform/openedx/core/djangoapps/user_authn

ENV CONFIG_ROOT /edx/etc/
ENV PATH /edx/app/edx-platform/edx-platform/bin:${PATH}

RUN pip install setuptools==39.0.1 pip==9.0.3
RUN pip install -r requirements/lmsauth.txt

RUN mkdir -p /edx/etc/
COPY ./lmsauth.yaml /edx/etc/lmsauth.yaml

EXPOSE 18999


FROM base as lmsauth
ENV SERVICE_VARIANT lms
ENV LMS_CFG /edx/etc/lmsauth.yaml
CMD gunicorn -c /edx/app/edx-platform/edx-platform/lms/docker_lms_gunicorn_conf.py --name lms --bind=0.0.0.0:18999 --max-requests=1000 --access-logfile - lmsauth.wsgi:application

