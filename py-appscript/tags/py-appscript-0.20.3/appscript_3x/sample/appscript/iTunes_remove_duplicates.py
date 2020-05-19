count = 0
foundids = []
tracks = app("iTunes").browser_windows[1].view.tracks
for id, track in zip(tracks.database_ID.get(), tracks.get()):
	if id in foundids:
		track.delete()
		count += 1
	else:
		foundids.append(id)
print("%i tracks removed." % count)