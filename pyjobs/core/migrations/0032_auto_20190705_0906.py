def generated_premium_dates(apps, schema_editor):
	Job = apps.get_model("core", "Job")
	for job in Job.objects.all():
		if job.premium == True:
			job.premium_at = job.created_at
		job.save()
class Migration(migrations.Migration):
	dependencies = [("core", "0031_job_premium_at")]
	operations = [migrations.RunPython(generated_premium_dates)]