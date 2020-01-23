The file structure is based off of
https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/

Installation Instructions
===========================

1) Verify that Python 3 is installed.
2) Install the required modules.
    1) In a terminal, CD into `/usdaars_primerlib` and type `pip install .`
        * If Python 2 is also installed, use `pip3 install .` instead.
    2) CD into `/usdaars_primerlibweb` and type `pip install .`
        * If Python 2 is also installed, use `pip3 install .` instead.

3) Create a .cgi file in `/cgi-bin/` named `primers.cgi` with the following content:
```
#! /path/to/python3
from wsgiref.handlers import CGIHandler
import primerlibweb

CGIHandler().run(primerlibweb.create_app())
```

4) Add the following Script Alias in `httpd.conf`. This means that anytime someone visits `/primers`, the `primer.cgi` file will handle the request. Here, `{SRVROOT}` is the installation location of Apache. By default, this is `C:\Apache24` on Windows.
`ScriptAlias /primers "${SRVROOT}/cgi-bin/primers.cgi"`

5) By default, Apache listens on port 80. To change this (eg. to run on localhost), change `Listen 80` to `Listen 8080` (or a different unused port) in `httpd.conf`.

6) Verify that Apache is working by visiting `localhost:8080/`. It should return a page that says **It works!**

7) Access the application by visiting `localhost:8080/primers`.
