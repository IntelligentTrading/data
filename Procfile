release: python manage.py migrate
web: gunicorn settings.wsgi
tickers: python manage.py fetch_tickers
blstats: python manage.py fetch_blockchain_stats