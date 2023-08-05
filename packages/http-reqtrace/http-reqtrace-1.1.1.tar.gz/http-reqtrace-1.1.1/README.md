![PyPI](https://img.shields.io/pypi/v/http-reqtrace)
![PyPI - License](https://img.shields.io/pypi/l/http-reqtrace)
![PyPI - Downloads](https://img.shields.io/pypi/dm/http-reqtrace)
[![docker-image-version](https://img.shields.io/docker/v/julb/http-reqtrace.svg?sort=semver)](https://hub.docker.com/r/julb/http-reqtrace)
[![docker-image-size](https://img.shields.io/docker/image-size/julb/http-reqtrace.svg?sort=semver)](https://hub.docker.com/r/julb/http-reqtrace)
[![docker-pulls](https://img.shields.io/docker/pulls/julb/http-reqtrace.svg)](https://hub.docker.com/r/julb/http-reqtrace)

# http-reqtrace

## Description

The application starts a Web server which logs details of all incoming HTTP requests such as:

- HTTP Method & URL
- Query params
- Headers
- Body

The application accepts all HTTP methods and URIs.
The routing is defined like this:

- `/status/:statusCode` : return an HTTP response with status code **statusCode** and body `{"message":"OK|KO"}`
- `/**/*` : return an HTTP response with status code **200 OK** and body `{"message":"OK"}`
- `/metrics` : return Prometheus metrics regarding HTTP requests

Following query parameters are also supported:

- `?latencyInMs=60000` : wait for the given period in milliseconds before responding. This time cannot exceed 5 minuts.

This service can be used to :

- See very quickly what are the requests received and inspect their content.
- Have a quick way to simulate specific cases with particular HTTP response codes.

## How to use

### Starts the service

- Run container:

```bash
$ docker run -ti --name http-reqtrace -p 80:8080 -e PORT=8080 -u 65534:65534 julb/http-reqtrace:latest
```

Note: the `PORT` environment variable can be set to customize listening port.

### Request the service with any method, URI and parameters

```bash
$ curl http://localhost/context/uri?param1=value1&param2=value2 -H "Authorization: Bearer jwt"
{"statusCode": 200,"message":"OK"}
```

```bash
INFO in app: > [GET] HTTP/1.1 http://localhost/context/uri?param1=value1&param2=value2
INFO in app: >>     Header : Host : localhost
INFO in app: >>     Header : User-Agent : curl/7.54.0
INFO in app: >>     Header : Accept : */*
INFO in app: >>     Header : Authorization : Bearer jwt
INFO in app: >>     Query  : param1 : value1
INFO in app: >>     Query  : param2 : value2
INFO in app: >>     Body   : b''
INFO in app: < [ HTTP 200 ]
```

### Getting specific HTTP responses status codes

```bash
$ curl http://localhost/status/404 -H "Authorization: Bearer jwt"
{"statusCode":404,"message":"KO"}

$ curl http://localhost/status/500 -H "Authorization: Bearer jwt"
{"statusCode":500,"message":"KO"}
```

```bash
INFO in app: > [GET] HTTP/1.1 http://localhost/status/404
INFO in app: >>     Header : Host : localhost
INFO in app: >>     Header : User-Agent : curl/7.54.0
INFO in app: >>     Header : Accept : */*
INFO in app: >>     Header : Authorization : Bearer jwt
INFO in app: >>     Body   : b''
INFO in app: < [ HTTP 404 ]
INFO in app: > [GET] HTTP/1.1 http://localhost/status/500
INFO in app: >>     Header : Host : localhost
INFO in app: >>     Header : User-Agent : curl/7.54.0
INFO in app: >>     Header : Accept : */*
INFO in app: >>     Header : Authorization : Bearer jwt
INFO in app: >>     Body   : b''
INFO in app: < [ HTTP 500 ]
```

### Simulate latency

```bash
$ curl http://localhost/status/504?latencyInMs=60000
{"statusCode":504,"message":"KO"}
```

```bash
INFO in app: > [GET] HTTP/1.1 http://localhost/status/504?latencyInMs=60000
INFO in app: >>     Header : Host : localhost
INFO in app: >>     Header : User-Agent : curl/7.54.0
INFO in app: >>     Header : Accept : */*
INFO in app: >>     Query  : latencyInMs : 60000
INFO in app: >>     Body   : b''
INFO in app: << Waiting for timeout exhaust: 60000ms.
INFO in app: < [ HTTP 504 ]
```
