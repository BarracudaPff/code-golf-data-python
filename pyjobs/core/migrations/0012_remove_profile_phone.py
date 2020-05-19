from __future__ import unicode_literals
from django.db import migrations
class Migration(migrations.Migration):
	dependencies = [("core", "0011_auto_20180413_2320")]
	operations = [migrations.RemoveField(model_name="profile", name="phone")]