# pull official base image
FROM python:3.8.5-slim-buster

# set work directory
WORKDIR /py-tools

#TZ
ENV TZ Asia/Shanghai

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements file
COPY ./requirements.txt /py-tools/requirements.txt

# install dependencies
RUN set -eux \
    && pip install -r /py-tools/requirements.txt -i https://pypi.douban.com/simple/\
    && pip install akshare -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com  --upgrade \
    && rm -rf /root/.cache/pip

# copy project
COPY . /py-tools

# RUN APP
CMD ["python", "./app/main.py"]