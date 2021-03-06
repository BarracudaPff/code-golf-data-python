from neo.Core.IO.Mixins import SerializableMixin
from neo.Core.Cryptography.Crypto import Crypto
from neo.Core.BigInteger import BigInteger
from neo.SmartContract.ContractParameterType import ContractParameterType, ToName
class FunctionCode(SerializableMixin):
	@property
	def ReturnTypeBigInteger(self):
		return BigInteger(self.ReturnType)
	@property
	def HasStorage(self):
		"""
        Flag indicating if storage is available.
        Returns:
            bool: True if available. False otherwise.
        """
		from neo.Core.State.ContractState import ContractPropertyState
		return self.ContractProperties & ContractPropertyState.HasStorage > 0
	@property
	def HasDynamicInvoke(self):
		"""
        Flag indicating if dynamic invocation is supported.
        Returns:
            bool: True if supported. False otherwise.
        """
		from neo.Core.State.ContractState import ContractPropertyState
		return self.ContractProperties & ContractPropertyState.HasDynamicInvoke > 0
	@property
	def IsPayable(self):
		"""
        Flag indicating if the contract accepts payments.
        Returns:
            bool: True if supported. False otherwise.
        """
		from neo.Core.State.ContractState import ContractPropertyState
		return self.ContractProperties & ContractPropertyState.Payable > 0
	def __init__(self, script=None, param_list=None, return_type=255, contract_properties=0):
		self._scriptHash = None
		self.Script = script
		if param_list is None:
			self.ParameterList = []
		else:
			self.ParameterList = param_list
		self.ReturnType = ContractParameterType.FromString(return_type).value
		self.ContractProperties = contract_properties
	def ScriptHash(self):
		"""
        Get the script hash.
        Returns:
            UInt160:
        """
		if self._scriptHash is None:
			self._scriptHash = Crypto.ToScriptHash(self.Script, unhex=False)
		return self._scriptHash
	def Deserialize(self, reader):
		"""
        Deserialize full object.
        Args:
            reader (neo.IO.BinaryReader):
        """
		self.Script = reader.ReadVarBytes()
		self.ParameterList = reader.ReadVarBytes()
		self.ReturnType = ord(reader.ReadByte())
	def Serialize(self, writer):
		"""
        Serialize full object.
        Args:
            writer (neo.IO.BinaryWriter):
        """
		writer.WriteVarBytes(self.Script)
		writer.WriteVarBytes(self.ParameterList)
		writer.WriteByte(self.ReturnType)
	def ToJson(self):
		"""
        Convert object members to a dictionary that can be parsed as JSON.
        Returns:
             dict:
        """
		parameters = self.ParameterList.hex()
		paramlist = [ToName(ContractParameterType.FromString(parameters[i : i + 2]).value) for i in range(0, len(parameters), 2)]
		return {"hash": self.ScriptHash().To0xString(), "script": self.Script.hex(), "parameters": paramlist, "returntype": ToName(self.ReturnType) if type(self.ReturnType) is int else ToName(int(self.ReturnType))}