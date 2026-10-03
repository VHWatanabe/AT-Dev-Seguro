# Relatório Final de Rastreabilidade — API de Agendamento de Consultas

## 1. Rastreabilidade: Threat Model → Vulnerabilidade → Correção

| Ameaça (Exercício 4) | Vulnerabilidade confirmada (Exercício 8) | Correção aplicada | Exercício | Evidência |
|---|---|---|---|---|
| Elevation of Privilege via BOLA | GET /consultas/{id} sem ownership | verificar_ownership adicionado | 9 | Teste automatizado e print 403 com dra.beatriz |
| Tampering via mass assignment | Campo status sem whitelist, extra não bloqueado | Enum StatusConsulta e extra=forbid | 9 | Teste automatizado e print 422 |
| Denial of Service via força bruta | Login sem limite de tentativas | Rate limiting 5 por minuto via slowapi | 10 | Teste automatizado e print 429 |
| Information Disclosure via CORS aberto | CORSMiddleware sem allowlist | Allowlist explícita, localhost 3000 | 10 | Teste funcional com portas 3000 e 5500 |
| Tampering via SQL Injection | Persistência em memória sem parametrização | Migração para SQLModel com queries parametrizadas | 11 | Testes automatizados passando |
| Spoofing via segredo JWT exposto | SECRET_KEY hardcoded no código fonte | Movido para variável de ambiente | 12 | Pipeline GitHub Actions, run 2 |
| Elevation of Privilege via BFLA | Recepcionista com acesso indevido a rotas de criação | require_role aplicado em POST /consultas/ | 6 e 12 | Teste automatizado test_bfla_recepcionista |

## 2. Findings do scan OWASP ZAP (scan passivo)

| Alerta | Risco ZAP | Categoria OWASP correlata | Avaliação | Ação |
|---|---|---|---|---|
| Content Security Policy Header Not Set | Médio | A05:2021 Security Misconfiguration | Real. CSP não foi implementado, apenas HSTS, X-Frame-Options e X-Content-Type-Options | Aceito como risco residual, fora do escopo explícito do Exercício 10 |
| Strict-Transport-Security Header Not Set | Baixo | A05:2021 Security Misconfiguration | Falso positivo parcial. O header está implementado no código, mas só tem efeito real sobre HTTPS; ambiente local roda em HTTP puro | Nenhuma ação necessária em desenvolvimento |
| Configuração Incorreta Entre Domínios | Baixo | A05:2021 Security Misconfiguration | Avaliado. Allowlist de CORS já restrita a localhost 3000, sem wildcard | Nenhuma ação necessária |
| Sub Resource Integrity Attribute Missing | Informativo | A06:2021 Vulnerable and Outdated Components | Falso positivo para este Assessment. Scripts carregados via CDN pelo Swagger UI, gerado automaticamente pelo FastAPI | Nenhuma ação necessária |
| Cross-Domain JavaScript Source File Inclusion | Informativo | A06:2021 Vulnerable and Outdated Components | Mesma causa do item acima | Nenhuma ação necessária |
| Divulgação de Data e Hora Unix | Informativo | Não aplicável | Campo data_hora exposto é dado de negócio esperado, não vazamento de informação do sistema | Nenhuma ação necessária |
| Demais alertas informativos (Session Management, Modern Web Application, Cache-control) | Informativo | Não aplicável | Classificações automáticas sobre comportamento observado, sem indicar vulnerabilidade | Nenhuma ação necessária |

## 3. Auditoria da especificação OpenAPI

Verificação manual do endpoint /openapi.json confirmou que o schema ConsultaPublic expõe apenas os campos paciente_id, profissional_id, data_hora, status e id, sem o campo interno observacoes_internas. O schema de usuário (contendo hashed_password) não é serializado em nenhuma resposta da API, já que não existe rota que retorna dados de usuário diretamente.

## 4. Testes de segurança com mocking

Implementados em tests/test_security_mocked.py, usando app.dependency_overrides para isolar a lógica de validação de entrada e autorização sem depender de login real:
- Validação de tipo de dado rejeitada (422) com usuário autenticado mockado
- Acesso negado (403) para usuário mockado sem papel adequado
- Acesso permitido (201) para usuário mockado com papel adequado

## 5. Risco residual

- Ausência de refresh token e rotação de token: aceito como risco residual de severidade baixa, CVSS 3.1, dado que o token de acesso expira em 30 minutos, limitando a janela de exposição em caso de vazamento.
- CORS configurado para um frontend placeholder, localhost 3000, não um frontend real: este Assessment não exige desenvolvimento de frontend; a allowlist demonstra o mecanismo corretamente.
- Content Security Policy não implementado: documentado no scan ZAP, aceito como melhoria futura fora do escopo explícito da disciplina.

## 6. Decisão de liberação para deploy

Com base na análise de CVSS do Exercício 12, na ausência de achados Críticos ou Altos não corrigidos no pipeline automatizado, Bandit e pip-audit, e no scan ZAP, a aplicação é considerada apta para deploy em ambiente de homologação, com os riscos residuais documentados acima aceitos e justificados. Rescan recomendado antes de produção real, incluindo scan ativo, fora do escopo desta disciplina.