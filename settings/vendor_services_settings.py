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

    DATABASES = {'default': dj_database_url.config()}
