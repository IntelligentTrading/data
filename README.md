# ITT Data-Sources


## Environment Setup

1. Install Prerequisites
 - python3.5 
 - pip
 - [mysqlclient prerequisites](https://github.com/PyMySQL/mysqlclient-python#install) (`sudo apt-get install python-dev libmysqlclient-dev python3-dev`)
 - if connecting to Postgres: `postgresql-server-dev-x.x` 
 - [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) 
 - [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
 - run commands to create virtual env
    ```
    $ mkvirtualenv --python=/usr/local/bin/python3 ITT`
    $ workon ITT
    ```
 
2. Clone and setup Django env
 - clone https://github.com/IntelligentTrading/data-sources.git
 - `$ cd data-sources`
 - `$ pip install -r requirements.txt`

3. Local Env Settings
 - make a copy of `settings/local_settings_template.py` and save as `settings/local_settings.py`
 - add private keys and passwords as needed

3. Connect to Database
 - install PostgreSQL server and create local database
 - run `$ python manage.py migrate` to setup schemas in local database
 - AND/OR
 - connect to read-only Amazon Aurora DB
 - set database connection settings in your `settings/local_settings.py`
 
4. Run Local Server
 - `$ python manage.py runserver`
 - open [http://localhost:8000/](http://localhost:8000/) (`127.0.0.1` does not work)
 - view logs and debug as needed

5. Run Worker Services
 - `$ python manage.py poloniex_polling`
 - ...
 
6. Query DB in Shell
 - `$ python manage.py shell`
 
    ```
    > from apps.channel.models import ExchangeData
    > print(ExchangeData.objects.first().data)
    ```
 
