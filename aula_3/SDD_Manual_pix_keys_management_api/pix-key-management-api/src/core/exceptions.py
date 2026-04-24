"""Custom domain exceptions."""


class PixKeyException(Exception):
    """Base exception for Pix Key domain."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        """
        Initialize exception.

        Args:
            code: Error code for client
            message: Human-readable error message
            status_code: HTTP status code (default 400)
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ChaveDuplicadaError(PixKeyException):
    """Raised when trying to create a duplicate Pix key."""

    def __init__(self, message: str = "Chave Pix já cadastrada para este cliente"):
        super().__init__(code="CHAVE_DUPLICADA", message=message, status_code=409)


class ContaNaoElegivelError(PixKeyException):
    """Raised when account is not eligible for Pix key."""

    def __init__(self, message: str = "Conta não é elegível para cadastro de chaves Pix"):
        super().__init__(code="CONTA_NAO_ELEGIVEL", message=message, status_code=400)


class ChaveNaoEncontradaError(PixKeyException):
    """Raised when Pix key is not found."""

    def __init__(self, message: str = "Chave Pix não encontrada"):
        super().__init__(code="CHAVE_NAO_ENCONTRADA", message=message, status_code=404)


class FormatoChaveInvalidoError(PixKeyException):
    """Raised when Pix key format is invalid."""

    def __init__(self, message: str = "Formato da chave Pix é inválido"):
        super().__init__(code="FORMATO_INVALIDO", message=message, status_code=400)


class ClienteNaoEncontradoError(PixKeyException):
    """Raised when client is not found."""

    def __init__(self, message: str = "Cliente não encontrado"):
        super().__init__(code="CLIENTE_NAO_ENCONTRADO", message=message, status_code=404)


class ContaNaoEncontradaError(PixKeyException):
    """Raised when account is not found."""

    def __init__(self, message: str = "Conta não encontrada"):
        super().__init__(code="CONTA_NAO_ENCONTRADA", message=message, status_code=404)
