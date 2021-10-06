import tkinter as tk
from tkinter import *
from tkinter import ttk


def about_dsc():
    tk.messagebox.showinfo('Sobre', 'Aplicativo desenvolvido no âmbito do projeto de investigação WISDom e da tese de doutoramento do Bruno Ferreira\n \nDesenvolvido e mantido por:\n    Bruno Ferreira (bruno.s.ferreira@estbarreiro.ips.pt) \n    Tiago Gonçalves Dias \n\nCoordenação: \n    Prof. Dídia Covas\n    Prof. Nelson Carriço\n    Prof. Raquel Barreira\n \nContributos: \n    Prof. Conceição Amado\n    André Antunes\n    Carlos Ascensão \n    Ricardo Sousa')


def help_menu():
    popup = tk.Toplevel()  # Criacao da instancia
    popup.wm_title("Ajuda")
    popup.resizable(0, 0)  # Desativa o botao de maximizar, minimizar
    popup.geometry('730x600')  # Em pixels
    popup.bind("<Escape>", popup.destroy)  # Para sair do programa
    popup.protocol('WM_DELETE_WINDOW', popup.destroy)
    popup.iconbitmap('icon.ico')

    # self.configure(background='white')  # Background

    notebook = ttk.Notebook(popup)
    add_tab(notebook)
    notebook.pack(expand=1, fill="both")

    popup.mainloop()


def add_tab(notebook):
    tab0 = Tab0Help(notebook)
    # tab1 = Tab1Help(notebook)
    # tab2 = Tab2Help(notebook)
    # tab3 = Tab3Help(notebook)
    # tab4 = Tab4Help(notebook)

    notebook.add(tab0, text="  Geral  ")
    # notebook.add(tab1, text="  1 - Identificação de falhas  ")
    # notebook.add(tab2, text="  2 - Imputaçao de valores pontuais  ")
    # notebook.add(tab3, text="  3 - Normalização temporal ")
    # notebook.add(tab4, text="  4 - Preenchimento de falhas  ")


class help_menu2(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)  # Criacao da instancia
        self.wm_title("Ajuda")
        self.resizable(0, 0)  # Desativa o botao de maximizar, minimizar
        self.geometry('750x600')  # Em pixels
        self.bind("<Escape>", exit)  # Para sair do programa
        self.protocol('WM_DELETE_WINDOW', exit)
        self.iconbitmap('icon.ico')

        # self.configure(background='white')  # Background
        self.notebook = ttk.Notebook()
        self.add_tab()
        self.notebook.pack(expand=1, fill="both")

        self.mainloop()

    def add_tab(self):
        tab0 = Tab0Help(self.notebook)
        # tab1 = Tab1Help(self.notebook)
        # tab2 = Tab2Help(self.notebook)
        # tab3 = Tab3Help(self.notebook)
        # tab4 = Tab4Help(self.notebook)

        self.notebook.add(tab0, text="  Geral  ")
        # self.notebook.add(tab1, text="  1 - Identificação de falhas  ")
        # self.notebook.add(tab2, text="  2 - Imputaçao de valores pontuais  ")
        # self.notebook.add(tab3, text="  3 - Normalização temporal ")
        # self.notebook.add(tab4, text="  4 - Preenchimento de falhas  ")


class Tab0Help(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="white")
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.configure(background='white')  # Background

        self.populate()

    def populate(self):

        for x in range(100):
            self.columnconfigure((x), weight=1)
        for x in range(100):
            self.rowconfigure((x), weight=1)

        Label(self.frame, bg='white', font='Helvetica 8 bold',
              text="Problema:", justify='center').grid(
            column=0, columnspan=100, row=3)
        Label(self.frame, bg='white', font='Helvetica 8',
              text="- Os sistemas de telegestão recolhem e armazenam, de forma sistemática e contínua, medições de caudal com uma dada frequência de aquisição.", wraplength=700, justify='left').grid(
            column=0, columnspan=100, row=4)
        Label(self.frame, bg='white', font='Helvetica 8',
              text="- Os dados de caudal são séries temporais que, devido à falta de fiabilidade do sensor ou outros problemas que afetam o sistema de comunicação, apresentam frequentemente valores anómalos e irregularidades no espaçamento.", wraplength=700, justify='left').grid(
            column=0, columnspan=100, row=5)
        Label(self.frame, bg='white', font='Helvetica 8',
              text="- Estes problemas impedem a aplicação de técnicas avançadas(e.g., aprendizagem automática) para a identificação em tempo quase real de eventos anómalos(e.g., roturas), entre outras possíveis aplicações.", wraplength=700, justify='left').grid(
            column=0, columnspan=100, row=6)

        Label(self.frame, bg='white', font='Helvetica 8 bold',
              text="Solução:", justify='center').grid(
            column=0, columnspan=100, row=7)
        Label(self.frame, bg='white', font='Helvetica 8',
              text="No âmbito do projeto de investigação “Water Intelligence System Data” (WISDom) foi desenvolvida uma metodologia para o tratamento e validação de séries temporais de caudal.", wraplength=700, justify='left').grid(
            column=0, columnspan=100, row=8)
        Label(self.frame, bg='white', font='Helvetica 8',
              text="A metodologia é constituída por quatro passos, conforme apresentado na Figura seguinte", wraplength=700, justify='left').grid(
            column=0, columnspan=100, row=9)
        Label(self.frame, bg='white', font='Helvetica 8',
              text="A metodologia apresentada é implementada no presente aplicativo", justify='left').grid(
            column=0, columnspan=100, row=11)

        self.img0 = PhotoImage(file="help_0.png")  # Imagem do logo
        self.img0 = self.img0.subsample(1, 1)  # Posicao da imagem
        Label(self.frame, image=self.img0, bg="white").grid(row=10, column=50, sticky='NSEW')

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Label(self, bg='white', font='Helvetica 8 bold', text="No âmbito do projeto de investigação “Water Intelligence System Data” (WISDom) foi desenvolvida uma metodologia para \n o tratamento e validação de séries temporais de caudal.").grid(column=0, columnspan=100, row=5)


class Tab1Help(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="white")

        # Preparacao da janela
        self.configure(background='white')  # Background

        # Todas as colunas e rows tem weight de 1 e cria uma matrix de 100 x 100
        for x in range(100):
            self.columnconfigure((x), weight=1)
        for x in range(100):
            self.rowconfigure((x), weight=1)

        # A Label widget to show in toplevel
        Label(self,
              text="O presente separador permite a identificação de leituras anómalas em séries temporais de caudal.",
              bg='white', font='Helvetica 8 bold').pack()
        Label(self,
              text="São distinguidos sete tipos de anómalias, nomeadamente:", bg='white').pack()
        Label(self,
              text="1) Leituras duplicadas com medições iguais \n 2) Leituras duplicadas com medições diferentes \n 3) Leituras negativas \n 4) Picos isolados elevados \n 5) Picos isolados baixos \n 6) Patamares estáticos \n 7) Leituras nulas",
              bg='white').pack()


class Tab2Help(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="white")
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.configure(background='white')  # Background

        self.populate()

    def populate(self):
        '''Put in some fake data'''
        for row in range(100):
            tk.Label(self.frame, text="%s" % row, width=3, borderwidth="1",
                     relief="solid").grid(row=row, column=0)
            t = "this is the second column for row %s" % row
            tk.Label(self.frame, text=t).grid(row=row, column=1)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class Tab3Help(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="white")
        # Preparacao da janela
        self.configure(background='white')  # Background

        # Todas as colunas e rows tem weight de 1 e cria uma matrix de 100 x 100
        for x in range(100):
            self.columnconfigure((x), weight=1)
        for x in range(100):
            self.rowconfigure((x), weight=1)


class Tab4Help(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="white")

        # Preparacao da janela
        self.configure(background='white')  # Background

        # Todas as colunas e rows tem weight de 1 e cria uma matrix de 100 x 100
        for x in range(100):
            self.columnconfigure((x), weight=1)
        for x in range(100):
            self.rowconfigure((x), weight=1)
