from django.conf import settings

def dadata_keys(request):
    return {
        'DADATA_API_KEY': settings.DADATA_API_KEY,
    }