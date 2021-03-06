from .Mixins import VerifiableMixin
from neo.Core.Cryptography.Helper import bin_dbl_sha256
from neo.Core.Cryptography.Crypto import Crypto
import binascii
from neo.Core.Helper import Helper
from neo.Blockchain import GetBlockchain, GetGenesis
from neo.Core.Witness import Witness
from neo.Core.UInt256 import UInt256
from neo.Core.Size import Size as s
from neo.SmartContract.Helper import Helper as SCHelper
class BlockBase(VerifiableMixin):
	def __init__(self):
		self.Version = 0
		self.PrevHash = 0
		self.MerkleRoot = 0
		self.Timestamp = None
		self.Index = 0
		self.ConsensusData = None
		self.NextConsensus = None
		self.Script = None
		self.__hash = None
		self.__htbs = None
		self.currentSnapshot = None
	@property
	def Hash(self):
		"""
        Get the hash value of the Blockbase.
        Returns:
            UInt256: containing the hash of the data.
        """
		if not self.__hash:
			hashdata = self.RawData()
			ba = bytearray(binascii.unhexlify(hashdata))
			hash = bin_dbl_sha256(ba)
			self.__hash = UInt256(data=hash)
		return self.__hash
	def ToArray(self):
		"""
        Get the byte data of self.
        Returns:
            bytes:
        """
		return Helper.ToArray(self)
	def RawData(self):
		"""
        Get the data used for hashing.
        Returns:
            bytes:
        """
		return Helper.GetHashData(self)
	@property
	def Scripts(self):
		"""
        Get the Scripts.
        Returns:
            list: with a single `neo.Core.Witness` object.
        """
		return [self.Script]
	def Size(self):
		"""
        Get the total size in bytes of the object.
        Returns:
            int: size.
        """
		scriptsize = 0
		if self.Script is not None:
			scriptsize = self.Script.Size()
		return s.uint32 + s.uint256 + s.uint256 + s.uint32 + s.uint32 + s.uint64 + s.uint160 + 1 + scriptsize
	def IndexBytes(self):
		"""
        Get the block height.
        Returns:
            bytes: array of bytes representing the block height.
        """
		return self.Index.to_bytes(4, "little")
	def Deserialize(self, reader):
		"""
        Deserialize full object.
        Args:
            reader (neo.IO.BinaryReader):
        """
		self.__hash = None
		self.DeserializeUnsigned(reader)
		byt = ord(reader.ReadByte())
		if int(byt) != 1:
			raise Exception("Incorrect format")
		witness = Witness()
		witness.Deserialize(reader)
		self.Script = witness
	def DeserializeUnsigned(self, reader):
		"""
        Deserialize unsigned data only.
        Args:
            reader (neo.IO.BinaryReader):
        """
		self.Version = reader.ReadUInt32()
		self.PrevHash = reader.ReadUInt256()
		self.MerkleRoot = reader.ReadUInt256()
		self.Timestamp = reader.ReadUInt32()
		self.Index = reader.ReadUInt32()
		self.ConsensusData = reader.ReadUInt64()
		self.NextConsensus = reader.ReadUInt160()
	def SerializeUnsigned(self, writer):
		"""
        Serialize unsigned data only.
        Args:
            writer (neo.IO.BinaryWriter):
        """
		writer.WriteUInt32(self.Version)
		writer.WriteUInt256(self.PrevHash)
		writer.WriteUInt256(self.MerkleRoot)
		writer.WriteUInt32(self.Timestamp)
		writer.WriteUInt32(self.Index)
		writer.WriteUInt64(self.ConsensusData)
		writer.WriteUInt160(self.NextConsensus)
	def GetMessage(self):
		"""
        Get the data used for hashing.
        Returns:
            bytes:
        """
		return Helper.GetHashData(self)
	def GetScriptHashesForVerifying(self, snapshot):
		"""
        Get the script hash used for verification.
        Raises:
            Exception: if the verification script is invalid, or no header could be retrieved from the Blockchain.
        Returns:
            list: with a single UInt160 representing the next consensus node.
        """
		if self.PrevHash.Data == bytearray(32):
			if type(self.Script.VerificationScript) is bytes:
				return [bytearray(self.Script.VerificationScript)]
			elif type(self.Script.VerificationScript) is bytearray:
				return [self.Script.VerificationScript]
			else:
				raise Exception("Invalid Verification script")
		prev_header = snapshot.GetHeader(self.PrevHash.ToBytes())
		if prev_header is None:
			raise Exception("Invalid operation")
		return [prev_header.NextConsensus]
	def Serialize(self, writer):
		"""
        Serialize full object.
        Args:
            writer (neo.IO.BinaryWriter):
        """
		self.SerializeUnsigned(writer)
		writer.WriteByte(1)
		self.Script.Serialize(writer)
	def ToJson(self):
		"""
        Convert object members to a dictionary that can be parsed as JSON.
        Returns:
             dict:
        """
		json = {}
		json["hash"] = self.Hash.To0xString()
		json["size"] = self.Size()
		json["version"] = self.Version
		json["previousblockhash"] = self.PrevHash.To0xString()
		json["merkleroot"] = self.MerkleRoot.To0xString()
		json["time"] = self.Timestamp
		json["index"] = self.Index
		nonce = bytearray(self.ConsensusData.to_bytes(8, "little"))
		nonce.reverse()
		json["nonce"] = nonce.hex()
		json["nextconsensus"] = Crypto.ToAddress(self.NextConsensus)
		json["script"] = "" if not self.Script else self.Script.ToJson()
		return json
	def Verify(self, snapshot):
		"""
        Verify block using the verification script.
        Returns:
            bool: True if valid. False otherwise.
        """
		if self.Index > 0:
			prev_header = snapshot.GetHeader(self.PrevHash.ToBytes())
			if prev_header is None:
				return False
			if prev_header.Index + 1 != self.Index:
				return False
			if prev_header.Timestamp >= self.Timestamp:
				return False
		if not SCHelper.VerifyWitnesses(self, snapshot):
			return False
		return True