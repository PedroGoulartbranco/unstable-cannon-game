import sys
import pygame
import math
import random
from config import *

pygame.init()

LARGURA, ALTURA = 900, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Canhão")

PRETO = (20, 20, 20)
BRANCO = (255, 255, 255)
VERDE = "#806e58"

fonte = pygame.font.SysFont(None, 20)
fonte_horda = pygame.font.SysFont(None, 30)
# Relógio para controlar o FPS
relogio = pygame.time.Clock()

angulo = 90  

velocidade_tiro = 12
gravidade_tiro = 0.4

largura_cano, altura_cano = 10, 55
cano_surf = pygame.Surface((largura_cano, altura_cano * 2), pygame.SRCALPHA)
pygame.draw.rect(cano_surf, VERDE, (0, 0, largura_cano, altura_cano))

lista_tiros = []

rodando = True
gravidade_tiro_ativa = False

vida_jogador = 100

numero_horda = 1
inimigos_derrotados_na_horda = 0
inimigos_proxima_horda = 10
intervalo_spawn = 2000
ultimo_spawn = 0
horda_ativa = True
limite_inimigo_tela = 10


class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, velocidade, gravidade):
        super().__init__()

        self.image = pygame.Surface((10, 10))
        self.image.fill("#32df0f")
        self.rect = self.image.get_rect(center=(x, y))

        angulo_radiano = math.radians(angulo)
        
        self.vel_x = math.cos(angulo_radiano) * velocidade
        self.vel_y = -math.sin(angulo_radiano) * velocidade

        self.gravidade = gravidade

        self.dano = 10
        
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if gravidade_tiro_ativa:
            self.vel_y += self.gravidade
        
        if self.rect.right < 0 or self.rect.left > LARGURA or self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, tipo="normal"):
        super().__init__()
        self.tipo = tipo

        self.vem_direcao = None
        self.largura = 30
        self.altura = 30

        self.dano = 5

        if self.tipo == "boss":
            self.largura = 100
            self.altura = 100
            self.image = pygame.Surface((100, 100))
            self.image.fill((255, 0, 0)) # Boss é vermelho
            self.velocidade = 1
            self.vida = 500
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill((0, 255, 0))
            self.velocidade = random.randint(1, 2)
            self.vida = 10
            
        self.rect = self.image.get_rect()
        
        if self.tipo == "boss":
            self.rect.x = random.randint(0, 700)
            self.rect.y = -100
        else:
            self.rect.x = random.choice([-40, 920])
            if self.rect.x ==  -40:
                self.vem_direcao = "ESQUERDA"
            else:
                self.vem_direcao = "DIREITA"
            self.rect.y = ALTURA_CHAO - 30

    def update(self):
        if self.tipo == "boss":
            self.rect.y += self.velocidade
        else:
            if self.vem_direcao == "ESQUERDA":
                self.rect.x += self.velocidade 
            else:
                self.rect.x -= self.velocidade 
            
        if self.tipo != "boss" and random.random() < 0.005 and self.largura < 180: 
            self.largura += 30
            self.altura += 30
            self.image = pygame.transform.scale(self.image, (self.largura, self.altura))
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.vida += 5
            self.dano += 5
            nova_velocidade = 60 / self.largura
            self.velocidade = max(1.0, nova_velocidade)
            self.mudar_cor()
    def mudar_cor(self):
        self.image.fill(dicionario_cor_inimigos[self.largura])

class Jogador(pygame.sprite.Sprite):
    def __init__(self, posicao_x, posicao_y):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA) 
        
        pygame.draw.circle(self.image, "#806e58", (30, 30), 30) 
        
        self.rect = self.image.get_rect()
        
        self.rect.centerx = posicao_x
        self.rect.centery = posicao_y
        self.vida = 100

grupo_tiros = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()
jogador = Jogador(int(LARGURA / 2), ALTURA_CHAO)
grupo_jogador = pygame.sprite.GroupSingle(jogador)

canhao_x = jogador.rect.centerx
canhao_y = jogador.rect.centery - 10

def mostrar_barra_vida_jogador(tela, fonte, vida_total, vida_atual):
    largura_tela = tela.get_width()
    fator_escala = largura_tela / 960

    largura_total_barra = int(500 * fator_escala)
    altura_barra = int(25 * fator_escala) 
    
    pos_x = (largura_tela // 2) - (largura_total_barra // 2)
    pos_y = int(20 * fator_escala)  

    vida_segura = max(0, min(vida_atual, vida_total))
    largura_atual_barra = int((vida_segura / vida_total) * largura_total_barra)

    rect_barra_fundo = pygame.Rect(pos_x, pos_y, largura_total_barra, altura_barra)
    rect_barra_frente = pygame.Rect(pos_x, pos_y, largura_atual_barra, altura_barra)

    pygame.draw.rect(tela, (60, 60, 60), rect_barra_fundo)   
    pygame.draw.rect(tela, (50, 200, 50), rect_barra_frente) 
    pygame.draw.rect(tela, (255, 255, 255), rect_barra_fundo, int(2 * fator_escala))

    texto_vida = f"{int(vida_segura)} / {int(vida_total)}"
    
    surf_texto = fonte.render(texto_vida, True, (255, 255, 255))
    
    rect_texto = surf_texto.get_rect(center=rect_barra_fundo.center)
    
    tela.blit(surf_texto, rect_texto)

def mostrar_horda(tela, fonte, numero_horda):
    largura_tela = tela.get_width()
    fator_escala = largura_tela / 960


    texto_horda = f"HORDA: {numero_horda}"
    
    surf_texto = fonte.render(texto_horda, True, (255, 255, 255))
    
    rect_texto = surf_texto.get_rect()
   
    rect_texto.right = largura_tela - int(30 * fator_escala)
    rect_texto.top = int(20 * fator_escala)
    
    tela.blit(surf_texto, rect_texto)

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                angulo_radiano = math.radians(angulo)
                
                ponta_x = canhao_x + altura_cano * math.cos(angulo_radiano)
                ponta_y = canhao_y - altura_cano * math.sin(angulo_radiano)
                novo_tiro = Tiro(ponta_x, ponta_y, angulo, velocidade_tiro, gravidade_tiro)
                grupo_tiros.add(novo_tiro)

    tempo_atual = pygame.time.get_ticks()

    if horda_ativa and len(grupo_inimigos) < limite_inimigo_tela: 
        if tempo_atual - ultimo_spawn > intervalo_spawn:
            novo_inimigo = Inimigo(tipo="normal") 
            grupo_inimigos.add(novo_inimigo)
            ultimo_spawn = tempo_atual

    if inimigos_derrotados_na_horda >= inimigos_proxima_horda:
        numero_horda += 1
        inimigos_derrotados_na_horda = 0
        inimigos_derrotados_na_horda = 0

        inimigos_proxima_horda = int(inimigos_proxima_horda * 1.4) 

        intervalo_spawn = max(400, int(intervalo_spawn * 0.9))

        if numero_horda % 5:
            limite_inimigo_tela = random.randint(11, 17)
        else:
            limite_inimigo_tela = 10

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
            if angulo < 180:
                angulo += 2
    if teclas[pygame.K_RIGHT]:
        if angulo > 0:
                angulo -= 2
    print(angulo)

    canhao_x = jogador.rect.centerx
    canhao_y = jogador.rect.centery - 5
    cano_rotacionado = pygame.transform.rotate(cano_surf, angulo - 90)
    cano_rect = cano_rotacionado.get_rect()
    
    cano_rect.center = (canhao_x, canhao_y)

    TELA.fill(PRETO)

    pygame.draw.rect(TELA, BRANCO, (0, ALTURA_CHAO, LARGURA, ALTURA - ALTURA_CHAO))
    mostrar_barra_vida_jogador(TELA, fonte, vida_jogador, jogador.vida)
    mostrar_horda(TELA, fonte_horda, numero_horda)

    grupo_jogador.draw(TELA)
    
    TELA.blit(cano_rotacionado, cano_rect)

    TELA.blit(cano_rotacionado, cano_rect)

    grupo_tiros.update()
    grupo_tiros.draw(TELA)

    grupo_inimigos.update()
    grupo_inimigos.draw(TELA)

    colisoes_tiro_inimigo = pygame.sprite.groupcollide(grupo_tiros, grupo_inimigos, True, False)
    colisoes_inimigo_jogador = pygame.sprite.groupcollide(grupo_jogador, grupo_inimigos, False, False)

    for tiro, lista_inimigos_atingidos in colisoes_tiro_inimigo.items():
        for inimigo in lista_inimigos_atingidos:
            inimigo.vida -= tiro.dano

            if inimigo.vida <= 0:
                inimigos_derrotados_na_horda += 1
                inimigo.kill()
    for jogador, lista_inimigos_atancando in colisoes_inimigo_jogador.items():
        for inimigo in lista_inimigos_atancando:
            jogador.vida -= inimigo.dano
            inimigo.kill()

    pygame.display.flip()
    relogio.tick(60)