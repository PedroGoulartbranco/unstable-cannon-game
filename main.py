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

largura_cano, altura_cano = 10, 40
cano_surf = pygame.Surface((largura_cano, altura_cano), pygame.SRCALPHA)
cano_surf.fill(VERDE)

lista_tiros = []

rodando = True
while rodando:
  # 1. Tratamento de Eventos
  for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    if evento.type == pygame.KEYDOWN:
      if evento.key == pygame.K_SPACE:
        angulo_radiano = math.radians(angulo)

        velocidade_tiro = 15

        vel_x = velocidade_tiro * math.cos(angulo_radiano)
        vel_y = -velocidade_tiro * math.sin(angulo_radiano)

        ponta_cano_x = canhao_x + largura_cano * math.cos(angulo_radiano)
        ponta_cano_y = canhao_y - altura_cano * math.sin(angulo_radiano)

        # 3. Cria o tiro na ponta do cano em vez de na base (canhao_x, canhao_y)
        lista_tiros.append([ponta_cano_x, ponta_cano_y, vel_x, vel_y])

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

  for tiro in lista_tiros:
    tiro[0] += tiro[2]  # x += vel_x
    tiro[1] += tiro[3]  # y += vel_y

    tiro[3] += 0.4  

    pygame.draw.circle(TELA, BRANCO, (int(tiro[0]), int(tiro[1])), 4)

  pygame.display.flip()
  relogio.tick(60)