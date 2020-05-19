class Migration(migrations.Migration):
	dependencies = [("djangocms_blog", "0014_auto_20160215_1331")]
	operations = [migrations.AlterField(model_name="post", name="date_published", field=models.DateTimeField(blank=True, null=True, verbose_name="published since"))]