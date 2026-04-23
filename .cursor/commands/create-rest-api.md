---
mode: agent
---
Crie um projeto Python em diretório para implementar APIs REST. Adicione um arquivo README.md e uma licença MIT. 

O projeto deve seguir as seguintes práticas de design e desenvolvimento:
- Padrões de URL: Utilize substantivos no plural para representar recursos (ex: GET /produtos em vez de getProdutos).
- Utilizar camel case para codificação 
- Versionamento: Adicione a versão na URL para evitar quebrar clientes (ex: /api/v1/recurso).
- Tratamento de Erros: Retorne códigos de status HTTP apropriados (\(200\) OK, \(201\) Created, \(400\) Bad Request, \(404\) Not Found, \(500\) Internal Server Error) e mensagens claras.
- Codificação em Português
Paginação e Filtros: Use queries para grandes volumes de dados (ex: /items?page=2&limit=50).
- Frameworks: Pergunte ao desenvolvedor qual dos seguintes frameworks será utilizado:  FastAPI, Flask ou Django REST Framework (só aceite uma dessas 3 opções).
- Validação: Use Pydantic para validação de dados automática.
- Documentação: Gere documentação automática usando Swagger UI/OpenAPI (nativo no FastAPI).

Para instalação, siga essas instruções:
- Gere o arquivo de requirements com todas as dependências na versão mais atualizada.
- Utilize o gerenciador de pacotes uv com a versão Python mais atualizada para instalação das dependências.
- Instale as dependências utilizando ambiente virtual com o nome da aplicação.
