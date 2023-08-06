from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from . import models as matialvarezs_time_sleep_models
from . import settings
import os


"""
@receiver(post_delete, sender = matialvarezs_time_sleep_models.Model)
def post_delete(sender, **kwargs):	
	try:
		instance = kwargs['instance']
		os.remove( os.path.join(settings.MEDIA_ROOT, instance.file.name) )
	except Exception as e:
		pass
"""


from django.dispatch import Signal
send_pending_time = Signal(providing_args=["data"])