class Exit:
	SUCCESS = 0
	FAILURE = 1
	COMMAND_LINE_SYNTAX_ERROR = 2

class SignMode:
	SELF_SIGN = "self-sign"
	CSR_ONLY = "csr-only"
	USE_CA = "use-ca"

	all = [SELF_SIGN, CSR_ONLY, USE_CA]

class CAType:
	CA = "ca"
	SERVER = "server"
	CLIENT = "client"

	all = [CA, SERVER, CLIENT]

