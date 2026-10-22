# ESTUDO TÉCNICO PRELIMINAR

## Solução de aquisição de dados de qualidade da água por Modbus-RTU/RS-485

**Versão:** 1.0  
**Data de atualização:** 22 de outubro de 2026  
**Unidade demandante:** `[PREENCHER]`  
**Responsável pela elaboração:** `[PREENCHER]`  
**Processo administrativo:** `[PREENCHER]`

> **Nota de uso:** este documento foi elaborado a partir do software `water_quality_modbus`, da documentação e dos testes existentes no repositório. Quantitativos, local de instalação, níveis de serviço e preços devem ser completados pelo órgão antes da instrução do processo.

## 1. Descrição da necessidade

Há necessidade de realizar aquisição contínua, confiável e rastreável de parâmetros físico-químicos da água em sondas multiparâmetros, com comunicação industrial Modbus-RTU sobre RS-485. A solução deve reduzir leituras manuais, permitir identificação de falhas de comunicação e disponibilizar dados estruturados para operação, fiscalização e análises ambientais.

O problema não é apenas obter um valor instantâneo: é manter uma cadeia de aquisição que tolere indisponibilidade temporária da porta serial, sinalize respostas Modbus inválidas, registre o instante da medição e rejeite valores fisicamente implausíveis.

## 2. Alinhamento e interesse público

A solução apoia o monitoramento de qualidade da água, a detecção de alterações físico-químicas e a formação de histórico para tomada de decisão. O alinhamento com o planejamento institucional, o plano de contratações anual e os instrumentos ambientais aplicáveis deve ser confirmado pela unidade demandante.

**Instrumentos de planejamento relacionados:** `[PREENCHER ou indicar “não aplicável”, com justificativa]`.

## 3. Requisitos da solução

### 3.1 Requisitos funcionais

- Ler, no mínimo, temperatura, condutividade elétrica, pressão de gás dissolvido (TDG) e oxigênio dissolvido óptico (LDO).
- Operar com sondas Hydrolab MS-5 e/ou In-Situ Aqua TROLL/MP TROLL, conforme mapa de registradores validado para cada modelo.
- Comunicar-se por Modbus-RTU em RS-485, com endereço da unidade, baud rate, paridade, bits de parada e tempo limite configuráveis.
- Decodificar pares de registradores de 16 bits em `float32` IEEE 754 com a ordem de palavras exigida pela sonda.
- Informar timestamp em UTC, estado de validade e mensagem de status para cada leitura.
- Detectar timeout, exceção Modbus, resposta insuficiente e perda de conexão.
- Permitir operação contínua e encerramento controlado, com fechamento da porta serial.

### 3.2 Requisitos não funcionais

- Python 3.10 ou superior, com dependências abertas e documentadas.
- Código versionado, testável e executável em ambiente Linux; a compatibilidade com Windows deve ser validada caso haja necessidade de uso em campo.
- Registro operacional por logging, sem depender de `print` para diagnóstico.
- Validação de plausibilidade: temperatura de -2 a 60 °C, condutividade de 0 a 100.000 µS/cm, TDG de 300 a 1.600 mmHg e LDO de 0 a 30 mg/L, com ajuste posterior pelo responsável técnico.
- Não armazenar credenciais ou dados pessoais no software. Acesso ao equipamento e ao ambiente computacional deve ser controlado pelo órgão.
- Documentação de instalação, configuração, mapa de registradores, procedimento de calibração e recuperação de falhas.

### 3.3 Requisitos de infraestrutura

- Sonda multiparâmetro compatível e em condição de calibração vigente.
- Transceptor USB-RS-485 industrial, cabeamento e proteção elétrica adequados ao ambiente.
- Computador, gateway ou equipamento de borda com porta USB/serial, Python e armazenamento suficiente para logs.
- Alimentação elétrica, proteção contra surtos e, quando aplicável, gabinete e grau de proteção compatíveis com o local.
- Definição de conectividade para supervisão remota, caso seja necessária.

## 4. Levantamento de alternativas

| Alternativa | Vantagens | Limitações | Avaliação |
|---|---|---|---|
| Leitura manual e registro em planilha | Baixo investimento inicial | Baixa frequência, erro humano, ausência de alerta e histórico automatizado | Não atende à necessidade contínua |
| Software proprietário fechado do fabricante | Suporte especializado e integração pronta | Dependência de fornecedor, licenças e menor flexibilidade | Adequado quando exigido pela garantia, mas deve ser comparado |
| Solução aberta em Python com Modbus-RTU | Baixo custo de licença, auditabilidade, testes e adaptação a diferentes sondas | Exige implantação, manutenção e validação de campo | **Alternativa recomendada** |
| Desenvolvimento integral de nova plataforma | Controle amplo sobre requisitos | Custo, prazo e risco maiores; repete componentes já disponíveis | Não recomendado neste momento |

## 5. Solução escolhida

Recomenda-se contratar/implantar uma solução composta por: (i) sondas multiparâmetros compatíveis; (ii) infraestrutura elétrica e RS-485; (iii) software de aquisição baseado no módulo existente `water_quality_modbus`; (iv) configuração, testes de aceitação, documentação, treinamento e suporte inicial.

O software existente já contém cliente serial, leitura de holding registers, tratamento de erro, reconexão por nova tentativa de conexão, decodificação word-swapped, validação de faixas e testes unitários. Antes da entrada em produção, devem ser confirmados em bancada o mapa de registradores de cada modelo, a validação de CRC pelo driver, a política de armazenamento/telemetria e a necessidade de retentativa com backoff.

## 6. Estimativa de quantitativos

| Item | Unidade | Quantidade |
|---|---:|---:|
| Sonda multiparâmetro compatível | unidade | `[PREENCHER]` |
| Transceptor USB-RS-485 industrial | unidade | `[PREENCHER]` |
| Computador/gateway de aquisição | unidade | `[PREENCHER]` |
| Instalação, configuração e testes | serviço | `[PREENCHER]` |
| Treinamento e documentação | serviço | `[PREENCHER]` |
| Suporte/manutenção por período definido | mês | `[PREENCHER]` |

Os quantitativos devem ser dimensionados pelo número de pontos de monitoramento, redundância desejada, frequência de leitura, disponibilidade de energia e estratégia de reposição/calibração.

## 7. Estimativa de valor

Não há pesquisa de preços no repositório. A estimativa deverá ser produzida pela área competente com fontes verificáveis, separando equipamento, instalação, calibração, suporte, manutenção e eventuais licenças. O custo de software aberto não elimina os custos de infraestrutura, integração, operação e suporte.

**Estimativa preliminar:** `[PREENCHER após pesquisa de preços]`.

## 8. Justificativa para parcelamento

Recomenda-se avaliar o parcelamento por grupos tecnicamente independentes: equipamentos de medição; infraestrutura e instalação; software/configuração; e suporte/calibração. A decisão final deve preservar a responsabilidade integral pela compatibilidade entre sonda, transceptor, mapa de registradores e software. Caso a garantia dependa de fornecedor único, a justificativa técnica deverá ser registrada.

## 9. Resultados pretendidos

- Aumentar a frequência e a regularidade das medições.
- Reduzir transcrição manual e erros de interpretação de registradores.
- Detectar indisponibilidade, resposta Modbus inválida e leituras fora de faixa.
- Manter histórico com timestamp, valores, validade e status da aquisição.
- Facilitar auditoria, manutenção e substituição de componentes sem dependência exclusiva de uma pessoa.

## 10. Providências prévias

1. Inventariar sondas, cabos, interfaces RS-485 e pontos de instalação.
2. Confirmar os mapas de registradores e a ordem de bytes com documentação do fabricante e ensaio em bancada.
3. Definir frequência de leitura, retenção dos dados, formato de exportação e destino do histórico.
4. Validar faixas físico-químicas com o responsável técnico e o método de monitoramento.
5. Definir responsáveis por calibração, limpeza, troca de consumíveis e atendimento de alarmes.
6. Preparar ambiente de execução, permissões, backup, sincronização de relógio e monitoramento do processo.

## 11. Riscos e controles

| Risco | Probabilidade | Impacto | Controle |
|---|---|---|---|
| Mapa de registradores ou endianness incorreto | Média | Alto | Ensaio com valores conhecidos, documentação por modelo e teste automatizado |
| Interferência ou aterramento inadequado no RS-485 | Média | Alto | Cabeamento apropriado, terminação, proteção e teste de sinal |
| Deriva de calibração da sonda | Média | Alto | Plano de calibração, inspeção, registro de validade e análise de plausibilidade |
| Perda de energia ou conexão | Média | Médio | Reconexão, alerta operacional, nobreak quando necessário e procedimento de retomada |
| Dependência de pessoa-chave | Média | Médio | Código versionado, documentação, treinamento e testes reproduzíveis |
| Dados inválidos aceitos como válidos | Baixa/Média | Alto | Validação de faixa, flag de validade, revisão técnica e teste de aceitação |

## 12. Sustentabilidade

A solução deve priorizar reaproveitamento de infraestrutura existente, manutenção e substituição modular, baixo consumo do gateway e descarte adequado de sondas, cabos, baterias e componentes eletrônicos. O fornecedor deve informar procedimentos de logística reversa quando aplicáveis e evitar materiais ou licenças que criem dependência desnecessária.

## 13. Modelo de execução, medição e aceitação

O fornecedor/implantador deverá entregar a solução configurada, documentação e evidências de teste. A aceitação mínima deverá demonstrar, para cada ponto:

- comunicação estável pelo período de teste definido;
- leitura dos canais contratados com valores de referência;
- decodificação correta dos registradores;
- tratamento de timeout e resposta de exceção;
- registro de timestamp, status e mensagem de erro;
- procedimento documentado de reconexão, calibração e operação.

O pagamento e a medição devem ser vinculados aos itens efetivamente entregues e aceitos, conforme o instrumento contratual.

## 14. Conclusão

Com base nas informações disponíveis, a solução de aquisição Modbus-RTU/RS-485 apoiada por software Python aberto é tecnicamente viável e atende melhor à necessidade de flexibilidade, auditabilidade e operação contínua. A contratação somente deve avançar após completar quantitativos, local, responsabilidades, pesquisa de preços, mapa de registradores validado e requisitos de armazenamento/telemetria.

**Elaborado por:** `[PREENCHER]`  
**Aprovado por:** `[PREENCHER]`  
**Data:** `[PREENCHER]`