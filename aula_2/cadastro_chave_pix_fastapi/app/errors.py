from typing import Any


class ErroApi(Exception):
    """
    Erro customizado para a API.
    Será capturado por handlers globais e convertido em resposta HTTP.
    """
    def __init__(
        self,
        statusCode: int,
        mensagem: str,
        detalhes: dict[str, Any] | None = None,
    ):
        self.statusCode = statusCode
        self.mensagem = mensagem
        self.detalhes = detalhes
        super().__init__(self.mensagem)


def extrairMensagemErro(erro: dict[str, Any]) -> str:
    """
    Extrai mensagem de erro formatada.
    
    Args:
        erro: Dicionário de erro
        
    Returns:
        Mensagem de erro em português
    """
    if isinstance(erro, dict):
        if "msg" in erro:
            return erro["msg"]
        if "detail" in erro:
            return erro["detail"]
    return "Erro desconhecido"
