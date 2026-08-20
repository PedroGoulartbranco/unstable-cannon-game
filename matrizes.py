import pygame
TRANSPARENTE = (0, 0, 0, 0)
VERMELHO = (255, 0, 0)
ROSA = (255, 105, 180)


_ = TRANSPARENTE
V = VERMELHO
R = ROSA

matriz_coracao = [
    [_, V, V, _, V, V, _],
    [V, R, V, V, V, V, V],
    [V, V, V, V, V, V, V],
    [_, V, V, V, V, V, _],
    [_, _, V, V, V, _, _],
    [_, _, _, V, _, _, _]
]

def criar_sprite_por_matriz(matriz, tamanho_pixel=4):
    linhas = len(matriz)
    colunas = len(matriz[0])
    
    largura = colunas * tamanho_pixel
    altura = linhas * tamanho_pixel
    superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)

    for y, linha in enumerate(matriz):
        for x, cor in enumerate(linha):
            if cor != TRANSPARENTE:
                retangulo_pixel = pygame.Rect(x * tamanho_pixel, y * tamanho_pixel, tamanho_pixel, tamanho_pixel)
                pygame.draw.rect(superficie, cor, retangulo_pixel)
                
    return superficie