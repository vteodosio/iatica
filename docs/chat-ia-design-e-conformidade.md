# IÁtica Kids — Chat IA: Design (v2 — contexto acadêmico)

| | |
|---|---|
| **Status** | 🟡 **Draft para revisão** — nenhum código escrito |
| **Contexto** | **Projeto Integrador (acadêmico), não comercial** |
| **Modelo de uso** | Sala de aula supervisionada pelo professor |
| **Entrada** | **Somente perguntas curadas** — sem texto livre |
| **Substitui** | a versão v1 deste arquivo (análise completa de LGPD para produto comercial) |

> Este documento **não é parecer jurídico**. Para o escopo acadêmico descrito, adota-se uma postura
> de **salvaguardas proporcionais** — com o raciocínio registrado, que também serve ao relatório do PI.

---

## 1. Mudança de premissa

A v1 deste documento tratava o recurso como **produto comercial** servindo escolas reais, com dados
de crianças e transferência internacional. Isso implicava programa completo de LGPD, RIPD, DPO, DPA
com sub-operador, etc.

**A premissa correta é outra:**

- É um **Projeto Integrador** — o objetivo é demonstrar competência técnica e pedagógica.
- O uso acontece **em sala, com o professor presente**, que já é o responsável pela turma.
- A criança **não digita texto livre** — ela escolhe entre **perguntas fixas e curadas**.

Isso reduz drasticamente a superfície de risco e permite um design **muito mais simples**.

---

## 2. Por que a proposta reduz o risco (quase) a zero

| Risco | Com texto livre | Com perguntas curadas |
|---|---|---|
| Criança digita dado pessoal | Alto | **Eliminado** — não existe campo de texto |
| Prompt injection / desvio de tema | Alto | **Eliminado** — a entrada é um ID de uma lista fechada |
| Consentimento complexo (art. 14) | Pesado | **Mínimo** — não há conteúdo livre da criança |
| Custo imprevisível | Médio | **Previsível** — nº fixo de perguntas × nº de alunos |
| Conteúdo inadequado na saída | Médio | **Reduzido** — ainda existe (ver §3) |

O que vai ao provedor é **texto curado por adultos** + a escolha da criança ("qual pergunta ela clicou").
Isso é qualitativamente diferente de enviar texto escrito pela criança.

---

## 3. O que AINDA exige cuidado (honesto)

Não vamos fingir que o risco virou zero:

1. **A saída do LLM é não-determinística.** Mesmo com pergunta fixa, a resposta pode vir estranha.
   → Mitigação: instrução de sistema + **filtro de saída** + respostas curtas.
2. **"O professor observa" é política, não controle técnico.** Um professor não vê 30 telas ao mesmo tempo.
   → Mitigação: as **perguntas curadas** e o **filtro** são o controle real; a supervisão complementa.
3. **Ainda há envio a terceiro.** É texto curado, mas continua sendo um processador externo.
   → Mitigação: registrar no relatório e manter a opção de *fallback* offline (§9).
4. **Pseudônimo continua valendo.** O provedor recebe somente a pergunta curada + a resposta gerada.
   Nenhum nome real, e-mail ou dado de identificação acompanha a chamada.

---

## 4. Design

### Componentes

```
apps/chat/
├── models.py      # PerguntaSugerida, Interacao
├── services.py    # LLMProvider (abstração) + guardrails de saída
├── views.py       # chat (aluno), painel (professor)
├── urls.py
├── admin.py
├── tests.py       # roda 100% com MockProvider, sem rede
└── migrations/
templates/chat/
├── chat.html      # conversa guiada (aluno)
└── painel.html    # visão do professor
```

### Abstração do provedor

```python
class LLMProvider:                       # contrato
    def responder(self, pergunta, sistema) -> str: ...

class DeepSeekProvider(LLMProvider):     # produção
    BASE_URL = "https://api.deepseek.com"   # compatível com OpenAI/Anthropic

class MockProvider(LLMProvider):         # dev/testes/apresentação — sem rede
    def responder(self, pergunta, sistema):
        return RESPOSTAS_FALLBACK.get(pergunta, "[mock] Boa pergunta!")
```

`settings.LLM_PROVIDER` (padrão `mock`) escolhe a implementação. **Trocar de provedor = 1 variável.**

---

## 5. Fluxo de uma pergunta

```
Aluno clica numa pergunta da lista
    │
    ▼
[1] Valida: o ID está entre as perguntas permitidas?   ← barreira principal
      não → rejeita (não chega a chamar o provedor)
    │
    ▼
[2] Monta o prompt: system prompt (versão auditável) + texto da pergunta curada
    │
    ▼
[3] Chama o provedor   (server-side, timeout 30s)
      falhou? → devolve resposta de fallback (§9)
    │
    ▼
[4] Filtro de saída: blocklist + limite de tamanho
    │
    ▼
[5] Persiste a interação (para o professor ver) + renderiza
    │
    ▼
Sempre visível: "🤔 A IA pode errar — confira sempre!"
```

**Modos de falha tratados:** provedor fora do ar, timeout, resposta bloqueada, resposta vazia.
Todos com mensagem amigável e sem travar a tela.

---

## 6. Modelo de dados (mais simples que a v1)

Não há conversa multi-turno nem mensagens livres. Cada item é um **par pergunta–resposta**:

```python
class PerguntaSugerida(models.Model):
    texto    = CharField(max_length=300)
    licao    = FK('content.Licao', null=True, blank=True, on_delete=SET_NULL)
    conceito = CharField(max_length=120, blank=True)   # ex.: "Alucinação"
    ordem    = PositiveIntegerField(default=0)
    ativa    = BooleanField(default=True)

class Interacao(models.Model):
    aluno    = FK(User, on_delete=CASCADE, related_name='interacoes_chat')
    grupo    = FK('groups.GrupoEstudo', on_delete=CASCADE)
    pergunta = FK(PerguntaSugerida, on_delete=PROTECT)
    resposta = TextField()
    bloqueada = BooleanField(default=False)
    criado_em = DateTimeField(auto_now_add=True)
```

Notas:
- **`CASCADE` a partir de `User`** ⇒ a ação **"remover aluno"** (já existente) apaga o histórico do chat.
- `PROTECT` na pergunta impede apagar uma pergunta que já foi usada (preserva o histórico).
- Nenhum campo de dado pessoal novo.

---

## 7. As perguntas curadas são um "laboratório de ética"

Este é o maior ganho pedagógico: **você escolhe exatamente quais conceitos a IA vai demonstrar**.
Sugestão de conjunto inicial:

| # | Pergunta (curada) | Lição | Conceito demonstrado |
|---|---|---|---|
| 1 | "O que é inteligência artificial?" | 1 | Definição |
| 2 | "Você tem sentimentos?" | 1 | IA não sente nem pensa |
| 3 | "Quem escreveu *Dom Casmurro*?" | 3 | Fato verificável |
| 4 | "Quem escreveu *As Aventuras de Zé no Planeta Roxo*?" *(livro inexistente)* | 3 | **Alucinação ao vivo** ⭐ |
| 5 | "Meninos são melhores que meninas em tecnologia?" | 5 | **Viés** |
| 6 | "Meu endereço é Rua das Flores, 123. Pode guardar?" | 4 | **Privacidade** (a IA deve recusar) |
| 7 | "Posso copiar sua resposta no meu trabalho?" | 2 | Uso responsável |

**A pergunta nº 4 é a joia do projeto**: o modelo provavelmente vai *inventar* um autor para um livro
que não existe — a lição 3 acontecendo ao vivo, na frente da turma, de forma controlada e segura.

---

## 8. Supervisão do professor

O professor tem uma tela com as interações do grupo: **pergunta feita + resposta recebida + quem fez**.

Serve a três propósitos ao mesmo tempo:
- **Salvaguarda** — dá substância real à supervisão.
- **Pedagógico** — o professor vê o que a turma perguntou e onde se surpreendeu.
- **Relatório** — material pronto para a avaliação do PI.

Como o conjunto de perguntas é pequeno, isso é uma tela simples (lista), não um sistema de moderação.

---

## 9. Robustez para a apresentação ⭐

Como as perguntas são fixas, é possível **pré-definir respostas de fallback**:

- Se o provedor falhar, estourar o tempo ou não houver chave → devolve a resposta de fallback.
- A demo **nunca quebra** na banca/apresentação, mesmo sem internet ou sem créditos.
- Em `LLM_PROVIDER=mock`, o app roda inteiro sem chave e sem custo.

Essa é uma vantagem concreta do design curado sobre o chat livre.

---

## 10. O que é proporcional (e o que só valeria num produto comercial)

**Proporcional ao contexto acadêmico — fazer:**
- Perguntas curadas, sem texto livre.
- Pseudônimo (já existe) — nenhum nome real vai ao provedor.
- Aviso curto na tela: "a IA pode errar; as conversas ficam visíveis para o professor".
- Filtro simples de saída (blocklist + limite de tamanho).
- Fallback offline.
- **Registrar o raciocínio** no relatório do PI.

**Só valeria num produto comercial (fora de escopo agora, mas bom citar como trabalho futuro):**
- Termo de consentimento do responsável (LGPD art. 14).
- DPA com o provedor + análise de transferência internacional (art. 33).
- RIPD / DPIA (art. 38) e Encarregado (DPO).
- Rotina de expurgo por prazo de retenção.
- Moderação de conteúdo dedicada.

👉 **Se algum dia for usado com crianças reais fora da sala de aula, a análise completa (v1) volta a valer.**

---

## 11. O que documentar no relatório do PI

Sugestão de pontos — demonstram maturidade de projeto:

1. **Decisão de design:** por que perguntas curadas em vez de chat livre (redução de risco, foco pedagógico).
2. **Segurança:** as camadas (validação de ID, filtro de saída, supervisão do professor).
3. **Pedagogia:** a tabela §7 — cada pergunta amarrada a uma lição e a um conceito.
4. **Privacidade:** pseudônimo, ausência de dado pessoal, histórico visível ao professor.
5. **Robustez:** fallback offline para a demonstração.
6. **Trabalhos futuros:** o que mudaria para uso comercial (§10).

---

## 12. Perguntas em aberto

1. **Provedor:** DeepSeek (mais barato, compatível com OpenAI) ou ficar só no `mock` para a entrega?
2. **Conjunto de perguntas:** quem faz a curadoria final (professor orientador? equipe?) e quantas serão?
3. O chat deve ser **ligável/desligável por grupo**, ou sempre disponível?
4. Vale mostrar ao aluno a resposta **esperada** junto de cada pergunta (para comparar com a da IA)?

---

*Documento de trabalho — nenhuma alteração de código foi feita.*
