import sys
import pygame
import math
import random
from config import *
from matrizes import *
from utils import *

pygame.init()

LARGURA, ALTURA = 900, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Unstable Cannon")

jogo_pausado = True
mostrar_comandos = False
mostrar_tela_inicial = True
tela_game_over = False
jogo_acabou= False

PRETO = (20, 20, 20)
BRANCO = (255, 255, 255)
VERDE = "#806e58"

pygame.mixer.init()

pygame.mixer.music.load(caminho_recurso("music/musica_fundo_1.ogg"))
som_tiro_basico = pygame.mixer.Sound(caminho_recurso("sons/som_tiro_normal.wav"))
som_tiro_grande = pygame.mixer.Sound(caminho_recurso("sons/som_tiro_grande.wav"))
som_dano = pygame.mixer.Sound(caminho_recurso("sons/som_dano.wav"))

som_tiro_basico.set_volume(0.2)
som_tiro_grande.set_volume(0.2)
som_dano.set_volume(0.3)

pygame.mixer.music.set_volume(0.7)

pygame.mixer.music.play(-1)

fonte = pygame.font.SysFont(None, 20)
fonte_horda = pygame.font.SysFont(None, 30)
fonte_gigante = pygame.font.SysFont("Arial", 80, bold=True)
fonte_titulo = pygame.font.SysFont("arial", 28, bold=True)
fonte_texto = pygame.font.SysFont("arial", 20)


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

tempo_ultimo_coracao = 0
intervalo_coracao = 20000

class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, velocidade, gravidade, tipo="normal", cor="#32df0f"):
        super().__init__()

        self.tamanho_base_tiro = 10
        self.cor = cor
        self.tipo = tipo

        if self.tipo == "tiro_grande":
            alpha = 128
            self.dano = 1
        else:
            alpha = 255
            self.dano = 10
        self.imagem_original = pygame.Surface((self.tamanho_base_tiro, self.tamanho_base_tiro), pygame.SRCALPHA)
        
        self.imagem_original.fill(self.cor)
        self.imagem_original.set_alpha(alpha)

        self.image = self.imagem_original.copy()
        self.image.fill(self.cor)
        self.rect = self.image.get_rect(center=(x, y))

        angulo_radiano = math.radians(angulo)
        
        self.vel_x = math.cos(angulo_radiano) * velocidade
        self.vel_y = -math.sin(angulo_radiano) * velocidade

        self.gravidade = gravidade

        self.limite_escala = 20.0
        self.escala_atual = 1.0
        self.taxa_crescimento = 0.2
        
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if gravidade_tiro_ativa:
            self.vel_y += self.gravidade

        if self.tipo == "tiro_grande":
            if  self.escala_atual < self.limite_escala:
                self.escala_atual += self.taxa_crescimento

                nova_dimensao = int(self.tamanho_base_tiro * self.escala_atual)

                self.image = pygame.transform.scale(self.imagem_original, (nova_dimensao, nova_dimensao))

                self.rect = self.image.get_rect(center=self.rect.center)

                self.dano += self.taxa_crescimento * 0.5
                
        if self.rect.right < 0 or self.rect.left > LARGURA or self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, tipo="normal", pode_crescer=False):
        super().__init__()
        self.tipo = tipo

        self.vem_direcao = None
        self.dano = 5

        self.pode_crescer = pode_crescer
        self.escala_atual = 1.0
        self.limite_escala = random.choice([2.0, 2.5])
        self.taxa_crescimento = 0.005

        self.tamanho_base_triangulo = 50

        if self.tipo == "boss":
            self.largura = 100
            self.altura = 100
            self.imagem_original = pygame.Surface((100, 100))
            self.imagem_original.fill((255, 0, 0)) 
            self.velocidade = 1
            self.vida = 500
            
        elif self.tipo == "normal":
            self.largura = 30
            self.altura = 30
            self.imagem_original = pygame.Surface((30, 30))
            self.imagem_original.fill((0, 255, 0)) 
            self.velocidade = random.randint(1, 2)
            self.vida = 10
            self.pode_crescer = True
            
        elif self.tipo == "nave":
            self.largura = 50
            self.altura = 50
            self.imagem_original = pygame.Surface((50, 50), pygame.SRCALPHA)
            pontos = [(0, 0), (50, 0), (25, 50)]
            pygame.draw.polygon(self.imagem_original, "#1e43e7", pontos)
            self.velocidade = random.randint(1, 2)
            self.vida = 5

        self.image = self.imagem_original.copy()
        self.rect = self.image.get_rect()
        
        if self.tipo == "boss":
            self.rect.x = random.randint(0, 700)
            self.rect.y = -100
        elif self.tipo == "normal":
            self.rect.x = random.choice([-40, 920])
            if self.rect.x == -40:
                self.vem_direcao = "ESQUERDA"
            else:
                self.vem_direcao = "DIREITA"
            self.rect.y = ALTURA_CHAO - 30
        elif self.tipo == "nave":
            self.rect.x = random.randint(0, 900)
            self.rect.y = -40

    def update(self, jogador):
        if self.tipo == "boss":
            self.rect.y += self.velocidade
        elif self.tipo == "normal":
            if self.vem_direcao == "ESQUERDA":
                self.rect.x += self.velocidade 
            else:
                self.rect.x -= self.velocidade
        elif self.tipo == "nave":
            delta_x  = jogador.rect.x - self.rect.x
            delta_y = jogador.rect.y - self.rect.y

            distancia = math.sqrt(delta_x**2 + delta_y**2)

            if distancia == 0:
                return 0, 0

            if distancia <= self.velocidade:
                return delta_x, delta_y

            vetor_x = delta_x / distancia
            vetor_y = delta_y / distancia

            self.rect.x += vetor_x * self.velocidade
            self.rect.y  += vetor_y * self.velocidade
            
        if self.tipo == "normal" and random.random() < 0.005 and self.largura < 180: 
            self.largura += 30
            self.altura += 30
            
            self.image = pygame.transform.scale(self.imagem_original, (self.largura, self.altura))
            
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            
            self.vida += 5
            self.dano += 5
            nova_velocidade = 60 / self.largura
            self.velocidade = max(1.0, nova_velocidade)
            self.mudar_cor()
       
        elif self.tipo != "normal" and self.pode_crescer and self.escala_atual < self.limite_escala:
            self.escala_atual += self.taxa_crescimento

            nova_dimensao = int(self.tamanho_base_triangulo * self.escala_atual)


            self.image = pygame.transform.scale(self.imagem_original, (nova_dimensao, nova_dimensao))

            self.rect = self.image.get_rect(center=self.rect.center)

            self.dano += self.taxa_crescimento
            self.vida += 0.05
            self.vida = min(60, self.vida)

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
        self.jogador_girada_angulo = 2

        self.limite_angulo_maior = 180
        self.limite_angulo_menor = 0

        self.pode_ativar_super = False

        self.duracao_super = 10000
        self.meta_super = 30
        self.tempo_inicio_super = 0
        self.super_ativo = False
        self.abates_para_super = 0

        self.tipo_super = "LASER"
    def update(self):
        if self.super_ativo:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.tempo_inicio_super > self.duracao_super:
                self.super_ativo = False
                self.jogador_girada_angulo = 2
                self.limite_angulo_maior = 180
                self.limite_angulo_menor = 0


class ItemCura(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.image = criar_sprite_por_matriz(matriz_coracao)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.velocidade_queda = 2
        self.valor_cura = 25

    def update(self):
        self.rect.y += self.velocidade_queda
        if self.rect.y > ALTURA_CHAO:
            self.kill()

def verificar_criar_coracao(tempo_atual, tempo_ultimo_coracao, intervalo_entre_coracao, vida):
    if vida == 100:
        return tempo_atual
    elif tempo_atual - tempo_ultimo_coracao > intervalo_entre_coracao:
        x = random.randint(0, 860)
        y = -40
        coracao = ItemCura(x, y)
        grupo_coracao.add(coracao)
        tempo_ultimo_coracao = tempo_atual
        return tempo_ultimo_coracao
    return tempo_ultimo_coracao

grupo_tiros = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()
jogador = Jogador(int(LARGURA / 2), ALTURA_CHAO)
grupo_jogador = pygame.sprite.GroupSingle(jogador)
grupo_coracao = pygame.sprite.Group()

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

def calcular_horda(orcamento, horda, tipo_horda):
    fila_inimigos = []
    saldo = orcamento

    custo_inimigo_normal = 10
    custo_inimigo_nave = 50

    pode_crescer = False

    while saldo >= custo_inimigo_normal:
        if tipo_horda == "areo":
            escolha = "nave"
            custo_inimigo_nave = custo_inimigo_normal
        elif tipo_horda == "normal":
            if horda >= 3:
                escolha = random.choice(["normal", "nave"])
            else:
                escolha = "normal"

        if escolha == "normal":
            novo_inimigo = Inimigo(tipo="normal") 
            fila_inimigos.append(novo_inimigo)
            saldo -= custo_inimigo_normal
        elif escolha == "nave":
            if tipo_horda == "areo":
                if random.random() < chance_nave_crescer_areo:
                    pode_crescer = True
            else:
                if random.random() < chance_nave_crescer:
                    pode_crescer = True
            novo_inimigo = Inimigo(tipo="nave", pode_crescer=pode_crescer) 
            fila_inimigos.append(novo_inimigo)
            saldo -= custo_inimigo_nave
    return fila_inimigos

def calcular_orcamento_horda(horda):
  pontos_base = 50
  return pontos_base + (20 * (horda**1.3))

def disparar_texto_horda(nome):
    global mostrar_texto, tempo_inicio_texto, nome_horda_atual
    if nome == "areo":
        nome_horda_atual ="FLY"
    mostrar_texto = True
    tempo_inicio_texto = pygame.time.get_ticks()

def desenhar_texto_horda(tela, nome_horda_atual):
    global mostrar_texto
    
    if mostrar_texto:
        tempo_atual = pygame.time.get_ticks()
        
        if tempo_atual - tempo_inicio_texto < 3000:
            texto_surf = fonte_gigante.render(f"HORDA: {nome_horda_atual}!", True, "#faec28")
            
            texto_rect = texto_surf.get_rect(center=(450, 300))
            
            tela.blit(texto_surf, texto_rect)
        else:
            mostrar_texto = False

def desenhar_barra_progresso_super(superficie, x, y, largura, altura, atual, maximo, super_ativo, tempo_iniciado, tempo_atual, tempo_maximo=1500,cor_borda="#0e0d0d"):
    if maximo <= 0:
        maximo = 1

    cor_preenchimento = "#19E073"
    if atual >= maximo:
        cor_preenchimento = "#16e916"

    if super_ativo:
        tempo_decorrido = tempo_atual - tempo_iniciado
        tempo_restante = tempo_maximo - tempo_decorrido
        porcentagem = max(0, min(tempo_restante / tempo_maximo, 1.0))
        cor_preenchimento = "#c9e916"
    else:
        porcentagem = max(0, min(atual / maximo, 1.0))

    pygame.draw.rect(superficie, cor_borda, (x, y, largura, altura), 1)

    margem = 2  
    largura_interna_max = largura - (margem * 2)
    altura_interna = altura - (margem * 2)

    largura_atual = largura_interna_max * porcentagem

    if largura_atual > 0:
        pygame.draw.rect(superficie, cor_preenchimento, (x + margem, y + margem, largura_atual, altura_interna))

    terco = largura / 3
    
    y_inicio = y + 1
    y_fim = y + altura - 1

    x_terco_1 = int(x + terco)
    x_terco_2 = int(x + (terco * 2))

    pygame.draw.line(superficie, cor_borda, (x_terco_1, y_inicio), (x_terco_1, y_fim), 1)
    pygame.draw.line(superficie, cor_borda, (x_terco_2, y_inicio), (x_terco_2, y_fim), 1)

def desenhar_painel_comandos(superficie, largura=500, altura=400):
    tela_largura = superficie.get_width()
    tela_altura = superficie.get_height()
    
    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)

    painel = pygame.Surface((largura, altura), pygame.SRCALPHA)

    cor_fundo = (15, 15, 20, 210) 
    painel.fill(cor_fundo)
    
    cor_borda = (25, 224, 115) 
    pygame.draw.rect(painel, cor_borda, (0, 0, largura, altura), 3)

    txt_titulo = fonte_titulo.render("PAUSED - CONTROLS", True, (255, 255, 255))
    rect_titulo = txt_titulo.get_rect(center=(largura // 2, 35))
    painel.blit(txt_titulo, rect_titulo)
    
    pygame.draw.line(painel, cor_borda, (20, 60), (largura - 20, 60), 2)
    
    comandos = [
        "AD / Arrows : Move and Aim",
        "SPACE : Basic Shot",
        "Q : Big Shot",
        "E : Fire Super Laser",
        "P / ESC : Pause / Resume",
        "",
        "Press SPACE to Continue"
    ]
    
    pos_y = 90
    for linha in comandos:
        if linha == "Press SPACE to Continue":
            txt_linha = fonte_texto.render(linha, True, (255, 230, 0))
            rect_linha = txt_linha.get_rect(center=(largura // 2, altura - 40))
            painel.blit(txt_linha, rect_linha)
        else:
            txt_linha = fonte_texto.render(linha, True, (220, 220, 220))
            painel.blit(txt_linha, (30, pos_y))
            pos_y += 35
            
    superficie.blit(painel, (x, y))

def desenhar_tela_inicio(superficie, largura=500, altura=450): 
    tela_largura = superficie.get_width()
    tela_altura = superficie.get_height()
    
    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)

    painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
    cor_fundo = (15, 15, 20, 210) 
    painel.fill(cor_fundo)
    
    cor_borda = (25, 224, 115) 
    pygame.draw.rect(painel, cor_borda, (0, 0, largura, altura), 3)

    txt_titulo = fonte_titulo.render("WELCOME TO THE GAME", True, (255, 255, 255))
    rect_titulo = txt_titulo.get_rect(center=(largura // 2, 35))
    painel.blit(txt_titulo, rect_titulo)
    
    pygame.draw.line(painel, cor_borda, (20, 60), (largura - 20, 60), 2)

    regras = [
        "This is an infinite horde survival game.",
        "The difficulty increases over time.",
        "WARNING: Do not let the enemies reach the tank!"
    ]
    
    pos_y = 80
    for regra in regras:
        if "WARNING" in regra:
            txt_regra = fonte_texto.render(regra, True, (255, 100, 100)) 
        else:
            txt_regra = fonte_texto.render(regra, True, (200, 200, 255))
            
        rect_regra = txt_regra.get_rect(center=(largura // 2, pos_y))
        painel.blit(txt_regra, rect_regra)
        pos_y += 35
        
    pygame.draw.line(painel, cor_borda, (100, pos_y + 10), (largura - 100, pos_y + 10), 1)
    
    pos_y += 35 
    comandos = [
        "AD / Arrows : Move and Aim",
        "SPACE : Basic Shot",
        "Q : Big Shot", 
        "E : Fire Super Laser",
        "P / ESC : Pause / Resume",
        "",
        "Press SPACE to Start"      
    ]
    
    for linha in comandos:
        if linha == "Press SPACE to Start":
            txt_linha = fonte_texto.render(linha, True, (255, 230, 0))
            rect_linha = txt_linha.get_rect(center=(largura // 2, altura - 40))
            painel.blit(txt_linha, rect_linha)
        elif linha == "CONTROLS:":
            txt_linha = fonte_texto.render(linha, True, (255, 255, 255))
            painel.blit(txt_linha, (50, pos_y))
            pos_y += 35
        else:
            txt_linha = fonte_texto.render(linha, True, (220, 220, 220))
            painel.blit(txt_linha, (50, pos_y))
            pos_y += 35
            
    superficie.blit(painel, (x, y))

def desenhar_tela_game_over(superficie, largura=500, altura=300):
    tela_largura = superficie.get_width()
    tela_altura = superficie.get_height()
    
    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)

    painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
    cor_fundo = (15, 15, 20, 210) 
    painel.fill(cor_fundo)
    
    cor_borda = (255, 50, 50) 
    pygame.draw.rect(painel, cor_borda, (0, 0, largura, altura), 3)

    txt_titulo = fonte_titulo.render("GAME OVER", True, (255, 50, 50))
    rect_titulo = txt_titulo.get_rect(center=(largura // 2, 45))
    painel.blit(txt_titulo, rect_titulo)
    
    pygame.draw.line(painel, cor_borda, (20, 80), (largura - 20, 80), 2)

    txt_motivo = fonte_texto.render("The tank was destroyed!", True, (220, 220, 220))
    rect_motivo = txt_motivo.get_rect(center=(largura // 2, altura // 2))
    painel.blit(txt_motivo, rect_motivo)
    
    txt_reiniciar = fonte_texto.render("Press SPACE to Restart", True, (255, 230, 0))
    rect_reiniciar = txt_reiniciar.get_rect(center=(largura // 2, altura - 40))
    painel.blit(txt_reiniciar, rect_reiniciar)
    
    superficie.blit(painel, (x, y))

barra_x_super = jogador.rect.centerx - (largura_barra_super // 2)
barra_y_super = jogador.rect.bottom + 10

numero_horda = 1
orcamento_atual = calcular_orcamento_horda(numero_horda)
fila_espera = calcular_horda(orcamento_atual, numero_horda, "normal")

intervalo_spawn = 2000
ultimo_spawn = 0
limite_inimigo_tela = 10

horda_ativa = True

tipo_horda_atual = "normal"
lista_tipo_hordas = ["normal", "areo"]

tempo_inicio_texto = 0
nome_horda_atual = ""
mostrar_texto = False

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if jogo_pausado is False:
                if evento.key == pygame.K_SPACE:
                    if jogador.tipo_super != "LASER" or jogador.super_ativo is False:
                        angulo_radiano = math.radians(angulo)
                        
                        ponta_x = canhao_x + altura_cano * math.cos(angulo_radiano)
                        ponta_y = canhao_y - altura_cano * math.sin(angulo_radiano)
                        novo_tiro = Tiro(ponta_x, ponta_y, angulo, velocidade_tiro, gravidade_tiro)
                        grupo_tiros.add(novo_tiro)
                        som_tiro_basico.play()
                elif evento.key == pygame.K_e:
                    if jogador.pode_ativar_super:
                        jogador.super_ativo = True
                        jogador.pode_ativar_super = False
                        jogador.tempo_inicio_super = tempo_atual
                        jogador.abates_para_super = 0
                        if jogador.tipo_super == "LASER":
                            jogador.jogador_girada_angulo = 1
                elif evento.key == pygame.K_q:
                    print(jogador.abates_para_super)
                    if jogador.abates_para_super >= 10 and jogador.super_ativo is False:
                        angulo_radiano = math.radians(angulo)
                        jogador.abates_para_super -= 10
                                            
                        ponta_x = canhao_x + altura_cano * math.cos(angulo_radiano)
                        ponta_y = canhao_y - altura_cano * math.sin(angulo_radiano)
                        novo_tiro = Tiro(ponta_x, ponta_y, angulo, 2, gravidade_tiro, tipo="tiro_grande", cor="#ffffff")
                        grupo_tiros.add(novo_tiro)
                        som_tiro_grande.play()
                elif evento.key == pygame.K_ESCAPE:
                    jogo_pausado = True
                    mostrar_comandos = True
            else:
                if evento.key == pygame.K_SPACE:
                    if mostrar_tela_inicial:
                        mostrar_tela_inicial = False
                        jogo_pausado = False
                    elif jogo_acabou:
                        jogo_acabou = False
                        jogo_pausado = False
                        jogador = Jogador(int(LARGURA / 2), ALTURA_CHAO)
                        grupo_jogador.empty()
                        grupo_inimigos.empty()
                        grupo_tiros.empty()
                        grupo_jogador = pygame.sprite.GroupSingle(jogador)
                        grupo_coracao.empty()
                        tipo_horda_atual = "normal"
                        numero_horda = 1
                    elif mostrar_comandos:
                        jogo_pausado = False
                        mostrar_comandos = False


        tempo_atual = pygame.time.get_ticks()
    TELA.fill(PRETO)
    if jogo_acabou is False:
        if jogador.vida <= 0:
            jogo_pausado= True
            jogo_acabou = True
    if jogo_pausado is False:
        if len(fila_espera) > 0 and len(grupo_inimigos) < limite_inimigo_tela: 
            if tempo_atual - ultimo_spawn > intervalo_spawn:
                
                proximo_inimigo = fila_espera.pop(0)
                grupo_inimigos.add(proximo_inimigo)
                
                ultimo_spawn = tempo_atual

        if len(fila_espera) == 0 and len(grupo_inimigos) == 0:
            numero_horda += 1

            if numero_horda % 5 == 0:
                tipo_horda_atual = random.choice(lista_tipo_hordas)
                # tipo_horda_atual = "areo"
                limite_inimigo_tela = random.randint(11, 15)
                if tipo_horda_atual != "normal":
                    disparar_texto_horda(tipo_horda_atual)
            else:
                tipo_horda_atual = "normal"
                limite_inimigo_tela = 10
        
            novo_orcamento = calcular_orcamento_horda(numero_horda)
            fila_espera = calcular_horda(novo_orcamento, numero_horda, tipo_horda_atual)
            if numero_horda % 5 == 0:
                intervalo_spawn = random.randint(200, 350)
            else:
                intervalo_spawn = max(400, int(intervalo_spawn * 0.9))

    
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            angulo += jogador.jogador_girada_angulo
            angulo = max(0, min(angulo, 180))
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            angulo -= jogador.jogador_girada_angulo
            angulo = max(0, min(angulo, 180))

        tempo_ultimo_coracao = verificar_criar_coracao(tempo_atual, tempo_ultimo_coracao, intervalo_coracao, jogador.vida)

        if jogador.super_ativo:
            if jogador.tipo_super == "LASER":
                angulo_radiano = math.radians(angulo)
        
                origem_x = canhao_x + altura_cano * math.cos(angulo_radiano)
                origem_y = canhao_y - altura_cano * math.sin(angulo_radiano)
                         
                    
                comprimento_laser = 500
                        
                fim_x = origem_x + comprimento_laser * math.cos(angulo_radiano)
                fim_y = origem_y - comprimento_laser * math.sin(angulo_radiano)
                        
                espessura_laser = 8
                pygame.draw.line(TELA, "#e94747", (origem_x, origem_y), (fim_x, fim_y), espessura_laser)
                    
                for inimigo in grupo_inimigos:
                    if inimigo.rect.clipline((origem_x, origem_y), (fim_x, fim_y)):
                        inimigo.vida -= 5 
                        if inimigo.vida <= 0:
                            inimigo.kill()
        
                for coracao in grupo_coracao:
                    if coracao.rect.clipline((origem_x, origem_y), (fim_x, fim_y)):
                        jogador.vida += coracao.valor_cura
                        coracao.kill()
                        if jogador.vida >= 100:
                            jogador.vida = 100

    canhao_x = jogador.rect.centerx
    canhao_y = jogador.rect.centery - 5
    cano_rotacionado = pygame.transform.rotate(cano_surf, angulo - 90)
    cano_rect = cano_rotacionado.get_rect()
            
    cano_rect.center = (canhao_x, canhao_y)

    pygame.draw.rect(TELA, BRANCO, (0, ALTURA_CHAO, LARGURA, ALTURA - ALTURA_CHAO))
    mostrar_barra_vida_jogador(TELA, fonte, vida_jogador, jogador.vida)
    mostrar_horda(TELA, fonte_horda, numero_horda)

    grupo_jogador.draw(TELA)
    if jogo_pausado is False:
        grupo_jogador.update()
        grupo_tiros.update()
        grupo_coracao.update()
        grupo_inimigos.update(jogador)
    
    TELA.blit(cano_rotacionado, cano_rect)
    grupo_tiros.draw(TELA)

    grupo_coracao.draw(TELA)

    grupo_inimigos.draw(TELA)

    desenhar_barra_progresso_super(
    TELA, 
    barra_x_super, 
    barra_y_super, 
    largura_barra_super, 
    altura_barra_super, 
    jogador.abates_para_super, 
    jogador.meta_super,
    jogador.super_ativo,
    jogador.tempo_inicio_super,
    tempo_atual,
    jogador.duracao_super
    )

    colisoes_tiro_inimigo = pygame.sprite.groupcollide(grupo_tiros, grupo_inimigos, False, False)
    colisoes_inimigo_jogador = pygame.sprite.groupcollide(grupo_jogador, grupo_inimigos, False, False)

    if len(grupo_coracao) >= 1:
        colisoes_tiro_coracao = pygame.sprite.groupcollide(grupo_tiros, grupo_coracao, False, False)
        for tiro, lista_coracao_atingido in colisoes_tiro_coracao.items():
                for coracao in lista_coracao_atingido:
                    jogador.vida += coracao.valor_cura
                    coracao.kill()

                    if tiro.tipo != "tiro_grande":
                        tiro.kill()

                    if jogador.vida >= 100:
                        jogador.vida = 100


    for tiro, lista_inimigos_atingidos in colisoes_tiro_inimigo.items():
        for inimigo in lista_inimigos_atingidos:
            inimigo.vida -= tiro.dano
            som_dano.play()

            if inimigo.vida <= 0:
                inimigo.kill()

                if jogador.super_ativo is False and tiro.tipo != "tiro_grande":
                    jogador.abates_para_super += 1

                    if jogador.abates_para_super >= jogador.meta_super:
                        jogador.pode_ativar_super = True
            if tiro.tipo != "tiro_grande":
                tiro.kill()
                
    for jogador, lista_inimigos_atancando in colisoes_inimigo_jogador.items():
        for inimigo in lista_inimigos_atancando:
            jogador.vida -= inimigo.dano
            som_dano.set_volume(1.0)
            som_dano.play()
            som_dano.set_volume(0.3)
            inimigo.kill()

    desenhar_texto_horda(TELA, nome_horda_atual)

    if mostrar_comandos:
        desenhar_painel_comandos(TELA)
    elif mostrar_tela_inicial:
        desenhar_tela_inicio(TELA)
    elif jogo_acabou:
        desenhar_tela_game_over(TELA)

    pygame.display.flip()
    relogio.tick(60)