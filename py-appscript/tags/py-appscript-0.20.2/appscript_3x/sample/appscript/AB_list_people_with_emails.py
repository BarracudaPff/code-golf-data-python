peopleref = app("Address Book").people[its.emails != []]
for name, emails in zip(peopleref.name.get(), peopleref.emails.value.get()):
	print(name, emails)