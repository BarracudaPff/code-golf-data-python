from __future__ import unicode_literals
from .. import Provider as BaseProvider
class Provider(BaseProvider):
	nino_formats = ("ZZ ## ## ## T", "ZZ######T", "ZZ ###### T")
	def ssn(self):
		pattern = self.random_element(self.nino_formats)
		return self.numerify(self.generator.parse(pattern))
	vat_id_formats = ("GB### #### ##", "GB### #### ## ###", "GBGD###", "GBHA###")
	def vat_id(self):
		"""
        http://ec.europa.eu/taxation_customs/vies/faq.html#item_11
        :return: A random British VAT ID
        """
		return self.bothify(self.random_element(self.vat_id_formats))