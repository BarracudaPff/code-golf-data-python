from __future__ import unicode_literals
from django.db import migrations, models
class Migration(migrations.Migration):
	dependencies = [("djangocms_blog", "0029_post_related")]
	operations = [migrations.AlterField(model_name="posttranslation", name="slug", field=models.SlugField(allow_unicode=True, blank=True, db_index=False, max_length=255, verbose_name="slug"))]