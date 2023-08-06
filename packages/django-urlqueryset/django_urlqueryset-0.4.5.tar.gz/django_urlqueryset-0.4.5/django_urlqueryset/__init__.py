import pkg_resources
from .urlqueryset import UrlQuerySet
from .fields import UrlFileField, UrlImageField

__all__ = ('UrlQuerySet', 'UrlFileField', 'UrlImageField', 'VERSION')

__version__ = pkg_resources.get_distribution(__name__).version

VERSION = __version__.split('.')

default_app_config = 'django_urlqueryset.apps.CheckConfig'

