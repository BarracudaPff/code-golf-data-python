logger = logging.getLogger("ChocolateService")
class ChocolateService(api_pb2_grpc.SuggestionServicer, HealthServicer):
	def GetSuggestions(self, request, context):
		"""
        Main function to provide suggestion.
        """
		base_serice = BaseChocolateService(algorithm_name=request.experiment.spec.algorithm.algorithm_name)
		search_space = HyperParameterSearchSpace.convert(request.experiment)
		trials = Trial.convert(request.trials)
		new_assignments = base_serice.getSuggestions(search_space, trials, request.request_number)
		return api_pb2.GetSuggestionsReply(parameter_assignments=Assignment.generate(new_assignments))