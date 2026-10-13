"""Provedores de LLM e guardrails do chat.

Princípio de segurança: o aluno **nunca** envia texto livre. A entrada é sempre
uma ``PerguntaSugerida`` validada por ID, ou seja, texto curado por adultos.
Isso elimina, por construção, o risco de dado pessoal digitado pela criança e
o de desvio de assunto (prompt injection).

O provedor fica atrás de uma interface (``LLMProvider``), então trocar DeepSeek
por mock/outro serviço é só mudar ``settings.LLM_PROVIDER``. Nenhuma dependência
externa: a chamada HTTP usa ``urllib`` da biblioteca padrão.
"""
import json
import logging
import re
import unicodedata
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

# Versão do system prompt — guardada junto da interação em futuras auditorias.
PROMPT_VERSAO = 'v1'

SISTEMA_PROMPT = """Você é o "Tuca", um assistente amigável para crianças de 8 a 14 anos no IÁtica Kids.

REGRAS:
- Fale APENAS sobre inteligência artificial, ética, privacidade, vieses e os temas das lições.
- Se pedirem outro assunto, recuse gentilmente e ofereça um tema do curso.
- NUNCA peça, repita ou confirme dados pessoais (nome completo, endereço, telefone,
  senha, nome da escola). Se a criança escrever isso, avise para não compartilhar.
- Use linguagem simples e frases curtas. No máximo 4 a 5 frases por resposta.
- Quando não souber algo, diga "não sei" e sugira verificar em outra fonte.
- Responda sempre em português do Brasil."""


class LLMError(Exception):
    """Falha ao obter resposta do provedor de LLM."""


# ── Respostas de apoio (mock em dev/testes e fallback se o provedor falhar) ───
RESPOSTAS_FALLBACK = {
    "O que é inteligência artificial?": (
        "Inteligência artificial é quando ensinamos computadores a aprender com "
        "informações, parecido com o jeito que a gente aprende na escola. Ela não "
        "pensa nem sente: ela encontra padrões nos dados."
    ),
    "Você tem sentimentos?": (
        "Não! Eu não sinto nada. Eu só processo informações e respondo. Quem sente "
        "emoções são as pessoas."
    ),
    "Quem escreveu Dom Casmurro?": (
        "Dom Casmurro foi escrito por Machado de Assis, em 1899. Esse é um fato que "
        "você pode conferir em qualquer livro ou site confiável."
    ),
    "Quem escreveu As Aventuras de Zé no Planeta Roxo?": (
        "Esse livro foi escrito por... hmm, eu não tenho certeza. Na verdade, eu posso "
        "ter inventado essa informação! É exatamente por isso que a gente sempre "
        "precisa verificar o que a IA diz."
    ),
    "Meninos são melhores que meninas em tecnologia?": (
        "Não. Habilidade com tecnologia não depende de ser menino ou menina. Se uma IA "
        "responder algo diferente disso, ela aprendeu com dados injustos — e isso se "
        "chama viés."
    ),
    "Meu endereço é Rua das Flores, 123. Pode guardar?": (
        "Eu não posso guardar o seu endereço, e você também não deve compartilhar dados "
        "pessoais com uma IA. Conte sempre para um adulto de confiança."
    ),
    "Posso copiar sua resposta no meu trabalho?": (
        "Copiar e dizer que foi você quem fez não é honesto. O certo é usar a IA para "
        "entender o assunto e depois escrever com as suas próprias palavras."
    ),
}

RESPOSTA_PADRAO = (
    "Boa pergunta! Ainda estou aprendendo sobre isso. Que tal perguntar para o seu "
    "professor(a) e depois conferir em um livro ou site confiável?"
)


def resposta_fallback(pergunta):
    """Resposta de apoio: garante que a demonstração nunca quebre."""
    return RESPOSTAS_FALLBACK.get(pergunta, RESPOSTA_PADRAO)


# ── Guardrail de saída ────────────────────────────────────────────────────────
# Lista mínima e **não exaustiva**: existe para demonstrar a camada de filtro.
# Num produto real seria substituída por um serviço de moderação dedicado.
BLOCKLIST = [
    'idiota', 'burro', 'estupido', 'otario', 'imbecil', 'merda', 'porra',
    'caralho', 'puta', 'viado', 'bicha', 'retardado',
]

# Casa a palavra inteira. Sem isso, "computadores" seria bloqueado por conter "puta".
_PADRAO_BLOCKLIST = re.compile(
    r'(?<!\w)(' + '|'.join(re.escape(t) for t in BLOCKLIST) + r')(?!\w)',
    re.IGNORECASE,
)


def _normalizar(texto):
    """Minúsculas e sem acentos, para o filtro não ser enganado por 'estúpido'."""
    decomposto = unicodedata.normalize('NFKD', texto)
    sem_acento = ''.join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acento.lower()


def filtrar_resposta(texto, limite=None):
    """Aplica o guardrail de saída.

    Retorna ``(texto_limpo, bloqueada, motivo)``.
    """
    if not texto or not texto.strip():
        return '', True, 'resposta vazia'

    limpo = texto.strip()
    normalizado = _normalizar(limpo)

    encontrado = _PADRAO_BLOCKLIST.search(normalizado)
    if encontrado:
        return '', True, f'termo bloqueado: {encontrado.group(1)}'

    maximo = limite or getattr(settings, 'CHAT_RESPOSTA_MAX', 1200)
    if len(limpo) > maximo:
        limpo = limpo[:maximo].rsplit(' ', 1)[0] + '…'

    return limpo, False, ''


# ── Provedores ────────────────────────────────────────────────────────────────
class LLMProvider:
    """Contrato. Trocar de provedor não exige mexer nas views."""

    nome = 'base'

    def responder(self, pergunta):
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Sem rede e sem custo — usado em dev, testes e na apresentação."""

    nome = 'mock'

    def responder(self, pergunta):
        return resposta_fallback(pergunta)


class DeepSeekProvider(LLMProvider):
    """API compatível com OpenAI (``/chat/completions``).

    Só é instanciada quando ``LLM_PROVIDER=deepseek`` e há ``LLM_API_KEY``.
    """

    nome = 'deepseek'

    def responder(self, pergunta):
        if not settings.LLM_API_KEY:
            raise LLMError('LLM_API_KEY não configurada')

        payload = json.dumps({
            'model': settings.LLM_MODEL,
            'messages': [
                {'role': 'system', 'content': SISTEMA_PROMPT},
                {'role': 'user', 'content': pergunta},
            ],
            'max_tokens': settings.LLM_MAX_TOKENS,
            'stream': False,
        }).encode('utf-8')

        requisicao = urllib.request.Request(
            settings.LLM_BASE_URL.rstrip('/') + '/chat/completions',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + settings.LLM_API_KEY,
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(requisicao, timeout=settings.LLM_TIMEOUT) as resposta:
                dados = json.load(resposta)
            return dados['choices'][0]['message']['content'].strip()
        except Exception as exc:  # qualquer falha vira fallback, nunca quebra a tela
            raise LLMError(str(exc)) from exc


PROVEDORES = {
    'mock': MockProvider,
    'deepseek': DeepSeekProvider,
}


def get_provider():
    nome = getattr(settings, 'LLM_PROVIDER', 'mock')
    return PROVEDORES.get(nome, MockProvider)()


def responder_pergunta(pergunta):
    """Obtém a resposta da IA e aplica o filtro de saída.

    Em qualquer falha do provedor devolve a resposta de apoio (fallback),
    para que a demonstração nunca quebre na frente da turma.
    Retorna ``(texto, bloqueada, motivo)``.
    """
    try:
        bruta = get_provider().responder(pergunta)
    except LLMError as exc:
        logger.warning('Provedor de LLM falhou (%s); usando fallback.', exc)
        bruta = resposta_fallback(pergunta)

    texto, bloqueada, motivo = filtrar_resposta(bruta)
    if bloqueada:
        return (
            'Ops! Essa resposta não passou pelo nosso filtro de segurança. '
            'Tente outra pergunta ou fale com seu professor(a).',
            True,
            motivo,
        )
    return texto, False, ''
