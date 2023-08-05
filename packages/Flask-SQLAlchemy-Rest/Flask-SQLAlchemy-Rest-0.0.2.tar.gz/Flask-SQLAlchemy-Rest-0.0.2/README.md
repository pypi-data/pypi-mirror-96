Flask-SQLAlchemy-Rest
================

Flask-SQLAlchemy-Rest is an extension for Flask that can easily generate rest api with Flask-SQLAlchemy.

Installing
----------
Install and update using `pip`:
    pip install Flask-SQLAlchemy-Rest

Example
-------
This is an example application:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_rest.rest import Rest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

```
