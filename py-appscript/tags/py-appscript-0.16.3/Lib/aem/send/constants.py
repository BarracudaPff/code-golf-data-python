"""constants -- Apple event attribute keys and send mode flags.
(C) 2005 HAS
"""
AutoGenerateReturnID = _kAE.kAutoGenerateReturnID
DefaultTimeout = _kAE.kAEDefaultTimeout
NoTimeout = _kAE.kNoTimeOut
NoReply = _kAE.kAENoReply
QueueReply = _kAE.kAEQueueReply
WaitReply = _kAE.kAEWaitReply
DontReconnect = _kAE.kAEDontReconnect
WantReceipt = _kAE.kAEWantReceipt
NeverInteract = _kAE.kAENeverInteract
CanInteract = _kAE.kAECanInteract
AlwaysInteract = _kAE.kAEAlwaysInteract
CanSwitchLayer = _kAE.kAECanSwitchLayer
Direct = _kAE.keyDirectObject
ResultType = _kAE.keyAERequestedType
Ignore = "cons"
TransactionID = _kAE.keyTransactionIDAttr
ReturnID = _kAE.keyReturnIDAttr
EventClass = _kAE.keyEventClassAttr
EventID = _kAE.keyEventIDAttr
Address = _kAE.keyAddressAttr
OptionalKeyword = _kAE.keyOptionalKeywordAttr
Timeout = _kAE.keyTimeoutAttr
InteractLevel = _kAE.keyInteractLevelAttr
EventSource = _kAE.keyEventSourceAttr
OriginalAddress = _kAE.keyOriginalAddressAttr
AcceptTimeout = _kAE.keyAcceptTimeoutAttr
Subject = "subj"
Case = _AE.AECreateDesc(_kAE.typeEnumeration, "case")
Diacriticals = _AE.AECreateDesc(_kAE.typeEnumeration, "diac")
Expansion = _AE.AECreateDesc(_kAE.typeEnumeration, "expa")
Punctuation = _AE.AECreateDesc(_kAE.typeEnumeration, "punc")
Hyphens = _AE.AECreateDesc(_kAE.typeEnumeration, "hyph")
Whitespace = _AE.AECreateDesc(_kAE.typeEnumeration, "whit")
CaseConsider = 0x00000001
DiacriticConsider = 0x00000002
WhiteSpaceConsider = 0x00000004
HyphensConsider = 0x00000008
ExpansionConsider = 0x00000010
PunctuationConsider = 0x00000020
CaseIgnore = 0x00010000
DiacriticIgnore = 0x00020000
WhiteSpaceIgnore = 0x00040000
HyphensIgnore = 0x00080000
ExpansionIgnore = 0x00100000
PunctuationIgnore = 0x00200000