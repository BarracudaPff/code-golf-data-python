class AddressDialog(WindowModalDialog):
	def __init__(self, parent, address):
		WindowModalDialog.__init__(self, parent, _("Address"))
		self.address = address
		self.parent = parent
		self.config = parent.config
		self.wallet = parent.wallet
		self.app = parent.app
		self.saved = True
		self.setMinimumWidth(700)
		vbox = QVBoxLayout()
		self.setLayout(vbox)
		vbox.addWidget(QLabel(_("Address:")))
		self.addr_e = ButtonsLineEdit(self.address)
		self.addr_e.addCopyButton(self.app)
		icon = ":icons/qrcode_white.png" if ColorScheme.dark_scheme else ":icons/qrcode.png"
		self.addr_e.addButton(icon, self.show_qr, _("Show QR Code"))
		self.addr_e.setReadOnly(True)
		vbox.addWidget(self.addr_e)
		try:
			pubkeys = self.wallet.get_public_keys(address)
		except BaseException as e:
			pubkeys = None
		if pubkeys:
			vbox.addWidget(QLabel(_("Public keys") + ":"))
			for pubkey in pubkeys:
				pubkey_e = ButtonsLineEdit(pubkey)
				pubkey_e.addCopyButton(self.app)
				vbox.addWidget(pubkey_e)
		try:
			redeem_script = self.wallet.pubkeys_to_redeem_script(pubkeys)
		except BaseException as e:
			redeem_script = None
		if redeem_script:
			vbox.addWidget(QLabel(_("Redeem Script") + ":"))
			redeem_e = ShowQRTextEdit(text=redeem_script)
			redeem_e.addCopyButton(self.app)
			vbox.addWidget(redeem_e)
		vbox.addWidget(QLabel(_("History")))
		self.hw = HistoryList(self.parent)
		self.hw.get_domain = self.get_domain
		vbox.addWidget(self.hw)
		vbox.addLayout(Buttons(CloseButton(self)))
		self.format_amount = self.parent.format_amount
		self.hw.update()
	def get_domain(self):
		return [self.address]
	def show_qr(self):
		text = self.address
		try:
			self.parent.show_qrcode(text, "Address", parent=self)
		except Exception as e:
			self.show_message(str(e))