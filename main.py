import pygame
import random
import os
import tkinter as tk
from tkinter import messagebox
# from recursos.funcoes import inicializarBancoDeDados
# from recursos.funcoes import escreverDados
import json

pygame.init()
tela = pygame.display.set_mode((1000, 700))
fps = pygame.time.Clock()
rodando = True

telaInicial = pygame.image.load("recursos/imagens/telas/telaInicio.png")

botaoStart = pygame.Rect(412, 448, 185, 75, border_radius=10) 
botaoSair = pygame.Rect(412, 550, 185, 75, border_radius=10)


while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

      
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            
            if botaoStart.collidepoint(mouse_x, mouse_y):
                print("Iniciar!")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
           
            if botaoSair.collidepoint(mouse_x, mouse_y):
                print("Sair!")

    tela.fill("#29157E")
    tela.blit(telaInicial, (0, 0))
    
       
    pygame.display.flip()
    fps.tick(144)

pygame.quit()