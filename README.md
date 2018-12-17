# ITF Data-Sources

## Description
ITF Data app collect price information from cryptocurrency exchanges.

## Commands

* `$ python manage.py fetch_tickers` - fetch price and volume information from exchanges. 
* `$ python manage.py fetch_ohlc_tickers` - fetch open, high, low, close price and volume information from exchanges.

List of exchanges set in EXCHANGE_MARKETS variable. This commands collect information using [CCXT library](https://github.com/ccxt/ccxt/tree/master/python) and publish this info to sns topic (AWS_SNS_TOPIC_ARN variable).
Both commands filter out information for unsupported counter currencies (COUNTER_CURRENCIES variable) and info with very low 24hr volume (TICKERS_MINIMUM_USD_VOLUME variable).
For logging json dump from ccxt saved to the ExchangeData model.

* `$ python manage.py fetch_blockchain_stats` - fetch blockchain info from [blockchain.info](https://api.blockchain.info/stats) and save it to BlockchainStats model. We don't send this info to SNS.


## Environment Setup

1. Install Prerequisites
 - python3.6
 - pip
 - [mysqlclient prerequisites](https://github.com/PyMySQL/mysqlclient-python#install) (`sudo apt-get install python-dev libmysqlclient-dev python3-dev`)
 - if connecting to Postgres: `postgresql-server-dev-x.x` 
 - [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) 
 - [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
 - run commands to create virtual env
    ```
    $ mkvirtualenv --python=/usr/local/bin/python3 ITF`
    $ workon ITF
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
 
