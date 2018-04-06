import os

import dj_database_url

from settings import LOCAL, PRODUCTION, STAGE


# AWS S3 info
if PRODUCTION:
    BUCKET_NAME = "intelligenttrading-s3-production"
else:
    BUCKET_NAME = "intelligenttrading-s3-stage"

HOST_URL = 'http://' + BUCKET_NAME + '.s3.amazonaws.com'


if not LOCAL:
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    MEDIA_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    AWS_STATIC_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    STATIC_ROOT = STATIC_URL = AWS_STATIC_URL
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    #DATABASES = {'default': dj_database_url.config()}
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }

# AWS
AWS_OPTIONS = {
    'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID', ''),
    'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
    'AWS_REGION': 'us-east-1',
}

if PRODUCTION:
    AWS_SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:983584755688:itt-sns-data-core-production'
else:
    AWS_SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:983584755688:itt-sns-data-core-stage'
