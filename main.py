import pygame
from recursos.funcoes.funcionalidades import dadosEmThread
from recursos.funcoes.funcionalidades import configuracoesDificuldade

# Inicialização do Pygame
pygame.init()
tela = pygame.display.set_mode((1000, 700))
fps = pygame.time.Clock()
rodando = True

# Telas
telaInicial = pygame.image.load("recursos/imagens/telas/telaInicio.png")
telaJogo = pygame.image.load("recursos/imagens/telas/telaJogo.png")
telaMorte = pygame.image.load("recursos/imagens/telas/telaMorte.png")

# Botões
botaoStart = pygame.Rect(412, 448, 185, 75, border_radius=10)
botaoSair = pygame.Rect(412, 550, 185, 75, border_radius=10)

# Variáveis do jogo
jogoIniciado = False
nomeJogador = ""
dificuldade = ""

# Personagem
personagemParado = pygame.image.load("recursos/imagens/personagem/personagemParado.png")
personagemAndando = [
    pygame.image.load("recursos/imagens/personagem/personagemAndando1.png"),
    pygame.image.load("recursos/imagens/personagem/personagemAndando2.png"),
    pygame.image.load("recursos/imagens/personagem/personagemAndando3.png")
]
personagemPulando = pygame.image.load("recursos/imagens/personagem/personagemPulando.png")
posicaoX = 500
posicaoY = 535
velocidade = 5
noChao = True
velocidadePulo = 0
gravidade = 1
forcaPulo = -17
frameAtual = 0
frameTimer = 0
viradoPraEsquerda = False



# Callback para receber os dados da thread
def definirDadosJogador(nome, dif):
    global nomeJogador, dificuldade, jogoIniciado
    nomeJogador = nome
    dificuldade = dif
    jogoIniciado = True

    configuracoesDificuldade(dificuldade)


# Loop principal do jogo
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            if not jogoIniciado and botaoStart.collidepoint(mouse_x, mouse_y):
                dadosEmThread(definirDadosJogador)

            if not jogoIniciado and botaoSair.collidepoint(mouse_x, mouse_y):
                rodando = False

    # Movimento e animações
    teclas = pygame.key.get_pressed()
    andando = False

    if jogoIniciado:
        if teclas[pygame.K_a]:
            posicaoX -= velocidade
            andando = True
            viradoPraEsquerda = True

        if teclas[pygame.K_d]:
            posicaoX += velocidade
            andando = True
            viradoPraEsquerda = False
        
        if posicaoX <= 200:
            posicaoX = 200
        if posicaoX >= 700:
            posicaoX = 700

        if teclas[pygame.K_w] and noChao:
            velocidadePulo = forcaPulo  
            noChao = False

    
    if not noChao:
        velocidadePulo += gravidade
        posicaoY += velocidadePulo
        if posicaoY >= 535: 
            posicaoY = 535
            velocidadePulo = 0
            noChao = True

   
    if not noChao:
        img = personagemPulando
    elif andando:
        frameTimer += 1
        if frameTimer >= 10:
            frameTimer = 0
            frameAtual = (frameAtual + 1) % len(personagemAndando)
        img = personagemAndando[frameAtual]
    else:
        img = personagemParado

    if viradoPraEsquerda:
        img = pygame.transform.flip(img, True, False)


    tela.blit(img, (posicaoX, posicaoX))
    tela.fill("#220202")


    if jogoIniciado:
        tela.blit(telaJogo, (0, 0))
        tela.blit(img, (posicaoX, posicaoY))  
    else:
        tela.blit(telaInicial, (0, 0))

    pygame.display.flip()
    fps.tick(144)

pygame.quit()
