"""
Description:
    Issue Transaction
Usage:
    from neo.Core.TX.IssueTransaction import IssueTransaction
"""
class IssueTransaction(Transaction):
	"""docstring for IssueTransaction"""
	def __init__(self, *args, **kwargs):
		"""
        Create an instance.
        Args:
            *args:
            **kwargs:
        """
		super(IssueTransaction, self).__init__(*args, **kwargs)
		self.Type = TransactionType.IssueTransaction
		self.Nonce = None
	def SystemFee(self):
		"""
        Get the system fee.
        Returns:
            Fixed8:
        """
		if self.Version >= 1:
			return Fixed8.Zero()
		all_neo_gas = True
		for output in self.outputs:
			if output.AssetId != GetSystemCoin().Hash and output.AssetId != GetSystemShare().Hash:
				all_neo_gas = False
		if all_neo_gas:
			return Fixed8.Zero()
		return super(IssueTransaction, self).SystemFee()
	def GetScriptHashesForVerifying(self, snapshot):
		pass
	def DeserializeExclusiveData(self, reader):
		"""
        Deserialize full object.
        Args:
            reader (neo.IO.BinaryReader):
        """
		self.Type = TransactionType.IssueTransaction
		if self.Version > 1:
			raise Exception("Invalid TX Type")
	def SerializeExclusiveData(self, writer):
		pass