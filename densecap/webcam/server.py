app = Flask(__name__)
api = Api(app)
CORS(app)
input_dir = "webcam/inputs"
output_dir = "webcam/outputs"
def f7(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]
def root_dir():
	return os.path.abspath(os.path.dirname(__file__))
def get_file(filename):
	try:
		src = os.path.join(root_dir(), filename)
		return open(src).read()
	except IOError as exc:
		return str(exc)
def decode_base64(data):
	"""Decode base64, padding being optional.
    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.
    """
	missing_padding = len(data) % 4
	if missing_padding != 0:
		data += "=" * (4 - missing_padding)
	return data
class ShortCaptions(Resource):
	def get(self):
		return Response("Method not allowed", mimetype="text/html")
	def post(self):
		try:
			img_id = random.randint(1, 1000000)
			img_name = os.path.join(input_dir, "%d.jpg" % img_id)
			data = request.data
			img_data = data
			im = Image.open(BytesIO(base64.b64decode(img_data)))
			im.save(img_name)
			json_name = os.path.join(output_dir, "%d.json" % img_id)
			while not os.path.isfile(json_name):
				time.sleep(0.05)
			with open(json_name, "r") as f:
				ann = json.load(f)
			os.remove(json_name)
			outlist = f7(ann["captions"])
			out = {}
			out["status"] = True
			out["data"] = outlist
		except Exception as e:
			out = {}
			out["status"] = False
			out["message"] = e.message
		return out
api.add_resource(ShortCaptions, "/")
if __name__ == "__main__":
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(5000)
	try:
		IOLoop.instance().start()
	except KeyboardInterrupt:
		IOLoop.instance().stop()