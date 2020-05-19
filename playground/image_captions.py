photos = Photo.objects.all()
captions = []
for idx, photo in enumerate(photos):
	if idx > 2:
		break
	thumbnail_path = photo.thumbnail.url
	with open("." + thumbnail_path, "rb") as image_file:
		encoded_string = base64.b64encode(image_file.read())
	encoded_string = str(encoded_string)[2:-1]
	resp_captions = requests.post("http://localhost:5000/", data=encoded_string)
	captions.append(resp_captions.json())