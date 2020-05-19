class Provider(PhoneNumberProvider):
	formats = ("%## ####", "%##-####", "%######", "0{{area_code}} %## ####", "0{{area_code}} %##-####", "0{{area_code}}-%##-####", "0{{area_code}} %######", "(0{{area_code}}) %## ####", "(0{{area_code}}) %##-####", "(0{{area_code}}) %######", "+64 {{area_code}} %## ####", "+64 {{area_code}} %##-####", "+64 {{area_code}} %######", "+64-{{area_code}}-%##-####", "+64{{area_code}}%######")
	area_codes = ["20", "21", "22", "27", "29", "3", "4", "6", "7", "9"]
	def area_code(self):
		return self.numerify(self.random_element(self.area_codes))
	def phone_number(self):
		pattern = self.random_element(self.formats)
		return self.numerify(self.generator.parse(pattern))