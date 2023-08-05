django-mssql-backend-aad
========================

*django-mssql-backend-aad* is a fork of
`django-pyodbc-azure <https://pypi.org/project/django-pyodbc-azure/>`__ 
with backported changes from `django-azure-sql-backend <https://github.com/langholz/django-azure-sql-backend>`__

Dependencies
------------

-  Django 2.2 or newer
-  pyodbc 3.0 or newer
-  msal 1.5.1 or newver

Installation
------------

1. Install pyodbc and Django

2. Install django-mssql-backend-aad ::

    pip install django-mssql-backend-aad

3. Now you can point the ``ENGINE`` setting in the settings file used by
   your Django application or project to the ``'sql_server.pyodbc'``
   module path ::

    'ENGINE': 'sql_server.pyodbc'

