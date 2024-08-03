from django.conf import settings
from pathlib import Path
import os
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def global_settings(request):
	return {
		'BRAND_NAME': settings.BRAND_NAME,
		'CEO_NAME': settings.CEO_NAME,
		'ADDRESS': settings.ADDRESS,
		'PHONE_NUMBER': settings.PHONE_NUMBER,
		'BUSINESS_REGISTRATION_NUMBER': settings.BUSINESS_REGISTRATION_NUMBER,
		'ECOMMERCE_REGISTRATION_NUMBER': settings.ECOMMERCE_REGISTRATION_NUMBER,
		'CPO_NAME': settings.CPO_NAME,
	}

def vite_asset(request):
	manifest_path = BASE_DIR / 'static/dist/.vite/manifest.json'
	with open(manifest_path, 'r') as f:
		manifest = json.load(f)
	return {
		'vite_asset': lambda asset_name: manifest[asset_name]['file']
	}

