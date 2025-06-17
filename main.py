import pygame
import random
import math
from recursos.funcoes.funcionalidades import dadosEmThread
from recursos.funcoes.funcionalidades import configuracoesDificuldade

cortinaConcluida = False

escala = 1.0
direcao_pulso = 1  # 1 = crescendo, -1 = diminuindo
velocidade_pulso = 0.005  # quanto menor, mais rápido
escala_max = 1.1
escala_min = 0.9

tempoEntreInimigosMin = 1000
tempoEntreInimigosMax = 2000

vidas = 2
filtroVermelho = pygame.Surface((1000, 700), pygame.SRCALPHA)
filtroVermelho.fill((255, 0, 0, 80))
danoAtivo = False
tempoUltimoDano = 0
tempoDano = 5000  # 5 segundos
jogoCongelado = False
estadoCortina = "final"  # "fechando", "esperando", "abrindo", "final"
tempoCortinaFechada = 0
cortinaEsquerdaX = 0
cortinaDireitaX = 1000
velocidadeCortina = 20

def hitbox_personagem_precisa(x, y, sprite):
    largura = sprite.get_width()
    altura = sprite.get_height()

    margem_lateral = int(largura * 0.2)
    margem_superior = int(altura * 0.15)
    altura_hitbox = int(altura * 0.75)

    return pygame.Rect(
        x + margem_lateral,
        y + margem_superior,
        largura - 2 * margem_lateral,
        altura_hitbox
    )

# === FUNÇÃO DE DANO ===
def aplicar_dano(tempoAtual):
    global vidas, danoAtivo, tempoUltimoDano, boostAtivo, jogoCongelado
    global cortinaEsquerdaX, cortinaDireitaX, estadoCortina

    if vidas == 2:
        vidas = 1
        danoAtivo = True
        tempoUltimoDano = tempoAtual
        boostAtivo = False  # desativa boost azul
    elif vidas == 1:
        vidas = 0
        jogoCongelado = True
        cortinaEsquerdaX = 0
        cortinaDireitaX = 1000
        estadoCortina = "fechando"

# === FUNÇÃO DE CORTINA ===
def desenhar_cortina(tela):
    global cortinaEsquerdaX, cortinaDireitaX, estadoCortina, tempoCortinaFechada, jogoCongelado
    global cortinaConcluida

    if estadoCortina == "fechando":
        if cortinaEsquerdaX < 500:
            cortinaEsquerdaX += velocidadeCortina
            cortinaDireitaX -= velocidadeCortina
        else:
            estadoCortina = "esperando"
            tempoCortinaFechada = pygame.time.get_ticks()

    elif estadoCortina == "esperando":
        if pygame.time.get_ticks() - tempoCortinaFechada > 1000:
            estadoCortina = "abrindo"

    elif estadoCortina == "abrindo":
        if cortinaEsquerdaX > 0:
            cortinaEsquerdaX -= velocidadeCortina
            cortinaDireitaX += velocidadeCortina
        else:
            estadoCortina = "final"
            jogoCongelado = False  # libera a lógica se quiser reiniciar
            cortinaConcluida = True

    # Desenha as cortinas em qualquer estado
    pygame.draw.rect(tela, (0, 0, 0), (0, 0, cortinaEsquerdaX, 700))
    pygame.draw.rect(tela, (0, 0, 0), (cortinaDireitaX, 0, 1000 - cortinaDireitaX, 700))



# === CLASSES DE JOGO ===
class Bala:
    def __init__(self, x, y, destino, sprite_original):
        self.x = x
        self.y = y
        dx = destino[0] - x
        dy = destino[1] - y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
        self.vx = (dx / dist) * 10
        self.vy = (dy / dist) * 10
        self.ativa = True
        angle = math.degrees(math.atan2(-dy, dx))
        self.sprite = pygame.transform.rotate(sprite_original, angle)


    def atualizar(self):
        if self.ativa:
            self.x += self.vx
            self.y += self.vy
            if self.x < 0 or self.x > 1000 or self.y < 0 or self.y > 700:
                self.ativa = False

    def desenhar(self, tela):
        if self.ativa:
            pygame.draw.circle(tela, (255, 255, 0), (int(self.x), int(self.y)), 4)

class BalaImagem:
    def __init__(self, x, y, destino, sprite_original, flip=False):
        self.x = x
        self.y = y
        dx = destino[0] - x
        dy = destino[1] - y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
        self.vx = (dx / dist) * 12
        self.vy = (dy / dist) * 12
        self.ativa = True

        # Rotaciona a sprite da bala para apontar para o destino
        angle = math.degrees(math.atan2(-dy, dx))
        if flip:
            sprite_original = pygame.transform.flip(sprite_original, True, False)
            angle += 180

        self.sprite = pygame.transform.rotate(sprite_original, angle)

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > 1000 or self.y < 0 or self.y > 700:
            self.ativa = False

    def desenhar(self, tela):
        if self.ativa:
            tela.blit(self.sprite, (self.x, self.y))




class Inimigo:
    def __init__(self, pos_parado, pos_mirando, sprites):
        self.pos_parado = pos_parado
        self.pos_mirando = pos_mirando
        self.sprites = sprites
        self.estado = "aparecendo"
        self.tempo_estado = pygame.time.get_ticks()
        self.flash_visivel = False
        self.bala = None
        self.posicao = pos_parado


    def atualizar(self, tempo_atual, pos_personagem):
        if self.estado == "aparecendo":
            if tempo_atual - self.tempo_estado > 1000:
                self.estado = "mirando"
                self.tempo_estado = tempo_atual

        elif self.estado == "mirando":
            if tempo_atual - self.tempo_estado > 1000:
                self.estado = "atirando"
                self.tempo_estado = tempo_atual
                self.flash_visivel = True

                # Criar a bala no momento do disparo
                tipo = self.sprites.get("tipo")
                flip = self.sprites["flip"]

                if tipo == "baixo":
                    offset_x = 88 if not flip else 10
                    offset_y = 62
                elif tipo == "meio":
                    offset_x = 110 if not flip else 5
                    offset_y = 83
                else:  # topo
                    offset_x = 96 if not flip else 10
                    offset_y = 90

                x_saida = self.pos_mirando[0] + offset_x
                y_saida = self.pos_mirando[1] + offset_y

                largura_pers = personagemParado.get_width()
                altura_pers = personagemParado.get_height()
                destino = (pos_personagem[0] + largura_pers // 2, pos_personagem[1] + altura_pers // 2)

                sprite_bala = self.sprites["bala"]
                self.bala = BalaImagem(x_saida, y_saida, destino, sprite_bala, flip=self.sprites["flip"])

        elif self.estado == "atirando":
            if tempo_atual - self.tempo_estado > 100:
                self.flash_visivel = False
            if tempo_atual - self.tempo_estado > 1000:
                self.estado = "desaparecendo"
                self.tempo_estado = tempo_atual

        if self.bala:
            self.bala.atualizar()
        
    def desenhar(self, tela):
        if self.estado == "aparecendo":
            img = pygame.transform.flip(self.sprites["parado"], True, False) if self.sprites["flip"] else self.sprites["parado"]
            tela.blit(img, self.pos_parado)
        else:
            img = pygame.transform.flip(self.sprites["mirando"], True, False) if self.sprites["flip"] else self.sprites["mirando"]
            tela.blit(img, self.pos_mirando)

        if self.flash_visivel:
            tipo = self.sprites.get("tipo")
            flip = self.sprites["flip"]

            if tipo == "baixo":
                offset_x = 88 if not flip else 110
                offset_y = 62
            elif tipo == "meio":
                offset_x = 108 if not flip else 130
                offset_y = 81
            else:  # topo
                offset_x = 96 if not flip else 123
                offset_y = 90

            if flip:
                fx = self.pos_mirando[0] + self.sprites["mirando"].get_width() - offset_x
            else:
                fx = self.pos_mirando[0] + offset_x

            fy = self.pos_mirando[1] + offset_y

            tela.blit(self.sprites["flash"], (fx, fy))

        if self.bala:
            self.bala.desenhar(tela)



            
    def deve_destruir(self):
        return self.estado == "desaparecendo" and pygame.time.get_ticks() - self.tempo_estado > 200


    

        


# === INICIALIZAÇÃO ===
pygame.init()
tela = pygame.display.set_mode((1000, 700))
fps = pygame.time.Clock()
rodando = True

imagemCoracao = pygame.image.load("recursos/imagens/ui/coracao.png").convert_alpha()

telaInicial = pygame.image.load("recursos/imagens/telas/telaInicio.png")
telaJogo = pygame.image.load("recursos/imagens/telas/telaJogo.png")
telaMorte = pygame.image.load("recursos/imagens/telas/telaMorte.png")

botaoStart = pygame.Rect(412, 448, 185, 75, border_radius=10)
botaoSair = pygame.Rect(412, 550, 185, 75, border_radius=10)
botaoJogarDeNovo = pygame.Rect(400, 430, 200, 70)  # ajuste conforme a imagem
botaoSairMorte = pygame.Rect(400, 520, 200, 70)


jogoIniciado = False
nomeJogador = ""
dificuldade = ""

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

imagemColetavel = pygame.image.load("recursos/imagens/coletaveis/municaoColetavel.png")
posicaoColetavelX = random.randint(200, 700)
posicaoColetavelYBase = 610
posicaoColetavelY = posicaoColetavelYBase
contadorAnimacaoColetavel = 0

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

oponenteMirando1 = pygame.image.load("recursos/imagens/oponente/oponenteMirando1.png")
oponenteMirando2 = pygame.image.load("recursos/imagens/oponente/oponenteMirando2.png")
oponenteMirando3 = pygame.image.load("recursos/imagens/oponente/oponenteMirando3.png")
spriteParado = pygame.image.load("recursos/imagens/oponente/oponenteAparecendo.png")
spriteParadoFlip = pygame.transform.flip(spriteParado, True, False)



spriteFlash = pygame.image.load("recursos/imagens/oponente/oponenteFlash.png")
spriteBala = pygame.image.load("recursos/imagens/oponente/oponenteBala.png")

janelasEsquerda = [(42, 104), (45, 318), (63, 524)]
janelasDireita = [(823, 104), (820, 318), (830, 524)]

janelas = [
    {"pos_parado": (63, 524), "pos_mirando": (63, 524), "mirando": oponenteMirando1, "parado": spriteParado, "flip": False, "tipo": "baixo"},
    {"pos_parado": (45, 306), "pos_mirando": (45, 318), "mirando": oponenteMirando2, "parado": spriteParado, "flip": False, "tipo": "meio"},
    {"pos_parado": (42, 88),  "pos_mirando": (42, 104), "mirando": oponenteMirando3, "parado": spriteParado, "flip": False, "tipo": "topo"},

    {"pos_parado": (830, 524), "pos_mirando": (830, 524), "mirando": oponenteMirando1, "parado": spriteParado, "flip": True, "tipo": "baixo"},
    {"pos_parado": (820, 306), "pos_mirando": (820, 318), "mirando": oponenteMirando2, "parado": spriteParado, "flip": True, "tipo": "meio"},
    {"pos_parado": (823, 88),  "pos_mirando": (823, 104), "mirando": oponenteMirando3, "parado": spriteParado, "flip": True, "tipo": "topo"},
]


inimigos = []


pontuacao = 0
fonte = pygame.font.SysFont("Arial", 30)




def definirDadosJogador(nome, dif):
    global nomeJogador, dificuldade, jogoIniciado, tempoEntreInimigosMin, tempoEntreInimigosMax, tempoProximoInimigo
    nomeJogador = nome
    dificuldade = dif
    jogoIniciado = True
    tempoEntreInimigosMin, tempoEntreInimigosMax = configuracoesDificuldade(dificuldade)
    tempoProximoInimigo = pygame.time.get_ticks() + random.randint(tempoEntreInimigosMin, tempoEntreInimigosMax)


# === LOOP PRINCIPAL ===
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
    
        if cortinaConcluida and vidas == 0 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouseX, mouseY = event.pos
            if botaoJogarDeNovo.collidepoint(mouseX, mouseY):
                # Reinicia o jogo
                vidas = 2
                danoAtivo = False
                cortinaConcluida = False
                jogoCongelado = False
                estadoCortina = "final"
                inimigos.clear()
                pontuacao = 0
                posicaoPersonagemX = 500
                posicaoPersonagemY = 535
                boostVisivel = False
                boostColetado = False
                boostAtivo = False
                velocidade = velocidadeOriginal
                tempoProximoInimigo = pygame.time.get_ticks() + random.randint(tempoEntreInimigosMin, tempoEntreInimigosMax)

            elif botaoSairMorte.collidepoint(mouseX, mouseY):
                rodando = False

    teclas = pygame.key.get_pressed()
    andando = False
    tempoAtual = pygame.time.get_ticks()

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
    if jogoIniciado:
        tela.blit(telaJogo, (0, 0))
        tela.blit(img, (posicaoPersonagemX, posicaoPersonagemY))

       

          # === FILTRO VERMELHO E CORTINA ===
       

        # Criação de novos inimigos
        if tempoAtual >= tempoProximoInimigo and len(inimigos) < 6:
            janelas_disponiveis = [j for j in janelas if all(i.posicao != j["pos_parado"] for i in inimigos)]
            if janelas_disponiveis:
                janela = random.choice(janelas_disponiveis)
                sprites = {
                    "parado": janela["parado"],
                    "mirando": janela["mirando"],
                    "flash": spriteFlash,
                    "bala": spriteBala,
                    "flip": janela["flip"],
                    "tipo": janela["tipo"]
                }
                inimigos.append(Inimigo(janela["pos_parado"], janela["pos_mirando"], sprites))
            tempoProximoInimigo = tempoAtual + random.randint(tempoEntreInimigosMin, tempoEntreInimigosMax)

        # Atualização e desenho de todos os inimigos existentes (sempre roda)
        for inimigo in inimigos[:]:
            inimigo.atualizar(tempoAtual, (posicaoPersonagemX, posicaoPersonagemY))
            inimigo.desenhar(tela)

            if inimigo.bala and inimigo.bala.ativa:
                hitboxPers = hitbox_personagem_precisa(posicaoPersonagemX, posicaoPersonagemY, img)
                hitboxBala = pygame.Rect(inimigo.bala.x, inimigo.bala.y, 6, 6)
                if hitboxPers.colliderect(hitboxBala):
                    inimigo.bala.ativa = False
                    if not jogoCongelado:
                        aplicar_dano(tempoAtual)

            if inimigo.deve_destruir():
                inimigos.remove(inimigo)



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

        if not boostVisivel and not boostColetado:
            if random.randint(0, 1000) < 2:
                while True:
                    novoX = random.randint(200, 700)
                    distanciaDaMunição = math.hypot(novoX - posicaoColetavelX, 0)
                    distanciaDoPersonagem = math.hypot(novoX - posicaoPersonagemX, 0)
                    if distanciaDaMunição > 100 and distanciaDoPersonagem > 100:
                        posicaoBoostX = novoX
                        break
                boostVisivel = True

        if boostColetado and tempoAtual - boostTempoUltimaColeta >= boostCooldown:
            boostColetado = False

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

        textoPontos = fonte.render(f"Pontos: {pontuacao}", True, (255, 255, 255))
        tela.blit(textoPontos, (655, 40))
    else:
        tela.blit(telaInicial, (0, 0))

    if boostAtivo:
        tempoAtual = pygame.time.get_ticks()
        tempoPassado = tempoAtual - tempoInicioBoost
        if tempoPassado < boostDuracao:
            if tempoPassado < boostDuracao - 1500:
                boostOverlay.fill((100, 100, 255, 40))
                tela.blit(boostOverlay, (0, 0))
            else:
                if (tempoAtual // 150) % 2 == 0:
                    boostOverlay.fill((100, 100, 255, 80))
                else:
                    boostOverlay.fill((100, 100, 255, 20))
                tela.blit(boostOverlay, (0, 0))
        else:
            velocidade = velocidadeOriginal
            boostAtivo = False


    if danoAtivo and not jogoCongelado:
        tela.blit(filtroVermelho, (0, 0))
        if tempoAtual - tempoUltimoDano > tempoDano:
            danoAtivo = False
            if vidas == 1:
                vidas = 2

    if jogoCongelado:
                desenhar_cortina(tela)

    # === Coração pulsando ===
    if jogoIniciado and vidas > 0:
        # Acelera batimento se com 1 vida
        velocidadePulso = 0.015 if vidas == 1 else 0.005

        escala += direcao_pulso * velocidadePulso
        if escala >= escala_max:
            escala = escala_max
            direcao_pulso = -1
        elif escala <= escala_min:
            escala = escala_min
            direcao_pulso = 1

        largura = int(imagemCoracao.get_width() * escala)
        altura = int(imagemCoracao.get_height() * escala)
        coracaoEscalado = pygame.transform.smoothscale(imagemCoracao, (largura, altura))


        # Centralizado em (20, 20) com compensação de escala
        posX = 210 - (largura - imagemCoracao.get_width()) // 2
        posY = 10 - (altura - imagemCoracao.get_height()) // 2
        tela.blit(coracaoEscalado, (posX, posY))

        # Primeiro: fundo preto se a cortina estiver abrindo ou esperando
    if estadoCortina in ["esperando", "abrindo"]:
        tela.fill((0, 0, 0))

    # Segundo: desenha a cortina se estiver em transição
    if jogoCongelado or estadoCortina in ["fechando", "esperando", "abrindo"]:
        desenhar_cortina(tela)

    # Terceiro: só mostra a tela de morte quando a cortina terminou de abrir
    if cortinaConcluida and vidas == 0:
        tela.fill((0, 0, 0))
        tela.blit(telaMorte, (0, 0))
        pygame.draw.rect(tela, (255, 0, 0), botaoJogarDeNovo, 2)  # borda vermelha
        pygame.draw.rect(tela, (0, 255, 0), botaoSairMorte, 2)    # borda verde
        
    


    pygame.display.flip()
    fps.tick(144)

pygame.quit()