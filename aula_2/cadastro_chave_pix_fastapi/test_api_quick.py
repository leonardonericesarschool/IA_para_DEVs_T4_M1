"""Teste rápido da API."""
from fastapi.testclient import TestClient
from app import criarApp

app = criarApp()
client = TestClient(app)

print("=" * 60)
print("TESTE RÁPIDO DA API")
print("=" * 60)

# Test health check
print("\n1. Health Check")
response = client.get("/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test create chave pix
print("\n2. Criar Chave Pix")
payload = {
    "tipoChave": "CPF",
    "valorChave": "12345678901",
    "descricao": "Minha chave"
}
response = client.post("/api/v1/chaves-pix", json=payload)
print(f"   Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"   ID: {data['id']}")
    print(f"   Tipo: {data['tipoChave']}")
    print(f"   Valor: {data['valorChave']}")

# Test list
print("\n3. Listar Chaves Pix")
response = client.get("/api/v1/chaves-pix")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Total items: {data['total']}")
    print(f"   Pages: {data['pages']}")
    print(f"   Items: {len(data['items'])}")

# Test duplicate (should fail)
print("\n4. Criar Chave Duplicada (deve falhar)")
response = client.post("/api/v1/chaves-pix", json=payload)
print(f"   Status: {response.status_code}")
if response.status_code != 201:
    print(f"   Mensagem: {response.json()['mensagem']}")

# Test get by id
print("\n5. Obter Chave por ID")
response = client.get("/api/v1/chaves-pix/1")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Valor: {data['valorChave']}")

# Test update
print("\n6. Atualizar Chave")
update_payload = {"descricao": "Nova descrição"}
response = client.put("/api/v1/chaves-pix/1", json=update_payload)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Descrição atualizada: {data['descricao']}")

# Test delete
print("\n7. Deletar Chave")
response = client.delete("/api/v1/chaves-pix/1")
print(f"   Status: {response.status_code}")

# Test get deleted (should fail)
print("\n8. Obter Chave Deletada (deve falhar)")
response = client.get("/api/v1/chaves-pix/1")
print(f"   Status: {response.status_code}")

print("\n" + "=" * 60)
print("TESTES CONCLUÍDOS")
print("=" * 60)
