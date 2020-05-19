def program(username):
	print("Hello " + username)
def login(username, password):
	validuser = False
	validpass = False
	with open("usernames.txt", "r") as usernamefile:
		usernamelist = usernamefile.readlines()
		for x in range(len(usernamelist)):
			usernamelist[x] = usernamelist[x].replace("\n", "")
		for usernameinfile in usernamelist:
			if username == usernameinfile:
				validuser = True
				usernameindex = usernamelist.index(username)
				with open("passwords.txt", "r") as passwordfile:
					passwordlist = passwordfile.readlines()
					for x in range(len(passwordlist)):
						passwordlist[x] = passwordlist[x].replace("\n", "")
					if password == passwordlist[usernameindex]:
						validpass = True
	if validuser and validpass:
		return True
	else:
		return False
username = input("What is your username?")
password = input("What is your password?")
valid = login(username, password)
if valid:
	program(username)
else:
	print("Invalid Username or Password.")