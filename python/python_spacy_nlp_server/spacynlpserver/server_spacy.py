"""Coreference resolution server example.
A simple server serving the coreference system.
This file is copied and modified from an example
program from https://github.com/huggingface/neuralcoref
"""
unicode_ = str
class AllResource(object):
	def __init__(self):
		self.nlp = spacy.load("en")
		print("Server loaded")
		self.response = None
	def on_get(self, req, resp):
		self.response = {}
		text_param = req.get_param("text")
		if text_param is not None:
			text = ",".join(text_param) if isinstance(text_param, list) else text_param
			text = unicode_(text)
			text = text.replace("%20", " ").replace("%3B", ";").replace("%2C", ",").replace("%3A", ":").replace("%24", "$").replace("%2C", ",")
			print("** text=", text)
			doc = self.nlp(text)
			self.response["entities"] = [ent.text + "/" + ent.label_ for ent in doc.ents]
			self.response["tokens"] = [token.text for token in doc]
			resp.body = json.dumps(self.response)
			resp.content_type = "application/json"
		resp.append_header("Access-Control-Allow-Origin", "*")
		resp.status = falcon.HTTP_200
if __name__ == "__main__":
	RESSOURCE = AllResource()
	APP = falcon.API()
	APP.add_route("/", RESSOURCE)
	HTTPD = make_server("0.0.0.0", 8008, APP)
	HTTPD.serve_forever()