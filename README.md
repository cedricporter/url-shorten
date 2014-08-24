# 163.gs url shorten service

This is the source code of [http://163.gs](http://163.gs). 

163.gs is written by Python with Tornado. 

## Generate shorten url interface

``` 
curl -d "url=http://EverET.org" http://163.gs/short/
```

Return short url if success. You can check whether the response is started with `http:` to determine if it is successful.

If fail, it returns the error message.

## Install
Copy `etc/config.py.sample` to `etc/config.py` and modify it if necessary.

## Dependency
Run `pip install -r requirements.txt` to install dependency. We advise you to install them in virtualenv.

```
$ virtualenv .env
$ source .env/bin/activate
$ pip install -r requirements.txt
```

## Simple deploy
And you can run execute `./main.py` to run it.

## By supervisor
Copy `etc/supervisor/163.gs.conf` to your supervisord config folder, and modify it accordingly. And run it with supervisord.

