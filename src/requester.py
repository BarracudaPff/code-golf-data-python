def bs4_decorator(function):
	"""
    Decorator
    Generator a soup from give html content
    :param function:
    :return Soup if content
            None if None:
    """
	def soup_generator(self, url):
		response = function(self, url)
		if response:
			return bs4.BeautifulSoup(response.text)
		else:
			return None
	return soup_generator
class Requester:
	"""
    Base class of requests maker like lawman and crawler
    Provided With Simple request function and bs decorator
    """
	def __init__(self, tieba_name="steam", cookie=None):
		if cookie is None:
			raise Exception("Cookie must be provided")
		self.tieba_name = tieba_name
		self.cookie = cookie
		cookie_jar = requests.utils.cookiejar_from_dict(cookie)
		self.session_worker = requests.Session()
		self.session_worker.cookies = cookie_jar
		self.tieba_base = TIEBA_MOBILE_BASE_URL.format(tieba_name=tieba_name)
		self.url_base = TIEBA_URL
	@bs4_decorator
	def get_content(self, url):
		"""
        Get content of url with cookie
        :param url:
        :return String if success
                None if failed:
        """
		try:
			response = self.session_worker.get(url, timeout=10)
			logging.debug("Get {0} SUCCESS".format(common.get_post_id(url)))
			return response
		except requests.Timeout as e:
			logging.warning("Get {0} TIMEOUT".format(common.get_post_id(url), e))
		except Exception as e:
			logging.warning("Get {0} FAILED :{1} ".format(common.get_post_id(url), e))
		return None