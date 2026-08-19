import sys
import pygame
import math
import random

pygame.init()

LARGURA, ALTURA = 900, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Canhão vs Alvo - Teste de Trigonometria")

PRETO = (20, 20, 20)
BRANCO = (255, 255, 255)
VERDE = (50, 200, 100)

# Relógio para controlar o FPS
relogio = pygame.time.Clock()

canhao_x, canhao_y = int(LARGURA / 2), 550.0
angulo = 90  

velocidade_tiro = 12
gravidade_tiro = 0.4

largura_cano, altura_cano = 10, 40
cano_surf = pygame.Surface((largura_cano, altura_cano), pygame.SRCALPHA)
cano_surf.fill(VERDE)

lista_tiros = []

rodando = True

vida_jogador = 100

y_chao = 570

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

        self.dano = 15
        
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        self.vel_y += self.gravidade
        
        if not pygame.Rect(0, 0, 800, 600).contains(self.rect):
            self.kill()

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, tipo="normal"):
        super().__init__()
        self.tipo = tipo

        self.vem_direcao = None

        if self.tipo == "boss":
            self.image = pygame.Surface((100, 100))
            self.image.fill((255, 0, 0)) # Boss é vermelho
            self.velocidade = 1
            self.vida = 500
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill((0, 255, 0))
            self.velocidade = random.randint(2, 4)
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
            self.rect.y = 570

    def update(self):
        # Movimentação
        if self.tipo == "boss":
            self.rect.y += self.velocidade
        else:
            if self.vem_direcao == "ESQUERDA":
                self.rect.x += self.velocidade 
            else:
                self.rect.x -= self.velocidade 
            
        if self.tipo != "boss" and random.random() < 0.005: 
            self.image = pygame.transform.scale(self.image, (60, 60))
            self.rect = self.image.get_rect(center=self.rect.center)
            self.vida += 2
            print("O quadrado ficou instável!")

grupo_tiros = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()

while rodando:
    # 1. Tratamento de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                angulo_radiano = math.radians(angulo)

                novo_tiro = Tiro(canhao_x, canhao_y, angulo, velocidade_tiro, gravidade_tiro)
                grupo_tiros.add(novo_tiro)

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        if angulo < 142:
            angulo += 2
    if teclas[pygame.K_RIGHT]:
        if angulo > 38:
            angulo -= 2

    print(angulo)

    cano_rotacionado = pygame.transform.rotate(cano_surf, angulo - 90)

    cano_rect = cano_rotacionado.get_rect()

    cano_rect.midbottom = (canhao_x, canhao_y)

    TELA.fill(PRETO)

    # Desenha o chão
    pygame.draw.rect(TELA, BRANCO, (0, 570, LARGURA, 30))

    pygame.draw.circle(TELA, VERDE, (int(canhao_x), int(canhao_y)), 20)

    TELA.blit(cano_rotacionado, cano_rect)

    grupo_tiros.update()
    grupo_tiros.draw(TELA)

    if random.randint(1, 100) == 1: # A cada 100 frames, spawna um inimigo
        novo_inimigo = Inimigo(tipo="normal")
        grupo_inimigos.add(novo_inimigo)

    grupo_inimigos.update()
    grupo_inimigos.draw(TELA)

    pygame.display.flip()
    relogio.tick(60)