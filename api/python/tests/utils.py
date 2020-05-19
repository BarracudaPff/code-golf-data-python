"""
Unittest setup
"""
class QuiltTestCase(TestCase):
	"""
    Base class for unittests.
    - Creates a mock config
    - Creates a test client
    - Mocks requests
    """
	def setUp(self):
		assert "pytest" in str(CONFIG_PATH)
		quilt3.config(navigator_url="https://example.com", elastic_search_url="https://es.example.com/", apiGatewayEndpoint="https://xyz.execute-api.us-east-1.amazonaws.com/prod", default_local_registry=pathlib.Path(".").resolve().as_uri() + "/local_registry", default_remote_registry="s3://example/", default_install_location=None, defaultBucket="test-bucket", registryUrl="https://registry.example.com")
		self.requests_mock = responses.RequestsMock(assert_all_requests_are_fired=False)
		self.requests_mock.start()
		self.s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
		self.s3_client_patcher = mock.patch("quilt3.data_transfer.create_s3_client", return_value=self.s3_client)
		self.s3_client_patcher.start()
		self.s3_stubber = Stubber(self.s3_client)
		self.s3_stubber.activate()
	def tearDown(self):
		self.s3_stubber.assert_no_pending_responses()
		self.s3_stubber.deactivate()
		self.s3_client_patcher.stop()
		self.requests_mock.stop()