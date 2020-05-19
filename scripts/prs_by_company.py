import argparse
import csv
import logging
import json
import collections
import os
import yaml
known_companies = ["google", "red hat", "cisco", "datawire", "teradata"]
def get_company_from_email(email):
	domain = email.split("!", 1)[1]
	if domain == "users.noreply.github.com":
		return ""
	company = domain.split(".", 1)[0]
	if company == "gmail":
		return ""
	return company
if __name__ == "__main__":
	logging.getLogger().setLevel(logging.INFO)
	parser = argparse.ArgumentParser(description="Create a CSV file containing # of PRs by company.")
	parser.add_argument("--users_file", default="", type=str, help="Json file containing information about committers.")
	parser.add_argument("--prs_file", default="", type=str, help="The csv file containing # of PRs for different users.")
	parser.add_argument("--output", default="", type=str, help="The file to write.")
	args = parser.parse_args()
	if not args.users_file:
		raise ValueError("--user_file must be specified.")
	if not args.prs_file:
		raise ValueError("--prs_file must be specified.")
	if not args.output:
		raise ValueError("--output must be specified.")
	with open(args.users_file) as hf:
		users = json.load(hf)
	login_to_company = {}
	for u in users:
		company = u.get("company")
		login = u.get("login")
		if not company:
			email = u.get("email")
			logging.info("Users %s company not set trying to infer from email: %s", login, email)
			company = get_company_from_email(email)
		if not company:
			logging.info("Skipping user %s no company", login)
			continue
		company = company.lower().strip()
		company = company.strip("!")
		for c in known_companies:
			if c in company:
				logging.info("Mapping %s to %s", company, c)
				company = c
				break
		login_to_company[login] = company
	counts = collections.Counter()
	with open(args.prs_file) as hf:
		reader = csv.reader(hf, delimiter=";")
		reader.next()
		for row in reader:
			login = row[1]
			num_prs = int(row[2])
			company = login_to_company.get(login, "unknown")
			logging.info("User %s company %s # prs %s", login, company, num_prs)
			counts.update({company: num_prs})
	logging.info("Writing output to %s", args.output)
	with open(args.output, "w") as hf:
		writer = csv.writer(hf)
		for k, v in counts.iteritems():
			writer.writerow([k, v])