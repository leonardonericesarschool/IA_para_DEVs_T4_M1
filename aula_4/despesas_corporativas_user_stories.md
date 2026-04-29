# User Stories e Critérios de Aceitação

## User Stories

1. **Como funcionário**, quero registrar uma despesa corporativa diária para transporte ou alimentação, para que meu reembolso seja processado rapidamente.

2. **Como sistema**, devo validar automaticamente as despesas de alimentação para recusar valores acima de R$ 100,00, para garantir conformidade com a política interna.

3. **Como funcionário**, quero receber uma resposta clara do endpoint indicando sucesso ou recusa, para saber se minha despesa foi aceita.

## Critérios de Aceitação

### Cenário 1: Registrar despesa válida de alimentação
- Dado que o funcionário envia um registro de despesa com nome, tipo de despesa `alimentação` e valor de R$ 80,00
- Quando o sistema processar a solicitação
- Então a despesa deve ser aceita e o endpoint deve retornar uma mensagem de sucesso

### Cenário 2: Recusar despesa de alimentação acima do limite
- Dado que o funcionário envia um registro de despesa com nome, tipo de despesa `alimentação` e valor de R$ 120,00
- Quando o sistema processar a solicitação
- Então a despesa deve ser recusada automaticamente e o endpoint deve indicar a recusa

### Cenário 3: Registrar despesa de transporte sem limite adicional
- Dado que o funcionário envia um registro de despesa com nome, tipo de despesa `transporte` e valor de R$ 150,00
- Quando o sistema processar a solicitação
- Então a despesa deve ser aceita e o endpoint deve retornar uma mensagem de sucesso
