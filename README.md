# Shorturl 

This is the source code of [http://163.gs](http://163.gs). 

163.gs is written by Python with Tornado. 

## Generate shorten url

``` 
curl -d "url=http://EverET.org" http://163.gs/short/
```

## Install
Copy `etc/config.py.sample` to `etc/config.py` and modify it if necessary.

## Simple 
And you can run execute `./main.py` to run it.

## By supervisor
Or copy `etc/supervisord.conf.sample` as supervisord config file, and run with supervisord.

