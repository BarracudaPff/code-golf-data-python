class Migration(migrations.Migration):
	dependencies = [("djangocms_blog", "0027_post_date_featured")]
	if LooseVersion(aldryn_apphooks_config.__version__) > LooseVersion("0.3.0"):
		operations = [migrations.AlterField(model_name="blogconfig", name="namespace", field=models.CharField(default=None, max_length=100, unique=True, verbose_name="Instance namespace")), migrations.AlterField(model_name="blogconfig", name="type", field=models.CharField(max_length=100, verbose_name="Type"))]