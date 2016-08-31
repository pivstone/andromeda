from .base import *

__author__ = 'xbeco'

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# EMail Block
ADMINS = (('pivstone', 'pivstone@gmail.com),)

EMAIL_HOST = config['email']['host']
EMAIL_PORT = config['email']['port']
EMAIL_HOST_USER = config['email']['user']
EMAIL_HOST_PASSWORD = config['email']['password']
EMAIL_USE_SSL = config['email']['use_ssl']
EMAIL_SUBJECT_PREFIX = config['email']['subject_prefix']

SERVER_EMAIL = config['email']['user']

DEFAULT_FROM_EMAIL = config['email']['user']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ' %(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/registry.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
        },

        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
