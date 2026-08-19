import sys
import pygame
import math
# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA, ALTURA = 900, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Canhão vs Alvo - Teste de Trigonometria")

# Cores (RGB)
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
        
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        self.vel_y += self.gravidade
        
        if not pygame.Rect(0, 0, 800, 600).contains(self.rect):
            self.kill()

grupo_tiros = pygame.sprite.Group()

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
        angulo += 2
    if teclas[pygame.K_RIGHT]:
        angulo -= 2

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

    pygame.display.flip()
    relogio.tick(60)