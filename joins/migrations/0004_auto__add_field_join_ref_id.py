class Migration(SchemaMigration):
	def forwards(self, orm):
		db.add_column(u"joins_join", "ref_id", self.gf("django.db.models.fields.CharField")(default="ABC", max_length=120), keep_default=False)
	def backwards(self, orm):
		db.delete_column(u"joins_join", "ref_id")
	models = {u"joins.join": {"Meta": {"object_name": "Join"}, "email": ("django.db.models.fields.EmailField", [], {"unique": "True", "max_length": "75"}), u"id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}), "ip_address": ("django.db.models.fields.CharField", [], {"default": "'ABC'", "max_length": "120"}), "ref_id": ("django.db.models.fields.CharField", [], {"default": "'ABC'", "max_length": "120"}), "timestamp": ("django.db.models.fields.DateTimeField", [], {"auto_now_add": "True", "blank": "True"}), "updated": ("django.db.models.fields.DateTimeField", [], {"auto_now": "True", "blank": "True"})}}
	complete_apps = ["joins"]