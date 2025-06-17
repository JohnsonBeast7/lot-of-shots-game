import tkinter as tk
from tkinter import messagebox, simpledialog
import threading

# Centralização da janela
def centralizarJanela(janela, largura, altura, tela_width=1000, tela_height=700):
    x = (tela_width // 2) - (largura // 2)
    y = (tela_height // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")


# Armazenamento do nome e dificuldade
def obterNomeEDificuldade():
    nomeJogador = ""
    dificuldade = ""

    while True:
        root_nome = tk.Tk()
        root_nome.withdraw()
        nomeJogador = simpledialog.askstring("Nome", "Digite seu nome:", parent=root_nome)
        root_nome.destroy()
        if nomeJogador and nomeJogador.strip():
            break
        else:
            aviso = tk.Tk()
            aviso.withdraw()
            messagebox.showwarning("Atenção", "Digite um nome para jogar!", parent=aviso)
            aviso.destroy()

    while True:
        root_dif = tk.Tk()
        root_dif.title("Dificuldade")
        root_dif.resizable(False, False)
        centralizarJanela(root_dif, 250, 160)

        tk.Label(root_dif, text=f"Bem-vindo, {nomeJogador}").pack(pady=(10, 5))
        dif = tk.StringVar(value="")

        for nivel in ["Normal", "Difícil", "Insano"]:
            tk.Radiobutton(root_dif, text=nivel, variable=dif, value=nivel).pack(anchor=tk.W, padx=20)

        def confirmar():
            if dif.get():
                root_dif.quit()
            else:
                aviso = tk.Tk()
                aviso.withdraw()
                messagebox.showwarning("Atenção", "Escolha uma dificuldade!", parent=aviso)
                aviso.destroy()

        tk.Button(root_dif, text="Confirmar", command=confirmar).pack(pady=10)
        root_dif.mainloop()

        if dif.get():
            dificuldade = dif.get()
            root_dif.destroy()
            break
        root_dif.destroy()

    return nomeJogador, dificuldade

def dadosEmThread(callback_definir_dados):
    def executar():
        nome, dificuldade = obterNomeEDificuldade()
        callback_definir_dados(nome, dificuldade)
    threading.Thread(target=executar).start()

# Configurações das dificuldades
# recursos/funcoes/funcionalidades.py

def configuracoesDificuldade(dificuldade):
    if dificuldade == "Normal":
        return 2000, 4000
    elif dificuldade == "Dificil":
        return 1000, 2000
    elif dificuldade == "Insano":
        return 500, 1000
    else:
        return 1500, 2200





