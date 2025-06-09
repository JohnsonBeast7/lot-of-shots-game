import pygame
import random
import math
from recursos.funcoes.funcionalidades import dadosEmThread
from recursos.funcoes.funcionalidades import configuracoesDificuldade
from pygame import Surface

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
posicaoPersonagemX = 500
posicaoPersonagemY = 535
velocidade = 4
velocidadeOriginal = 4
noChao = True
velocidadePulo = 0
gravidade = 0.9
forcaPulo = -17
frameAtual = 0
frameTimer = 0
viradoPraEsquerda = False

# Munição Coletável
imagemColetavel = pygame.image.load("recursos/imagens/coletaveis/municaoColetavel.png")
posicaoColetavelX = random.randint(200, 700)
posicaoColetavelYBase = 610
posicaoColetavelY = posicaoColetavelYBase
contadorAnimacaoColetavel = 0

# Speed Boost Coletável
imagemBoost = pygame.image.load("recursos/imagens/coletaveis/speedBoost.png")
boostVisivel = False
boostColetado = False
boostTempoUltimaColeta = 0
boostContadorAnimacao = 0
posicaoBoostX = random.randint(200, 700)
posicaoBoostY_base = 610
tempoInicioBoost = 0
boostDuracao = 8000
boostCooldown = 15000
boostAtivo = False
boostOverlay = pygame.Surface((1000, 700), pygame.SRCALPHA)

# Pontuação
pontuacao = 0
fonte = pygame.font.SysFont("Arial", 30)

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
            mouseX, mouseY = event.pos

            if not jogoIniciado and botaoStart.collidepoint(mouseX, mouseY):
                dadosEmThread(definirDadosJogador)

            if not jogoIniciado and botaoSair.collidepoint(mouseX, mouseY):
                rodando = False

    # Movimentos e animações do personagem principal
    teclas = pygame.key.get_pressed()
    andando = False

    if jogoIniciado:
        if teclas[pygame.K_a]:
            posicaoPersonagemX -= velocidade
            andando = True
            viradoPraEsquerda = True
        if teclas[pygame.K_d]:
            posicaoPersonagemX += velocidade
            andando = True
            viradoPraEsquerda = False
        if posicaoPersonagemX <= 200:
            posicaoPersonagemX = 200
        if posicaoPersonagemX >= 700:
            posicaoPersonagemX = 700
        if teclas[pygame.K_w] and noChao:
            velocidadePulo = forcaPulo
            noChao = False

    if not noChao:
        velocidadePulo += gravidade
        posicaoPersonagemY += velocidadePulo
        if posicaoPersonagemY >= 535:
            posicaoPersonagemY = 535
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

    tela.fill("#220202")

    # Tela do jogo com o personagem 
    if jogoIniciado:
        tela.blit(telaJogo, (0, 0))
        tela.blit(img, (posicaoPersonagemX, posicaoPersonagemY))

        # Animação e colisão - Coletável
        contadorAnimacaoColetavel += 0.1
        posicaoColetavelY = posicaoColetavelYBase + math.sin(contadorAnimacaoColetavel) * 8
        tela.blit(imagemColetavel, (posicaoColetavelX, posicaoColetavelY))

        hitboxPersonagem = pygame.Rect(posicaoPersonagemX, posicaoPersonagemY, img.get_width(), img.get_height())
        hitboxColetavel = pygame.Rect(posicaoColetavelX, posicaoColetavelY, imagemColetavel.get_width(), imagemColetavel.get_height())
        if hitboxPersonagem.colliderect(hitboxColetavel):
            pontuacao += 1
            while True:
                novoXColetavel = random.randint(200, 700)
                if abs(novoXColetavel - posicaoPersonagemX) > 200:
                    posicaoColetavelX = novoXColetavel
                    break

        # Aparecimento do boost
        tempoAtual = pygame.time.get_ticks()
        if not boostVisivel and not boostColetado:
            if random.randint(0, 1000) < 2:
                while True:
                    novoX = random.randint(200, 700)
                    if abs(novoX - posicaoColetavelX) > 80:  # distância mínima entre boost e munição
                        posicaoBoostX = novoX
                        break
                boostVisivel = True

        if boostColetado and tempoAtual - boostTempoUltimaColeta >= boostCooldown:
            boostColetado = False

        # Animação e colisão do boost
        if boostVisivel:
            boostContadorAnimacao += 0.1
            posicaoBoostY = posicaoBoostY_base + math.sin(boostContadorAnimacao) * 6
            tela.blit(imagemBoost, (posicaoBoostX, posicaoBoostY))

            hitboxBoost = pygame.Rect(posicaoBoostX, posicaoBoostY, imagemBoost.get_width(), imagemBoost.get_height())
            if hitboxPersonagem.colliderect(hitboxBoost):
                boostVisivel = False
                boostColetado = True
                boostTempoUltimaColeta = tempoAtual
                velocidade = 8
                boostAtivo = True
                tempoInicioBoost = tempoAtual

        if boostAtivo and tempoAtual - tempoInicioBoost >= boostDuracao:
            velocidade = velocidadeOriginal
            boostAtivo = False
            

        # Pontuação na tela
        textoPontos = fonte.render(f"Pontos: {pontuacao}", True, (255, 255, 255))
        tela.blit(textoPontos, (657, 5))
    else:
        tela.blit(telaInicial, (0, 0))

    # Efeito visual do boost
    if boostAtivo:
        tempoAtual = pygame.time.get_ticks()
        tempoPassado = tempoAtual - tempoInicioBoost

        if tempoPassado < boostDuracao:
            # Efeito normal azul claro
            if tempoPassado < boostDuracao - 1500:
                boostOverlay.fill((100, 100, 255, 40))  # Azul suave
                tela.blit(boostOverlay, (0, 0))
            else:
                # Piscando nos últimos 1.5s
                if (tempoAtual // 150) % 2 == 0:
                    boostOverlay.fill((100, 100, 255, 80))
                else:
                    boostOverlay.fill((100, 100, 255, 20))
                tela.blit(boostOverlay, (0, 0))
        else:
            velocidade = velocidadeOriginal
            boostAtivo = False

    pygame.display.flip()
    fps.tick(144)

pygame.quit()
