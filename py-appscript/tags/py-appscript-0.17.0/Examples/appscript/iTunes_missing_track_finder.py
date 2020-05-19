from appscript import *
for track in app("iTunes").sources["Library"].library_playlists["Library"].file_tracks.get():
	if track.location.get() == k.MissingValue:
		track.delete()