from django.core.management.base import BaseCommand
from apps.content.models import Licao
from apps.quiz.models import Pergunta, Alternativa


LICOES = [
    {
        "ordem": 1,
        "icone": "🤖",
        "cor_tema": "#f59e0b",
        "titulo": "O que é Inteligência Artificial?",
        "subtitulo": "Vamos descobrir como os computadores aprendem!",
        "conteudo_html": """
<div class="lesson-body">
  <p class="lead-text">Você já percebeu que quando você assiste a um vídeo no YouTube, o site logo sugere outros vídeos parecidos? Ou que o corretor do celular já sabe qual palavra você quer digitar? Isso é <strong>Inteligência Artificial</strong> em ação!</p>
  <div class="highlight-box">
    <span class="highlight-icon">💡</span>
    <p><strong>Inteligência Artificial (IA)</strong> é quando ensinamos os computadores a resolver problemas e aprender com informações, parecido com o jeito que nós aprendemos na escola!</p>
  </div>
  <h3>Como um computador aprende?</h3>
  <p>Imagina que você quer ensinar um robô a reconhecer um cachorro. Você mostra <strong>milhares de fotos</strong> de cachorros e diz: "isso é um cachorro". Depois de ver tantas fotos, o robô começa a aprender o que é um cachorro sozinho!</p>
  <div class="example-cards">
    <div class="example-card">
      <span class="example-icon">🎵</span>
      <h4>Spotify</h4>
      <p>Aprende as músicas que você curte e recomenda novas!</p>
    </div>
    <div class="example-card">
      <span class="example-icon">🎮</span>
      <h4>Jogos</h4>
      <p>Os inimigos nos jogos usam IA para jogar melhor contra você!</p>
    </div>
    <div class="example-card">
      <span class="example-icon">📱</span>
      <h4>Face ID</h4>
      <p>Reconhece seu rosto para desbloquear o celular.</p>
    </div>
  </div>
  <div class="curiosity-box">
    <span>🧠</span>
    <p><strong>Curiosidade:</strong> A IA não tem sentimentos! Ela não sente felicidade, tristeza ou amor. Ela apenas processa informações muito rapidamente.</p>
  </div>
</div>
""",
    },
    {
        "ordem": 2,
        "icone": "✅",
        "cor_tema": "#10b981",
        "titulo": "Usando a IA com Responsabilidade",
        "subtitulo": "Como ser um usuário inteligente!",
        "conteudo_html": """
<div class="lesson-body">
  <p class="lead-text">A IA pode ser uma ferramenta incrível para aprender, criar e descobrir coisas novas. Mas assim como uma faca serve para cortar frutas ou para machucar, a IA também depende de como a gente usa!</p>
  <div class="highlight-box green">
    <span class="highlight-icon">🌟</span>
    <p>Usar a IA com responsabilidade significa usá-la para <strong>crescer, aprender e ajudar</strong> as pessoas — nunca para enganar ou prejudicar.</p>
  </div>
  <h3>✅ Usos Legais da IA</h3>
  <ul class="good-list">
    <li>🔍 Pesquisar e entender assuntos difíceis</li>
    <li>✍️ Pedir ajuda para melhorar um texto que você escreveu</li>
    <li>🎨 Usar para criar arte ou músicas novas</li>
    <li>🗣️ Praticar um idioma novo</li>
    <li>🧪 Explorar experimentos científicos</li>
  </ul>
  <h3>❌ Cuidados Importantes</h3>
  <ul class="bad-list">
    <li>🚫 Não copie respostas da IA e diga que são suas — isso é desonesto</li>
    <li>🚫 Não acredite em tudo que a IA fala sem verificar</li>
    <li>🚫 Não compartilhe informações pessoais com IAs</li>
    <li>🚫 Não use a IA para fazer bullying ou enganar alguém</li>
  </ul>
  <div class="curiosity-box">
    <span>🤔</span>
    <p><strong>Pense nisso:</strong> Se você pede para a IA fazer toda sua lição de casa, quem aprende? A IA já sabe! Você perde a chance de aprender algo novo.</p>
  </div>
</div>
""",
    },
    {
        "ordem": 3,
        "icone": "🔍",
        "cor_tema": "#6366f1",
        "titulo": "A IA Mente? Entendendo as Alucinações",
        "subtitulo": "Por que você sempre deve checar as informações!",
        "conteudo_html": """
<div class="lesson-body">
  <p class="lead-text">Aqui vai um segredo importante: <strong>a IA pode errar!</strong> Às vezes, ela inventa informações que parecem verdadeiras, mas não são. Os especialistas chamam isso de "alucinação".</p>
  <div class="highlight-box purple">
    <span class="highlight-icon">⚠️</span>
    <p><strong>Alucinação da IA:</strong> quando a IA cria uma resposta que parece correta, mas na verdade é falsa ou inventada. Ela não mente de propósito — ela simplesmente não sabe que está errando!</p>
  </div>
  <h3>Por que a IA erra?</h3>
  <p>A IA aprende com textos escritos por pessoas. E as pessoas às vezes erram ou escrevem coisas incorretas. A IA absorve esses erros junto com as informações certas e pode misturar tudo.</p>
  <div class="example-cards">
    <div class="example-card warn">
      <span class="example-icon">📚</span>
      <h4>Exemplo</h4>
      <p>Você pergunta "Quem escreveu Dom Casmurro?" e a IA responde corretamente: "Machado de Assis". Mas se perguntar sobre um livro inventado, ela pode inventar um autor!</p>
    </div>
  </div>
  <h3>Como se proteger?</h3>
  <ul class="good-list">
    <li>🔍 Sempre verifique informações importantes em outras fontes (livros, sites confiáveis)</li>
    <li>👩‍🏫 Pergunte para um adulto de confiança se tiver dúvida</li>
    <li>📰 Use sites de notícias conhecidos para checar fatos</li>
    <li>🧐 Desconfie de respostas muito detalhadas sobre coisas obscuras</li>
  </ul>
  <div class="curiosity-box">
    <span>🕵️</span>
    <p><strong>Seja um detetive!</strong> Antes de usar uma informação da IA em um trabalho escolar, sempre confirme em pelo menos 2 outras fontes.</p>
  </div>
</div>
""",
    },
    {
        "ordem": 4,
        "icone": "🔒",
        "cor_tema": "#ef4444",
        "titulo": "Privacidade e Segurança com a IA",
        "subtitulo": "Protegendo suas informações pessoais!",
        "conteudo_html": """
<div class="lesson-body">
  <p class="lead-text">Você não contaria sua senha para um estranho na rua, certo? Com a IA é a mesma coisa! Existem informações que você nunca deve compartilhar com ferramentas de IA.</p>
  <div class="highlight-box red">
    <span class="highlight-icon">🔐</span>
    <p><strong>Privacidade digital</strong> é o direito de proteger suas informações pessoais. Na internet e com a IA, isso é muito importante!</p>
  </div>
  <h3>🚫 Nunca compartilhe com a IA:</h3>
  <ul class="bad-list">
    <li>📍 Seu endereço ou onde você mora</li>
    <li>📞 Seu número de telefone</li>
    <li>🔑 Senhas de qualquer coisa</li>
    <li>💳 Dados de cartão ou informações financeiras da família</li>
    <li>📸 Fotos suas sem autorização dos pais</li>
    <li>🏫 Nome completo + escola + série juntos</li>
  </ul>
  <h3>Por quê?</h3>
  <p>Quando você escreve em um chat de IA, essas mensagens podem ser armazenadas em servidores. Pessoas mal-intencionadas poderiam usar essas informações para te prejudicar ou prejudicar sua família.</p>
  <div class="highlight-box green">
    <span class="highlight-icon">👨‍👩‍👧</span>
    <p><strong>Regra de ouro:</strong> Sempre converse com seus pais ou responsável antes de usar uma ferramenta de IA pela primeira vez!</p>
  </div>
  <div class="curiosity-box">
    <span>🛡️</span>
    <p><strong>Lembre-se:</strong> Você tem o direito de proteger sua privacidade. Se alguém te pedir para compartilhar informações pessoais online, fale com um adulto de confiança.</p>
  </div>
</div>
""",
    },
    {
        "ordem": 5,
        "icone": "⚖️",
        "cor_tema": "#8b5cf6",
        "titulo": "Ética e Justiça nas Respostas da IA",
        "subtitulo": "A IA pode ser justa ou injusta?",
        "conteudo_html": """
<div class="lesson-body">
  <p class="lead-text">Você já ouviu falar que um juiz deve ser imparcial? Que ele não pode favorecer uma pessoa por causa de sua cor, religião ou de onde ela vem? A IA também precisa ser assim — mas nem sempre é!</p>
  <div class="highlight-box">
    <span class="highlight-icon">⚖️</span>
    <p><strong>Viés (ou preconceito) na IA:</strong> quando uma IA trata pessoas de forma injusta porque aprendeu com dados que continham preconceitos humanos.</p>
  </div>
  <h3>Como isso acontece?</h3>
  <p>Se você treina uma IA para reconhecer "um bom médico" usando apenas fotos de médicos homens, ela vai aprender que médicos são homens — ignorando todas as médicas mulheres! Isso é injusto e errado.</p>
  <div class="example-cards">
    <div class="example-card">
      <span class="example-icon">🌍</span>
      <h4>Diversidade</h4>
      <p>IAs boas aprendem com pessoas de todos os países, cores e culturas.</p>
    </div>
    <div class="example-card">
      <span class="example-icon">👥</span>
      <h4>Inclusão</h4>
      <p>Todos merecem ser representados nos dados que ensinam a IA.</p>
    </div>
  </div>
  <h3>O que você pode fazer?</h3>
  <ul class="good-list">
    <li>🗣️ Se perceber que uma IA está sendo injusta, fale sobre isso</li>
    <li>🤝 Trate todos com respeito, inclusive ao usar IA</li>
    <li>🌈 Valorize a diversidade nas tecnologias que você usa</li>
    <li>📢 Seja uma voz para a IA mais justa no futuro</li>
  </ul>
  <div class="curiosity-box">
    <span>🚀</span>
    <p><strong>Você pode mudar o futuro!</strong> Os desenvolvedores de IA de amanhã são as crianças de hoje. Aprender sobre ética agora te prepara para criar tecnologias mais justas!</p>
  </div>
</div>
""",
    },
]

PERGUNTAS = [
    {
        "texto": "O que é Inteligência Artificial?",
        "ordem": 1,
        "alternativas": [
            {"texto": "Um robô que tem sentimentos humanos", "correta": False},
            {"texto": "Quando ensinamos computadores a resolver problemas e aprender com informações", "correta": True},
            {"texto": "Um videogame muito avançado", "correta": False},
            {"texto": "Uma rede social para computadores", "correta": False},
        ]
    },
    {
        "texto": "Qual destes é um exemplo de uso RESPONSÁVEL da IA?",
        "ordem": 2,
        "alternativas": [
            {"texto": "Copiar a resposta da IA e dizer que é sua", "correta": False},
            {"texto": "Compartilhar seu endereço com um chatbot", "correta": False},
            {"texto": "Pedir ajuda para entender um conceito difícil", "correta": True},
            {"texto": "Usar a IA para fazer bullying com um colega", "correta": False},
        ]
    },
    {
        "texto": "O que é uma 'alucinação' da IA?",
        "ordem": 3,
        "alternativas": [
            {"texto": "Quando a IA fica com medo de alguma coisa", "correta": False},
            {"texto": "Quando a IA inventa informações que parecem verdadeiras mas são falsas", "correta": True},
            {"texto": "Quando a IA sonha enquanto está desligada", "correta": False},
            {"texto": "Quando a IA vê imagens que não existem", "correta": False},
        ]
    },
    {
        "texto": "Qual informação NUNCA deve ser compartilhada com uma IA?",
        "ordem": 4,
        "alternativas": [
            {"texto": "Sua cor favorita", "correta": False},
            {"texto": "O nome de um personagem de desenho que você gosta", "correta": False},
            {"texto": "Sua senha e endereço de casa", "correta": True},
            {"texto": "O nome de uma música que você curtiu", "correta": False},
        ]
    },
    {
        "texto": "O que é 'viés' (preconceito) na IA?",
        "ordem": 5,
        "alternativas": [
            {"texto": "Quando a IA fica com preguiça de responder", "correta": False},
            {"texto": "Quando a IA trata pessoas de forma injusta por causa de preconceitos nos dados", "correta": True},
            {"texto": "Quando a IA escolhe a cor favorita dela", "correta": False},
            {"texto": "Quando a IA fica lenta demais", "correta": False},
        ]
    },
    {
        "texto": "Antes de usar uma informação que a IA deu em um trabalho escolar, o que você deve fazer?",
        "ordem": 6,
        "alternativas": [
            {"texto": "Usar direto, pois a IA sempre está certa", "correta": False},
            {"texto": "Verificar em pelo menos 2 outras fontes confiáveis", "correta": True},
            {"texto": "Pedir para a IA confirmar a própria resposta", "correta": False},
            {"texto": "Perguntar para outro aluno se ele acredita", "correta": False},
        ]
    },
    {
        "texto": "Por que é importante que a IA seja treinada com dados de pessoas de culturas diversas?",
        "ordem": 7,
        "alternativas": [
            {"texto": "Para a IA aprender mais idiomas", "correta": False},
            {"texto": "Para tornar a IA mais justa e representativa para todos", "correta": True},
            {"texto": "Para a IA ficar mais rápida", "correta": False},
            {"texto": "Para economizar energia no servidor", "correta": False},
        ]
    },
    {
        "texto": "Se seus pais nunca ouviram falar de uma ferramenta de IA que você quer usar, o que é mais correto?",
        "ordem": 8,
        "alternativas": [
            {"texto": "Usar escondido, pois você sabe mais de tecnologia", "correta": False},
            {"texto": "Conversar com eles e explicar o que é a ferramenta antes de usar", "correta": True},
            {"texto": "Perguntar só para seus amigos", "correta": False},
            {"texto": "Usar qualquer ferramenta, pois IA é sempre segura", "correta": False},
        ]
    },
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com lições e quiz padrão sobre ética e IA'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando lições...')
        for dados in LICOES:
            licao, criada = Licao.objects.update_or_create(
                ordem=dados['ordem'],
                defaults={
                    'titulo': dados['titulo'],
                    'subtitulo': dados['subtitulo'],
                    'conteudo_html': dados['conteudo_html'],
                    'icone': dados['icone'],
                    'cor_tema': dados['cor_tema'],
                    'ativa': True,
                }
            )
            status = '✅ Criada' if criada else '🔄 Atualizada'
            self.stdout.write(f'  {status}: {licao}')

        self.stdout.write('\nCriando banco de perguntas padrão...')
        from apps.quiz.models import Pergunta, Alternativa
        for dados in PERGUNTAS:
            pergunta, criada = Pergunta.objects.update_or_create(
                ordem=dados['ordem'],
                defaults={'texto': dados['texto']}
            )
            Alternativa.objects.filter(pergunta=pergunta).delete()
            for alt in dados['alternativas']:
                Alternativa.objects.create(
                    pergunta=pergunta,
                    texto=alt['texto'],
                    correta=alt['correta']
                )
            status = '✅ Criada' if criada else '🔄 Atualizada'
            self.stdout.write(f'  {status}: {pergunta}')

        self.stdout.write(self.style.SUCCESS('\n🎉 Dados populados com sucesso!'))
