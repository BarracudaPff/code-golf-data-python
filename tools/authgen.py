import subprocess
import json
import re
p = subprocess.Popen('az cloud show -o json --query "{managementURI: endpoints.management, baseURL: endpoints.resourceManager, authURL: endpoints.activeDirectory, graphURL: endpoints.activeDirectoryGraphResourceId}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
cloud = json.loads(p.stdout.read().decode("utf8"))
p = subprocess.Popen('az account show -o json --query "{subscription: id}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
account = json.loads(p.stdout.read().decode("utf8"))
p = subprocess.Popen('az ad sp create-for-rbac -o json --query "{client: appId, key: password, tenant: tenant}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
out = p.stdout.read()
out = re.sub(b"[^.]*{", b"{", out)
sp = json.loads(out.decode("utf8"))
for key, value in sp.items():
	print(key + "=" + value)
for key, value in account.items():
	print(key + "=" + value)
for key, value in cloud.items():
	if not value.endswith("/"):
		value = value + "/"
	print(key + "=" + value.replace("https://", r"https\://"))