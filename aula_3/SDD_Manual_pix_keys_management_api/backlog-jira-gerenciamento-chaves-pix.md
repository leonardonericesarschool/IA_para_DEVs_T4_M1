# Backlog Jira - Gerenciamento de Chaves Pix

## Objetivo

Estruturar o backlog do produto em formato compativel com Jira para desenvolvimento backend da aplicacao de **Gerenciamento de Chaves Pix**.

## Premissas

- O escopo cobre backend e integracoes necessarias para o ciclo de vida de chaves Pix.
- O backlog esta organizado para um time de engenharia backend com apoio de arquitetura, seguranca e operacoes.
- Regras regulatorias detalhadas devem ser refinadas com Compliance antes da liberacao em producao.

## Estrutura recomendada no Jira

- `Epic`: agrupador funcional de alto nivel
- `Story`: entrega orientada a valor e comportamento de negocio
- `Task`: implementacao tecnica, integracao, observabilidade ou preparacao operacional
- `Sub-task`: opcional para desdobramento interno do time

## Epic

### EPIC PIX-EP01 - Gerenciamento de Chaves Pix Backend

**Descricao**  
Construir a camada backend para cadastro, consulta, listagem, exclusao, auditoria e monitoramento de chaves Pix, com foco em seguranca, rastreabilidade, resiliencia operacional e prontidao para evolucao futura.

**Resultado esperado**
- Disponibilizar APIs backend para gerenciamento de chaves Pix
- Garantir consistencia de estado e trilha de auditoria
- Suportar operacao monitoravel e reprocessavel

**Criterios de sucesso**
- Cadastro, consulta, listagem e exclusao funcionando de ponta a ponta
- Baixa incidencia de duplicidade e inconsistencias
- Rastreabilidade completa por operacao
- Integracoes com falha tratadas de forma segura e observavel

---

## Stories

### PIX-1 - Cadastrar chave Pix

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**  
Como sistema de gestao de chaves Pix, quero registrar uma nova chave Pix vinculada a uma conta elegivel para permitir que o cliente receba transferencias via Pix.

**Critérios de aceite**
- Receber requisicao com `tipo_chave`, `valor_chave`, `conta_id` e `cliente_id`
- Validar formato da chave conforme o tipo informado
- Validar elegibilidade da conta
- Impedir cadastro duplicado no contexto interno
- Persistir status inicial da solicitacao
- Registrar auditoria da operacao
- Retornar `chave_id`, `status` e `correlation_id`

**Definition of Done**
- API implementada e documentada
- Testes unitarios das regras de validacao
- Testes de integracao do fluxo de cadastro
- Logs e metricas adicionados

### PIX-2 - Consultar chave Pix por identificador

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: High

**Descricao**  
Como sistema de atendimento e canais digitais, quero consultar os dados de uma chave Pix cadastrada para exibir o estado atual e suportar operacoes posteriores.

**Critérios de aceite**
- Permitir consulta por `chave_id`
- Permitir consulta por `tipo_chave` + `valor_chave`
- Retornar status, vinculo com conta e timestamps relevantes
- Mascarar dados sensiveis quando aplicavel
- Retornar erro padronizado para nao encontrado
- Gerar logs com `correlation_id`

**Definition of Done**
- Endpoint implementado
- Contrato de resposta revisado
- Cobertura de testes de sucesso e nao encontrado
- Auditoria de consulta administrativa definida

### PIX-3 - Listar chaves Pix de cliente ou conta

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: High

**Descricao**  
Como canal digital ou operacao, quero listar as chaves Pix associadas a um cliente ou conta para permitir gestao e suporte operacional.

**Critérios de aceite**
- Permitir listagem por `cliente_id`
- Permitir listagem por `conta_id`
- Retornar tipo da chave, valor mascarado, status e data de criacao
- Suportar paginacao
- Suportar ordenacao deterministica
- Excluir campos internos desnecessarios

**Definition of Done**
- Endpoint implementado
- Paginacao validada
- Testes de performance basicos executados
- Contrato documentado

### PIX-4 - Excluir chave Pix

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**  
Como sistema de gestao de chaves Pix, quero remover uma chave Pix existente para encerrar seu uso com seguranca e manter o cadastro atualizado.

**Critérios de aceite**
- Validar pertencimento da chave a conta ou cliente
- Impedir exclusao em estado incompativel
- Atualizar status da chave ao longo da operacao
- Manter historico da chave apos exclusao logica
- Garantir idempotencia
- Registrar auditoria completa

**Definition of Done**
- Fluxo de exclusao implementado
- Regras de idempotencia testadas
- Historico persistido
- Observabilidade adicionada

### PIX-5 - Centralizar validacoes de elegibilidade e regras de negocio

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**  
Como plataforma backend, quero centralizar as validacoes de elegibilidade para criacao e manutencao de chaves para reduzir inconsistencias e risco operacional.

**Critérios de aceite**
- Validar conta ativa e apta para Pix
- Validar vinculo entre cliente e conta
- Validar restricoes de estado antes de transicoes
- Padronizar erros de validacao
- Expor metricas de rejeicao por regra de negocio

**Definition of Done**
- Regras em camada de dominio reutilizavel
- Testes unitarios cobrindo cenarios criticos
- Codigos de erro definidos

### PIX-6 - Integrar backend com servicos externos do ecossistema operacional

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**  
Como backend de chaves Pix, quero integrar com servicos externos necessarios ao ciclo de vida da chave para manter o estado interno consistente com o ecossistema operacional.

**Critérios de aceite**
- Encapsular chamadas externas em adaptadores
- Aplicar `timeout` e retry controlado
- Distinguir falhas tecnicas de falhas de negocio
- Mapear respostas externas para estados internos
- Permitir reprocessamento de operacoes pendentes

**Definition of Done**
- Cliente de integracao implementado
- Tratamento de excecoes padronizado
- Testes de integracao ou mocks contratuais adicionados
- Logs estruturados ativos

### PIX-7 - Manter trilha de auditoria das operacoes

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**  
Como area de risco, compliance e operacao, quero que todas as operacoes relevantes sobre chaves Pix sejam auditaveis para suportar investigacao, conciliacao e prestacao de contas.

**Critérios de aceite**
- Registrar criacao, alteracao de status, exclusao e falhas relevantes
- Registrar `quem`, `quando`, `origem`, `acao`, `resultado` e `correlation_id`
- Proteger trilha contra alteracao indevida
- Mascarar ou tokenizar dados sensiveis
- Permitir busca historica por `chave_id`

**Definition of Done**
- Modelo de auditoria implementado
- Persistencia validada
- Politica de mascaramento aplicada
- Consulta historica suportada

### PIX-8 - Garantir idempotencia nas operacoes criticas

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: High

**Descricao**  
Como backend transacional, quero tratar requisicoes duplicadas sem efeitos colaterais para evitar inconsistencias no cadastro e exclusao de chaves.

**Critérios de aceite**
- Aceitar chave de idempotencia em operacoes criticas
- Repeticao com mesmo payload retornar mesmo resultado logico
- Repeticao com payload divergente ser rejeitada
- Definir retencao configuravel para controle de idempotencia

**Definition of Done**
- Persistencia de idempotencia implementada
- Testes automatizados cobrindo duplicidade
- Contrato tecnico documentado

### PIX-9 - Disponibilizar observabilidade operacional

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: High

**Descricao**  
Como time de operacao e engenharia, quero monitorar o processamento das operacoes de chave Pix para detectar falhas rapidamente e reduzir tempo de resolucao.

**Critérios de aceite**
- Expor metricas de volume, sucesso, erro, latencia e pendencia
- Permitir busca de logs por `correlation_id`
- Tornar falhas de integracao monitoraveis
- Dar visibilidade a operacoes presas em estado intermediario

**Definition of Done**
- Metricas publicadas
- Dashboard inicial definido
- Alertas para falhas relevantes configurados

### PIX-10 - Preparar dominio para portabilidade e reivindicacao

**Tipo**: Story  
**Epic Link**: PIX-EP01  
**Prioridade**: Medium

**Descricao**  
Como produto backend, quero modelar eventos e estados para portabilidade ou reivindicacao de chave para permitir evolucao futura sem refatoracao estrutural pesada.

**Critérios de aceite**
- Suportar estados intermediarios e transicoes auditaveis
- Separar cadastro simples de operacoes disputadas
- Permitir extensao futura com prazos, aprovacoes e callbacks
- Registrar limitacoes da primeira versao

**Definition of Done**
- Modelo de dominio preparado
- Documentacao tecnica atualizada
- Testes das transicoes basicas implementados

---

## Tasks tecnicas recomendadas

### PIX-11 - Definir contrato de API para gerenciamento de chaves Pix

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**
- Especificar endpoints, payloads, codigos de resposta e padrao de erros
- Definir politica de versionamento
- Formalizar campos obrigatorios e opcionais

### PIX-12 - Modelar entidades de dominio e persistencia

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**
- Modelar entidade `chave_pix`
- Modelar historico de status
- Modelar auditoria
- Definir indices para busca e unicidade

### PIX-13 - Implementar mecanismo de idempotencia

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: High

**Descricao**
- Criar armazenamento de chave de idempotencia
- Definir estrategia de expiracao
- Integrar mecanismo aos endpoints criticos

### PIX-14 - Implementar cliente de integracao externa

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**
- Criar adaptador para servicos externos
- Implementar timeout, retry e tratamento de erro
- Adicionar correlation tracing

### PIX-15 - Implementar trilha de auditoria

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**
- Persistir eventos de auditoria
- Definir mascaramento de payload
- Garantir consulta por `chave_id` e `correlation_id`

### PIX-16 - Implementar observabilidade e alertas

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: High

**Descricao**
- Expor metricas tecnicas e funcionais
- Padronizar logs estruturados
- Definir dashboard inicial
- Configurar alertas de erro e latencia

### PIX-17 - Criar suite de testes automatizados

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: Highest

**Descricao**
- Testes unitarios de regras de negocio
- Testes de integracao dos endpoints
- Testes de idempotencia
- Testes de falha de integracao

### PIX-18 - Documentar operacao e reprocessamento

**Tipo**: Task  
**Epic Link**: PIX-EP01  
**Prioridade**: Medium

**Descricao**
- Descrever runbook de falhas operacionais
- Definir procedimento de reprocessamento
- Registrar fallback manual

---

## Ordem sugerida de implementacao

1. PIX-11 - Definir contrato de API
2. PIX-12 - Modelar entidades de dominio e persistencia
3. PIX-5 - Centralizar validacoes de elegibilidade e regras de negocio
4. PIX-1 - Cadastrar chave Pix
5. PIX-6 - Integrar backend com servicos externos do ecossistema operacional
6. PIX-7 - Manter trilha de auditoria das operacoes
7. PIX-8 - Garantir idempotencia nas operacoes criticas
8. PIX-4 - Excluir chave Pix
9. PIX-2 - Consultar chave Pix por identificador
10. PIX-3 - Listar chaves Pix de cliente ou conta
11. PIX-9 - Disponibilizar observabilidade operacional
12. PIX-10 - Preparar dominio para portabilidade e reivindicacao

## Sugestao de labels no Jira

- `pix`
- `backend`
- `payments`
- `audit`
- `observability`
- `compliance`
- `idempotency`

## Campos adicionais recomendados no Jira

- `Epic Link`
- `Priority`
- `Story Points`
- `Component`
- `Labels`
- `Acceptance Criteria`
- `Definition of Done`
- `Dependencies`
- `Risk/Control Notes`

## Dependencias externas a registrar

- Servico de contas e clientes
- Servico de autenticacao e autorizacao
- Integracao com diretorio/servicos externos do ecossistema Pix
- Plataforma de logs, metricas e alertas
- Validacao de politicas com Compliance e Arquitetura
