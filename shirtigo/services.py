# here we create the main logic for the API calls
import requests
import logging
from django.conf import settings
from .models import ShirtigoOrder, ShirtigoAPILog

logger = logging.getLogger(__name__)