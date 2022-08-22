import time
import csv
from itertools import groupby
from operator import itemgetter
from tkinter import filedialog, messagebox
import seaborn as sns
import matplotlib.pyplot as plt
import traces
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from pandas.api.types import CategoricalDtype
from statsmodels.tsa.seasonal import seasonal_decompose
from tkinter import ttk
import math
# import datetime as dt
from functions_forecast import *
from functions_clean import *
import tkinter as tk
from tkinter import *
from sys import exit
import webbrowser
import os

pd.options.mode.chained_assignment = None

label_version = 'v.1.1.0 160822'

FORMAT_DATE = "%d/%m/%y %H:%M:%S"
# FORMAT_DATE = "%H:%M:%S"
DATE_FORM = DateFormatter(FORMAT_DATE)

NORMAL_FONT = "Helvetica 8 bold"

dictionary_keywords = pd.read_csv('dictionary.csv', header=0, index_col=0)
selected_language = 'en'

def about_dsc(dictionary_keywords, selected_language):
    tk.messagebox.showinfo(dictionary_keywords.loc[14,selected_language], dictionary_keywords.loc[98,selected_language])

def manual(selected_language):
    os.system('Manual.pdf')

    # tk.messagebox.showinfo(dictionary_keywords.loc[97,selected_language], dictionary_keywords.loc[99,selected_language])
    # MsgBox = tk.messagebox.askquestion (dictionary_keywords.loc[100,selected_language],dictionary_keywords.loc[99,selected_language],icon = 'question')
    # if MsgBox == 'yes':
        # webbrowser.open("https://wisdom.ips.pt/manual")

    # else:
    #     tk.messagebox.showinfo('Return','You will now return to the application screen')

def research_paper(selected_language):
    os.system('Research_paper.pdf')

def add_dataset(which_tab=None):  # Criar condicao para quando ha e nao ha dataset
    if which_tab == Tab1:  # Quando nao ha dataset anterior meter o original
        repo.set_dataset("dataset1", repo.get_dataset("original"))
    elif which_tab == Tab2:  # Quando nao ha dataset anterior meter o original
        repo.set_dataset("dataset2", repo.get_dataset("original"))
    elif which_tab == Tab3:  # Quando nao ha dataset anterior meter o original
        repo.set_dataset("dataset3", repo.get_dataset("original"))
    elif which_tab == Tab4:  # Quando nao ha dataset anterior meter o original
        repo.set_dataset("dataset4", repo.get_dataset("original"))
    else:  # QUando houver dataset previo colocar esse como entrada
        pass

def file_output(key):  # Exportação do dataset
    # Pergunta que dirétorio guardar o dataset
    file_out = tk.filedialog.asksaveasfilename(defaultextension='.csv', filetype=(
        ("CSV", "*.csv"), ("Text files", "*.txt"), ("all files", "*.*")))

    # Exporta dataset, com NaN
    df_out = repo.get_dataset_output(key)
    df_out.to_csv(file_out, index=False, header=True, na_rep="NaN")

    messagebox.showinfo(dictionary_keywords.loc[20,selected_language],dictionary_keywords.loc[21,selected_language]) #exported and data exported

class Repository:
    def __init__(self):
        self.dataset_original = None  # Dataset do input do user
        self.plot_dataset = None

        # Datasets de entrada para cada separador
        self.datasets = {
            "dataset1": None,
            "dataset2": None,
            "dataset3": None,
            "dataset4": None
        }

        self.datasets_outputs = {
            "dataset1": None,
            "dataset2": None,
            "dataset3": None,
            "dataset4": None
        }

        self.peaks = {
            "negative_peaks": None,
            "high_peaks": None,
            "low_peaks": None,
            "flow_PH": None,
            "flow_PL": None,
            "slopes_PH": None,
            "slopes_PL": None,
            "flat_points": None
        }

        self.tab1_values = {

        }

        self.tab2_values = {
            "nans": None,
            "time_spacing": None,
            "set_nans": None,
            "set_nans_short": None,
            "set_nans_long": None
        }

    def set_original_dataset(self, dataset):  # Insere dataset do user
        self.dataset_original = dataset

    def set_history_dataset(self, dataset):  # Insere dataset do user
        self.dataset_history = dataset


    def set_dataset(self, key, dataset):  # Insere o dataset que vem dos separadores
        if key == "plot":
            self.plot_dataset = dataset
        else:
            self.datasets[key] = dataset

    def set_dataset_output(self, key, dataset):  # Insere o dataset que vem dos separadores
        self.datasets_outputs[key] = dataset

    def get_dataset_output(self, key):  # Retorna qualquer dataset que esteja no repositório
        if self.datasets_outputs[key] is None:
            return self.datasets[key]
        return self.datasets_outputs[key]

    def get_dataset(self, key):  # Retorna qualquer dataset que esteja no repositório
        if key == "original":
            return self.dataset_original
        elif key == "plot":
            return self.plot_dataset
        elif key == "history":
            return self.dataset_history
        else:
            return self.datasets[key]

    def set_peaks(self, negative_peaks, high_peaks, low_peaks, flow_PH, flow_PL, slopes_PH, slopes_PL, flat_points):
        self.peaks.update({
            "negative_peaks": negative_peaks,
            "high_peaks": high_peaks,
            "low_peaks": low_peaks,
            "flow_PH": flow_PH,
            "flow_PL": flow_PL,
            "slopes_PH": slopes_PH,
            "slopes_PL": slopes_PL,
            "flat_points": flat_points
        })

    def get_peaks(self):
        return self.peaks

    def set_values_tab1(self):
        self.tab1_values.update({
        })

    def get_values_tab1(self):
        return self.tab1_values

    def get_values_tab2(self):
        return self.tab2_values

    def set_values_tab2(self, nans, time_spacing):
        self.tab2_values.update({
            "nans": nans,
            "time_spacing": time_spacing
        })

    def set_params_tab3(self, params, key):
        if key=='ARIMA':
            self.params_arima = params
        if key=='ES':
            self.params_es = params

    def get_params_tab3(self,key):
        if key=='ARIMA':
            return self.params_arima
        if key=='ES':
            return self.params_es


class MainGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)  # Criação da janela

        #Import do dicionário de termos



        # Criação do quadro da janela
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Configurações da plataforma
        # self.bind("<Escape>", exit)  # Para sair do programa
        self.protocol('WM_DELETE_WINDOW', exit)  # Para sair do programa

        # Preparacao da janela
        self.title(dictionary_keywords.loc[0,selected_language] + "    (" + label_version + ")")
        self.geometry('1100x700')  # Em pixels
        self.iconbitmap('icon.ico')  # Logo
        self.configure(background='white')  # Background

        # Preparação de uma grelha 100 x 100 (colunas x linhas) com grossura de 1
        for x in range(100):
            self.columnconfigure(x, weight=1)
        for x in range(100):
            self.rowconfigure(x, weight=1)

        self.frames = {}  # Todas os separadores da plataforma ficarão aqui
        frame = Tab0(self.container)  # Inicia construtor do separador
        self.frames[Tab0] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        """Show a frame for the given page name"""
        frame = self.frames[Tab0]  # Apanha a frame requirida
        frame.tkraise()  # Coloca-a "à frente" da plataforma
        menubar = frame.menubar(self)  # Coloca o menu respetivo do separador
        self.configure(menu=menubar)

    def file_input(self, tab):  # Introdução do ficheiro
        # Guarda diretorio do ficheiro
        file_inp = filedialog.askopenfilename(
            filetype=(("CSV", "*.csv"), ("Text files", "*.txt"), ("all files", "*.*")))
        # print(file_inp)
        # Verificação caso o ficheiro de entrada não contenha cabeçalho
        with open(file_inp, newline='') as csvfile:  # Parsa CSV, retorna true ou false se tiver cabeçalho ou não
            dialect = csv.Sniffer().has_header(csvfile.read(1024))
            csvfile.seek(0)

        if dialect is True:  # Remove e coloca o cabeçalho uniforme da plataforma (para evitar cabeçalhos errados)
            dataset = pd.read_csv(file_inp, header=0, names=['date', 'value'], parse_dates=['date'],
                                  infer_datetime_format=False, dayfirst=True).sort_values(by=['date']).reset_index(drop=True)
        else:  # Apenas coloca cabeçalho uniforme
            dataset = pd.read_csv(file_inp, names=['date', 'value'], parse_dates=['date'],
                                  infer_datetime_format=False, dayfirst=True).sort_values(by=['date']).reset_index(drop=True)

        repo.set_original_dataset(dataset)  # Insere no repositório como o primeiro a entrar

        tk.messagebox.showinfo(dictionary_keywords.loc[1,selected_language], dictionary_keywords.loc[2,selected_language])

        if tab == Tab0:  # Se o import foi feito a partir da Capa:
            add_dataset(which_tab=Tab1)
            self.show_frame(Tab1)
        else:
            add_dataset(which_tab=tab)
            self.show_frame(tab)  # Faz-se o show_frame para a mesma tab para fazer as funções de cada separador

    def history_input(self):  # Introdução do ficheiro
        # Guarda diretorio do ficheiro
        file_inp = filedialog.askopenfilename(
            filetype=(("CSV", "*.csv"), ("Text files", "*.txt"), ("all files", "*.*")))
        # print(file_inp)
        # Verificação caso o ficheiro de entrada não contenha cabeçalho
        # Parsa CSV, retorna true ou false se tiver cabeçalho ou não
        with open(file_inp, newline='') as csvfile:
            dialect = csv.Sniffer().has_header(csvfile.read(1024))
            csvfile.seek(0)

        # Remove e coloca o cabeçalho uniforme da plataforma (para evitar cabeçalhos errados)
        if dialect is True:
            dataset = pd.read_csv(file_inp, header=0, names=['date', 'value'], parse_dates=['date'],
                                  infer_datetime_format=False, dayfirst=True).sort_values(by=['date']).reset_index(drop=True)
        else:  # Apenas coloca cabeçalho uniforme
            dataset = pd.read_csv(file_inp, names=['date', 'value'], parse_dates=['date'],
                                  infer_datetime_format=False, dayfirst=True).sort_values(by=['date']).reset_index(drop=True)

        # Insere no repositório como o primeiro a entrar
        repo.set_history_dataset(dataset)

        tk.messagebox.showinfo(dictionary_keywords.loc[1,selected_language], dictionary_keywords.loc[3,selected_language])

    def show_frame(self, page_name, from_menu=False, force=False):
        if len(self.frames) != 5 or force is True:   #cria as framesaquando da 1ª utilização. Tabs são criadas na lingua pretendida
            for F in (Tab1, Tab2, Tab3, Tab4):
                frame = F(self.container)  # Inicia construtor do separador
                self.frames[F] = frame
                frame.grid(row=0, column=0, sticky="nsew")


        """Show a frame for the given page name"""
        frame = self.frames[page_name]  # Apanha a frame requirida
        frame.tkraise()  # Coloca-a "à frente" da plataforma
        if from_menu is False:  # Se o separador não foi selecionado pelo menubar
            frame.tab_functions()

        menubar = frame.menubar(self)  # Coloca o menu respetivo do separador
        self.configure(menu=menubar)

    def clear_all(self):
        # print('clear_all')

        plt.close('all')

        #Limpar dados de cada separador
        #Tab1
        repo.set_dataset("dataset1", None)  # Remove o dataset do repositório
        repo.set_dataset("plot", None)
        repo.set_peaks(None, None, None, None, None, None, None, None)

        #Tab2
        repo.set_dataset("dataset2", None)
        repo.set_values_tab2(None, None)

        #Tab3
        repo.set_dataset("dataset3", None)

        #Tab4
        repo.set_dataset("dataset4", None)
        repo.set_history_dataset(None)
        repo.set_dataset_output("dataset4", None)


        #Criar nova janela de cada separador
        for F in (Tab1, Tab2, Tab3, Tab4):
            frame = F(self.container)  # Inicia construtor do separador
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")


        #puxa tab0 
        frame = self.frames[Tab0]  # Apanha a frame requirida
        frame.tkraise()  # Coloca-a "à frente" da plataforma
        menubar = frame.menubar(self)  # Coloca o menu respetivo do separador
        self.configure(menu=menubar)


    def change_language(self, language):
        global selected_language
        selected_language = language
        # print('change_language')

        frame = Tab0(self.container)  # Inicia construtor do separador
        self.frames[Tab0] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        """Show a frame for the given page name"""
        frame = self.frames[Tab0]  # Apanha a frame requirida
        frame.tkraise()  # Coloca-a "à frente" da plataforma
        menubar = frame.menubar(self)  # Coloca o menu respetivo do separador
        self.configure(menu=menubar)
        return


class Tab0(tk.Frame):  # Capa
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.canvas = Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.background = PhotoImage(file="background_cover.png")
        self.canvas.create_image(0, 0, image=self.background, anchor="nw")

        self.img0 = PhotoImage(file="Wisdom_logo.png")
        self.canvas.create_image(1100/2, 600/2, image=self.img0, anchor="center")

        self.img1 = PhotoImage(file="ips.png")
        self.canvas.create_image(1100/5 * 1, 600, image=self.img1, anchor="center")

        self.img2 = PhotoImage(file="ist.png")
        self.canvas.create_image(1100/5 * 2, 600, image=self.img2, anchor="center")

        self.img3 = PhotoImage(file="inesc.png")
        self.canvas.create_image(1100/5 * 3, 600, image=self.img3, anchor="center")

        self.img4 = PhotoImage(file="fct.png")
        self.canvas.create_image(1100/5 * 4, 600, image=self.img4, anchor="center")
        
        self.canvas_txt_id1 = self.canvas.create_text(1100/2, 400, fill="white", font="Helvetica 14 bold",
                                text=dictionary_keywords.loc[4,selected_language] + '   ')
        self.canvas.create_text(1050, 20, fill="white", font="Helvetica 8",
                                text=label_version)
        
    def menubar(self, root):  # Menu - Semelhante em cada separador, diferenciando na visualização dos gráficos (WIP)
        menubar = tk.Menu(root)  # Criação do menu
        fileMenu = tk.Menu(menubar, tearoff=False)  # Ficheiro
        fileMenu.add_command(label=dictionary_keywords.loc[5,selected_language], command=lambda: root.file_input(Tab0))
        fileMenu.add_separator()
        fileMenu.add_command(label=dictionary_keywords.loc[6,selected_language], command=self.quit)

        menubar.add_cascade(label=dictionary_keywords.loc[7,selected_language], menu=fileMenu)

        methodMenu = tk.Menu(menubar, tearoff=False)  # Métodos
        methodMenu.add_command(label=dictionary_keywords.loc[8,selected_language], command=lambda: root.show_frame(Tab1, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[9,selected_language], command=lambda: root.show_frame(Tab2, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[10,selected_language], command=lambda: root.show_frame(Tab3, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[11,selected_language], command=lambda: root.show_frame(Tab4, from_menu=True))
        menubar.add_cascade(label=dictionary_keywords.loc[12,selected_language], menu=methodMenu)

        helpMenu = tk.Menu(menubar, tearoff=False)  # Ajuda e Sobre
        helpMenu.add_command(label=dictionary_keywords.loc[97,selected_language], command=lambda: manual(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[103,selected_language], command=lambda: research_paper(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[14,selected_language ], command=lambda: about_dsc(dictionary_keywords, selected_language))
        menubar.add_cascade(label=dictionary_keywords.loc[13,selected_language], menu=helpMenu)


        languageMenu = tk.Menu(menubar, tearoff=False)  # Ajuda e Sobre
        languageMenu.add_command(label="English", command=lambda: root.change_language("en"))
        languageMenu.add_command(label="Portuguese", command=lambda: root.change_language("pt"))
        menubar.add_cascade(label=dictionary_keywords.loc[94,selected_language], menu=languageMenu)


        return menubar

    def get_data(self):
        # Na capa não tem dados para ir buscar ao repositório
        pass


class Tab1(tk.Frame):  # 1- Identificação de falhas
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)  # Criação do separador
        self.configure(background='white')  # Background

        # Preparação de uma grelha 100 x 100 (colunas x linhas) com grossura de 1
        for x in range(100):
            self.columnconfigure(x, weight=1)
        for x in range(100):
            self.rowconfigure(x, weight=1)

        # # Formato das horas para graphs
        # self.format_date = "%d/%m/%y %H:%M:%S"
        # DATE_FORM = DateFormatter(self.format_date)  # Labels nos gráficos

        # Separadores - linhas que dividem o programa
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=2, row=12, columnspan=96, sticky='ew')
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=2, row=60, columnspan=96, sticky='ew')

        # Botões
        # Remover os eventos anómalos todos
        tk.Button(self, text=dictionary_keywords.loc[15,selected_language], command=self.remove_all, font=NORMAL_FONT,
                  relief=GROOVE).grid(row=68, column=75, columnspan=10, sticky='NSEW')

        # Avançar
        tk.Button(self, text=dictionary_keywords.loc[16,selected_language], command=self.next_tab, font=NORMAL_FONT,
                  relief=GROOVE).grid(row=90, column=75, columnspan=10, sticky='NSEW')

        # Inputs de parâmetros
        #### Picos altos ####
        # Tamanho da janela
        tk.Label(self, text=dictionary_keywords.loc[17,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=5, row=56, columnspan=10, sticky='NSWE')

        self.wPH = tk.Entry(self, textvariable=tk.StringVar(self, None))
        self.wPH.grid(column=15, row=56, columnspan=1, sticky='NSWE')

        # Threshold
        tk.Label(self, text=dictionary_keywords.loc[95,selected_language], bg='white', #threshold label
                 font=NORMAL_FONT, anchor='e').grid(column=5, row=58, columnspan=10, sticky='NSWE')
        self.tPH = tk.Entry(self, textvariable=tk.StringVar(self, None))
        self.tPH.grid(column=15, row=58, columnspan=1, sticky='NSWE')

        #### Picos baixos ####
        # Tamanho da janela
        tk.Label(self, text=dictionary_keywords.loc[17,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=45, row=56, columnspan=10, sticky='NSWE')
        self.wPL = tk.Entry(self, textvariable=tk.StringVar(self, None))
        self.wPL.grid(column=55, row=56, columnspan=1, sticky='NSWE')

        # Threshold
        tk.Label(self, text=dictionary_keywords.loc[95,selected_language], bg='white', #threshold label
                 font=NORMAL_FONT, anchor='e').grid(column=45, row=58, columnspan=10, sticky='NSWE')
        self.tPL = tk.Entry(self, textvariable=tk.StringVar(self, None))
        self.tPL.grid(column=55, row=58, columnspan=1, sticky='NSWE')

        #### Patamares ####
        # Tamanho da janela
        tk.Label(self, text=dictionary_keywords.loc[17,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=70, row=56, columnspan=10, sticky='NSWE')
        self.wFL = tk.Entry(self, textvariable=tk.StringVar(self, None))
        self.wFL.grid(column=80, row=56, columnspan=2, sticky='NSWE')

        # Threshold
        tk.Label(self, text=dictionary_keywords.loc[102,selected_language], bg='white', #threshold label
                 font=NORMAL_FONT, anchor='e').grid(column=70, row=58, columnspan=10, sticky='NSWE')
        self.tFL = tk.Entry(self, textvariable=tk.StringVar(self, None))
        self.tFL.grid(column=80, row=58, columnspan=2, sticky='NSWE')

        # Funções dos gráficos em branco
        self.graph_original()  # Série original
        self.table_original()  # Análise do espaçamento/Caudal
        self.histograms_original()  # Histograma Espaçamento/Caudal
        self.peak_high_original()  # Picos anómalos altos
        self.peak_low_original()  # Picos anómalos baixos
        self.flat_original()  # Patamares estáticos
        self.final_graph()  # Série com anómalos identificados
        self.table_results_original()  # Contagem

    def tab_functions(self):
        df = repo.get_dataset("dataset1")
        values = df['value']
        dates = df['date']

        values2 = df['value'].values.copy()
        dates2 = df['date'].values.copy()

        # Create the diffs
        flow = np.diff(values2)
        flow = np.insert(flow, 0, np.nan, axis=0)
        time = np.diff(dates2).tolist()
        time = np.divide(time, np.power(10, 9))


        slopes = np.divide(abs(flow[1:]), time)
        slopes = np.insert(slopes, 0, 0, axis=0)
        slopes = pd.DataFrame(slopes)
        slopes = slopes.describe(percentiles=[0.05, 0.25, 0.50, 0.75, 0.80, 0.85, 0.90, 0.95, 0.97, 0.995])  # Estatisticas do espacamento
        slopes = slopes.iloc[:, 0]
        # print(slopes)

        plt.close('all')
        self.upd_graph_original(values, dates)  # Atualiza Série original
        self.upd_table_original(values, dates)  # Atualiza Análise do espaçamento/caudal
        self.upd_histograms_original(values)  # Atualiza histograma do espaçamento/caudal
        # print(self.spacing_detail)

        # Para limpar os gráficos
        self.wPH.delete(0, "end")
        self.tPH.delete(0, "end")
        self.wPH.insert(0, int(self.spacing_detail[0][5] * 3))
        self.tPH.insert(0, round(float(slopes[12]), 3))

        self.wPL.delete(0, "end")
        self.tPL.delete(0, "end")
        self.wPL.insert(0, int(self.spacing_detail[0][5] * 3))
        self.tPL.insert(0, round(float(slopes[12]), 3))

        self.wFL.delete(0, "end")
        self.tFL.delete(0, "end")
        self.wFL.insert(0, max(int(self.spacing_detail[0][5] * 2.5),300))
        self.tFL.insert(0, round(float(self.value_detail[2] * 0.03), 3))
        # Para limpar os gráficos que já estavam preenchidos
        self.peak_high_original()
        self.peak_low_original()
        self.flat_original()
        self.final_graph()
        self.table_results_original()

    def menubar(self, root):  # O mesmo com o Tab0, adicionando os gráficos respetivos
        menubar = tk.Menu(root)

        fileMenu = tk.Menu(menubar, tearoff=False)  # Ficheiro
        fileMenu.add_command(label=dictionary_keywords.loc[5,selected_language], command=lambda: root.file_input(Tab1))
        fileMenu.add_command(label=dictionary_keywords.loc[18,selected_language], command=self.clear)
        fileMenu.add_command(label=dictionary_keywords.loc[101,selected_language], command=lambda: root.clear_all()) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[19,selected_language], command=lambda: file_output("dataset1")) #export data
        fileMenu.add_separator()
        fileMenu.add_command(label=dictionary_keywords.loc[6,selected_language], command=self.quit)
        menubar.add_cascade(label=dictionary_keywords.loc[7,selected_language], menu=fileMenu)

        methodMenu = tk.Menu(menubar, tearoff=False)  # Métodos
        methodMenu.add_command(label=dictionary_keywords.loc[8,selected_language], command=lambda: root.show_frame(Tab1, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[9,selected_language], command=lambda: root.show_frame(Tab2, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[10,selected_language], command=lambda: root.show_frame(Tab3, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[11,selected_language], command=lambda: root.show_frame(Tab4, from_menu=True))
        menubar.add_cascade(label=dictionary_keywords.loc[12,selected_language], menu=methodMenu)

        graphMenu = tk.Menu(menubar, tearoff=False)  # Gráficos de visualização
        graphMenu.add_command(label=dictionary_keywords.loc[22,selected_language], command=self.G1)
        graphMenu.add_command(label=dictionary_keywords.loc[23,selected_language], command=self.G2)
        graphMenu.add_command(label=dictionary_keywords.loc[24,selected_language], command=self.G3)
        graphMenu.add_command(label=dictionary_keywords.loc[25,selected_language], command=self.G4)
        graphMenu.add_command(label=dictionary_keywords.loc[26,selected_language], command=self.G5)
        menubar.add_cascade(label=dictionary_keywords.loc[27,selected_language], menu=graphMenu)

        helpMenu = tk.Menu(menubar, tearoff=False)  # Ajuda e sobre
        helpMenu.add_command(label=dictionary_keywords.loc[97,selected_language], command=lambda: manual(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[103,selected_language], command=lambda: research_paper(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[14,selected_language], command=lambda: about_dsc(dictionary_keywords, selected_language))#about
        menubar.add_cascade(label=dictionary_keywords.loc[13,selected_language], menu=helpMenu)


        return menubar

    def clear(self):  # Limpar dados
        repo.set_dataset("dataset1", None)  # Remove o dataset do repositório
        repo.set_dataset("plot", None)
        repo.set_peaks(None, None, None, None, None, None, None, None)
        plt.close('all')

        # Limpa todas as labels das estatísticas
        for x in range(self.spacing_detail.shape[0]):
            tk.Label(self, text='', bg='white').grid(column=50, row=1 + x, columnspan=5, sticky='NSWE')

        for x in range(self.value_detail.shape[0]):
            tk.Label(self, text='', bg='white').grid(column=55, row=1 + x, columnspan=5, sticky='NSWE')

        # Remove todos os parâmetros
        self.wPH.delete(0, "end")
        self.tPH.delete(0, "end")
        self.wPL.delete(0, "end")
        self.tPL.delete(0, "end")
        self.wFL.delete(0, "end")
        self.tFL.delete(0, "end")

        for x in range(8):
            tk.Label(self, text='', bg='white').grid(column=80, row=74 + x, sticky='NSWE')

        # Funcoes dos gráficos em branco
        self.graph_original()
        self.histograms_original()
        self.peak_high_original()
        self.peak_low_original()
        self.flat_original()
        self.final_graph()

    def remove_all(self):  # Função de remover todos os anómalos, em sequência
        plt.close(2)
        plt.close(3)
        plt.close(4)
        plt.close(5)

        df = repo.get_dataset("dataset1").copy()
        df, dup_equal = remove_duplicates_exact(df)
        # = len(repo.get_dataset("dataset1")) - len(df) # Duplicates exatos

        nans = []  # nans originais

        # array com ID's dos nans
        for row in range(len(df)):
            if np.isnan(df['value'][row]):
                nans.append(row)
        # Usa o dataset e vai passando por uma sucessão de funções, onde no fim irá ter todos os valores colocados a nan
        # os respetivos ìndices, para visualização
        df, dup_diffs = remove_duplicates_dif(df)  # Duplicates diferentes

        temp_df = df.copy()  # Para utilizar nos gráficos a posteriori
        repo.set_dataset("plot", temp_df)

        df, negative_peaks = remove_negatives(df)  # negativos

        # Picos altos
        df, high_peaks, flow_PH, slopes_PH = remove_pontuals_high(df, win_size=int(self.wPH.get()),
                                                                  threshold=float(self.tPH.get()))

        self.upd_peak_high(temp_df, high_peaks, flow_PH, slopes_PH)

        # Picos baixos
        df, low_peaks, flow_PL, slopes_PL = remove_pontuals_low(df, win_size=int(self.wPL.get()),
                                                                threshold=float(self.tPL.get()))

        self.upd_peak_low(temp_df, low_peaks, flow_PL, slopes_PL)

        # Patamares
        df, flat_points = new_remove_flat_lines(df, win_size=int(self.wFL.get()), threshold=float(self.tFL.get()))

        self.upd_flat(df, temp_df, flat_points)

        # atualizar todos os gráficos
        self.upd_final_graph(df, temp_df, negative_peaks, high_peaks, low_peaks, flat_points)
        self.upd_table_results(dup_equal, dup_diffs, nans, negative_peaks, high_peaks, low_peaks, flat_points)

        repo.set_dataset_output("dataset1", df)
        repo.set_peaks(negative_peaks, high_peaks, low_peaks, flow_PH, flow_PL, slopes_PH, slopes_PL, flat_points)

    def next_tab(self):  # Botão avançar
        # O que sai dos métodos é colocado no dataset de saída
        # E no de entrada para ser usado no método (Separador) seguinte
        repo.set_dataset("dataset2", repo.get_dataset_output("dataset1"))
        app.show_frame(Tab2)  # Muda de separador

    def graph_original(self):  # Gráfico da Série original, em branco
        self.fig = Figure(figsize=(1, 1), dpi=50)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(dictionary_keywords.loc[22,selected_language])

        # Label das horas
        self.ax.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                     ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language])
        self.ax.legend()

        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language])  # Label do Y (caudal m^3/h)

        FigureCanvasTkAgg(self.fig, master=self).get_tk_widget().grid(
            column=0, row=0, columnspan=45, rowspan=10, sticky='NSEW')

    def upd_graph_original(self, values, dates):  # Atualiza gráfico da série original
        # Limpa gráfico prévio
        self.ax.cla()

        # Gráfico da série original
        self.ax.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language])

        # Formatação do gráfico
        self.ax.xaxis.set_major_formatter(DATE_FORM)  # Para a label do x, data no formato estipulado no main
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language])  # Label do Y (caudal m^3/h)
        self.ax.set_title(dictionary_keywords.loc[22,selected_language])
        self.ax.legend()

        self.fig.canvas.draw()

    def table_original(self):  # Estatisticas do Input
        tk.Label(self, text=dictionary_keywords.loc[29,selected_language], bg='white', font=NORMAL_FONT,
                 wraplength=100).grid(column=50, row=0, columnspan=5, rowspan=1, sticky='NSWE')#Title 
        tk.Label(self, text=dictionary_keywords.loc[30,selected_language], bg='white', font=NORMAL_FONT,
                 wraplength=80).grid(column=55, row=0, columnspan=5, rowspan=1, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[31,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=45, row=1, columnspan=5, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[32,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=45, row=2, columnspan=5, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[33,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=45, row=3, columnspan=5, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[34,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=45, row=4, columnspan=5, sticky='NSWE')
        tk.Label(self, text="P25", bg='white', font=NORMAL_FONT).grid(
            column=45, row=5, columnspan=5, sticky='NSWE')
        tk.Label(self, text="P50", bg='white', font=NORMAL_FONT).grid(
            column=45, row=6, columnspan=5, sticky='NSWE')
        tk.Label(self, text="P75", bg='white', font=NORMAL_FONT).grid(
            column=45, row=7, columnspan=5, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[35,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=45, row=8, columnspan=5, sticky='NSWE')

        for x in range(8):
            tk.Label(self, text='', bg='white').grid(column=50, row=1 + x, columnspan=5, sticky='NSWE')
        for x in range(8):
            tk.Label(self, text='', bg='white').grid(column=55, row=1 + x, columnspan=5, sticky='NSWE')

    def upd_table_original(self, values, dates):  # Atualiza estatistica de input
        # Preparacao das variaveis
        sum = 0
        time_spacing = np.zeros(len(values) - 1)

        # Cálculo do spacamento temporal
        for line in range(1, len(values), 1):
            # Conversao ns para s
            time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))
            sum += float((dates[line] - dates[line - 1]) / np.power(10, 9))

        time_spacing = pd.DataFrame(time_spacing)
        self.spacing_detail = time_spacing.describe()  # Estatisticas do espacamento
        self.espacamento = time_spacing.iloc[:, 0]
        # print('detail',self.spacing_detail)
        # print('espacamento',self.espacamento)
        # Escrever ao longo da "tabela"
        for x in range(self.spacing_detail.shape[0]):
            tk.Label(self, text=round(self.spacing_detail[0][x], 2), bg='white').grid(
                column=50, row=1 + x, columnspan=5, sticky='NSWE')

        self.value_detail = values.describe(include=[np.number])  # Estatisticas do caudal

        # Escrever ao longo da "tabela"
        for x in range(self.value_detail.shape[0]):
            if isinstance(self.value_detail[x], str):
                tk.Label(self, text=self.value_detail[x], bg='white').grid(column=55, row=1 + x, columnspan=5,
                                                                           sticky='NSWE')
            else:
                tk.Label(self, text=round(self.value_detail[x], 2), bg='white').grid(column=55, row=1 + x, columnspan=5,
                                                                                     sticky='NSWE')
        tk.Label(self, text=self.spacing_detail[0][0] + 1, bg='white').grid(column=55, row=1 + 0, columnspan=5,
                                                                            sticky='NSWE')

    def histograms_original(self):  # Histogramas do Input
        # Espaçamento temporal
        self.fig2 = Figure(figsize=(1, 1), dpi=50)
        self.hist = self.fig2.add_subplot(111)
        self.hist.set_title(dictionary_keywords.loc[36,selected_language]) #Histogram spacing title 

        FigureCanvasTkAgg(self.fig2, master=self).get_tk_widget().grid(
            column=60, row=0, columnspan=20, rowspan=10, sticky='NSEW')

        # Caudal
        self.fig3 = Figure(figsize=(1, 1), dpi=50)
        self.hist2 = self.fig3.add_subplot(111)
        self.hist2.set_title(dictionary_keywords.loc[37,selected_language]) #Histogram Flow title

        FigureCanvasTkAgg(self.fig3, master=self).get_tk_widget().grid(
            column=80, row=0, columnspan=20, rowspan=10, sticky='NSEW')

    def upd_histograms_original(self, caudal):  # Atualiza histograma do input
        self.hist.cla()
        self.hist.hist(self.espacamento, bins=20, alpha=0.5)
        self.hist.set_title(dictionary_keywords.loc[36,selected_language]) #Histogram spacing title
        self.fig2.canvas.draw()

        self.hist2.cla()
        self.hist2.hist(caudal, bins=20, alpha=0.5)
        self.hist2.set_title(dictionary_keywords.loc[37,selected_language]) #Histogram Flow title

        self.fig3.canvas.draw()

    ### Tratamento dos dados ###
    def peak_high_original(self):  # Picos altos
        self.fig5 = Figure(figsize=(1, 1), dpi=50)
        self.deltaq_pho = self.fig5.add_subplot(111)
        self.deltaq_pho.set_title(dictionary_keywords.loc[23,selected_language]) #abnormal high peaks title

        # Labels e gráfico default para gráfico do caudal
        self.deltaq_pho.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                             ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[39,selected_language])
        self.deltaq_pho.set_ylabel(dictionary_keywords.loc[39,selected_language])  # Label do Y (difference)
        self.deltaq_pho.legend()
        FigureCanvasTkAgg(self.fig5, master=self).get_tk_widget().grid(
            column=0, row=13, columnspan=38, rowspan=20, sticky='NSEW')

        # Labels e gráfico default para gráfico do gradiente do caudal
        self.fig6 = Figure(figsize=(1, 1), dpi=50)
        self.gradq_pho = self.fig6.add_subplot(111)
        self.gradq_pho.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                            ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[38,selected_language])

        self.gradq_pho.set_ylabel(dictionary_keywords.loc[38,selected_language]) # Label do Y rate of change 
        self.gradq_pho.legend()

        FigureCanvasTkAgg(self.fig6, master=self).get_tk_widget().grid(
            column=0, row=33, columnspan=38, rowspan=18, sticky='NSEW')

    def upd_peak_high(self, df, high_peaks, flow_PH, slopes_PH):  # Atualiza gráficos dos picos altos
        # Limpa graficos existentes
        self.deltaq_pho.cla()
        self.gradq_pho.cla()
        #
        # # Divide em dois arrays para simplificar a manipulação nos gráficos
        # self.values = [float(i[1]) for i in self.df2]  # Valores de Caudal, em float
        # self.values = np.array(self.values)
        #
        # self.dates = [i[0].to_pydatetime() for i in self.df2]  # Datas, em pydatetime
        # self.dates = np.array(self.dates)

        # Gráfico do caudal
        self.deltaq_pho.plot(df['date'], flow_PH, "#6F8EAF", label=dictionary_keywords.loc[39,selected_language]) #flowrate lable
        self.deltaq_pho.plot(df['date'][high_peaks], flow_PH[high_peaks], "^r", label=dictionary_keywords.loc[50,selected_language]) #abnormal high peaks lable
        # self.deltaq_pho.xaxis.set_major_formatter(DATE_FORM)
        self.deltaq_pho.set_title(dictionary_keywords.loc[23,selected_language]) #abnormal high values title
        self.deltaq_pho.set_ylabel(dictionary_keywords.loc[39,selected_language])  # Label do Y (difference)
        self.deltaq_pho.legend()
        self.fig5.canvas.draw()

        # Gráfico do gradiente do caudal
        self.gradq_pho.plot(df['date'], slopes_PH, "#6F8EAF", label=dictionary_keywords.loc[38,selected_language]) #label of rate of change plot
        self.gradq_pho.plot(df['date'][high_peaks], slopes_PH[high_peaks],
                            "^r", label=dictionary_keywords.loc[50,selected_language]) #label of Abnormally high values plot
        self.gradq_pho.axhline(y=float(self.tPH.get()), linestyle="--", label="Threshold")
        self.gradq_pho.axhline(y=-float(self.tPH.get()), linestyle="--")
        # self.gradq_pho.xaxis.set_major_formatter(DATE_FORM)
        self.gradq_pho.set_ylabel(dictionary_keywords.loc[38,selected_language]) # Label do Y rate of change 
        self.gradq_pho.legend()
        self.fig6.canvas.draw()

    def peak_low_original(self):  # Picos Baixos, Igual aos picos altos
        self.fig8 = Figure(figsize=(1, 1), dpi=50)
        self.deltaq_plo = self.fig8.add_subplot(111)
        self.deltaq_plo.set_title(dictionary_keywords.loc[23,selected_language]) #abnormal high values title
        self.deltaq_plo.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                             ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[39,selected_language]) #label of difference in plot
        self.deltaq_plo.set_ylabel(dictionary_keywords.loc[39,selected_language])  # Label do Y (difference)
        self.deltaq_plo.legend()
        FigureCanvasTkAgg(self.fig8, master=self).get_tk_widget().grid(
            column=38, row=13, columnspan=32, rowspan=20, sticky='NSEW')

        self.fig9 = Figure(figsize=(1, 1), dpi=50)
        self.gradq_plo = self.fig9.add_subplot(111)
        self.gradq_plo.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                            ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[38,selected_language]) #label of rate of change in plot
        self.gradq_plo.set_ylabel(dictionary_keywords.loc[38,selected_language]) # Label do Y rate of change 
        self.gradq_plo.legend()
        FigureCanvasTkAgg(self.fig9, master=self).get_tk_widget().grid(
            column=38, row=33, columnspan=32, rowspan=18, sticky='NSEW')

    def upd_peak_low(self, df, low_peaks, flow_PL,
                     slopes_PL):  # Atualiza gráficos dos picos baixos, igual aos picos altos
        self.deltaq_plo.cla()
        self.gradq_plo.cla()

        self.deltaq_plo.plot(df['date'], flow_PL, "#6F8EAF", label=dictionary_keywords.loc[39,selected_language]) #label of difference in plot
        self.deltaq_plo.plot(df['date'][low_peaks], flow_PL[low_peaks], "^m", label=dictionary_keywords.loc[51,selected_language]) #low peaks label in plot

        # self.deltaq_plo.xaxis.set_major_formatter(DATE_FORM)
        self.deltaq_plo.set_title(dictionary_keywords.loc[24,selected_language]) #low peaks title
        self.deltaq_plo.set_ylabel(dictionary_keywords.loc[39,selected_language])  # Label do Y (difference)
        self.deltaq_plo.legend()
        self.fig8.canvas.draw()

        self.gradq_plo.plot(df['date'], slopes_PL, "#6F8EAF", label=dictionary_keywords.loc[38,selected_language]) #rate of change plot lable
        self.gradq_plo.plot(df['date'][low_peaks], slopes_PL[low_peaks], "^m", label=dictionary_keywords.loc[51,selected_language]) #low peaks label in plot
        self.gradq_plo.axhline(y=float(self.tPL.get()), linestyle="--", label=dictionary_keywords.loc[96,selected_language]) #X label threshold
        self.gradq_plo.axhline(y=-float(self.tPL.get()), linestyle="--")

        # self.gradq_plo.xaxis.set_major_formatter(DATE_FORM)
        self.gradq_plo.set_ylabel(dictionary_keywords.loc[38,selected_language]) # Label Y rate of change 
        self.gradq_plo.legend()
        self.fig9.canvas.draw()

    def flat_original(self):  # Patamares
        self.fig10 = Figure(figsize=(1, 1), dpi=50)
        self.flat = self.fig10.add_subplot(111)
        self.flat.set_title(dictionary_keywords.loc[25,selected_language]) #flat lines title

        # we plot y as a function of a, which parametrizes x
        self.flat.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                       ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) #flowrate lable
        self.flat.legend()
        self.flat.set_ylabel(dictionary_keywords.loc[28,selected_language]) # Y lable of flowrate

        FigureCanvasTkAgg(self.fig10, master=self).get_tk_widget().grid(
            column=70, row=13, columnspan=35, rowspan=42, sticky='NSEW')

    def upd_flat(self, df, temp_df, flat_points):  # Atualiza gráficos dos patamares
        self.flat.cla()  # Limpa gráficos prévios

        # Plot original com os picos assinalados
        self.flat.plot(df['date'], df['value'], "#6F8EAF", label=dictionary_keywords.loc[28,selected_language])  # Plot original flowrate
        self.flat.plot(temp_df['date'][flat_points], temp_df['value'][flat_points], "^g", label=dictionary_keywords.loc[40,selected_language]) #flat lines values plot

        # self.flat.xaxis.set_major_formatter(DATE_FORM)
        self.flat.set_title(dictionary_keywords.loc[25,selected_language]) #flat lines title
        self.flat.set_ylabel(dictionary_keywords.loc[28,selected_language]) # Label y - flowrate 
        self.flat.legend()
        self.fig10.canvas.draw()

    def final_graph(self):  # Série de Output
        self.fig11 = Figure(figsize=(1, 1), dpi=65)
        self.final_fig = self.fig11.add_subplot(111)
        self.final_fig.set_title(dictionary_keywords.loc[26,selected_language]) #Time series with identified anomalous values 

        # we plot y as a function of a, which parametrizes x
        self.final_fig.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                            ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label of - flowrate 
        self.final_fig.legend()
        self.final_fig.set_ylabel(dictionary_keywords.loc[28,selected_language]) # Label y - flowrate 

        FigureCanvasTkAgg(self.fig11, master=self).get_tk_widget().grid(
            column=0, row=61, columnspan=75, rowspan=40, sticky='NSEW')

    def upd_final_graph(self, df, temp_df, negative_peaks, high_peaks, low_peaks,
                        flat_points):  # Atualiza série de output
        self.final_fig.cla()  # Limpa gráficos prévios

        # Gráfico original
        self.final_fig.plot(df['date'], df['value'], '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate 

        # Negativos
        self.final_fig.plot(temp_df['date'][negative_peaks], temp_df['value'][negative_peaks],
                            linestyle='None', marker="x", color='#D95221', label=dictionary_keywords.loc[41,selected_language])

        # Picos altos
        self.final_fig.plot(temp_df['date'][high_peaks], temp_df['value'][high_peaks], "xr", label=dictionary_keywords.loc[23,selected_language])#Abnormally high values

        # Picos Baixos
        self.final_fig.plot(temp_df['date'][low_peaks], temp_df['value'][low_peaks], "xm", label=dictionary_keywords.loc[24,selected_language])#Abnormally low values

        # Patamares
        self.final_fig.plot(temp_df['date'][flat_points], temp_df['value'][flat_points], "xg", label=dictionary_keywords.loc[44,selected_language]) #Values in flat line

        # Formatação dos gráficos
        self.final_fig.xaxis.set_major_formatter(DATE_FORM)
        self.final_fig.set_ylabel(dictionary_keywords.loc[28,selected_language]) # Label y - flowrate 
        self.final_fig.set_title(dictionary_keywords.loc[26,selected_language]) #Time series with identified anomalous values 
        self.final_fig.legend()
        self.fig11.canvas.draw()

    def table_results_original(self):  # Tabela resultados finais
        #count:
        tk.Label(self, text=dictionary_keywords.loc[59,selected_language], bg='white', font=NORMAL_FONT).grid(column=80, row=73, sticky='NSWE')
        #Dup. equal:
        tk.Label(self, text=dictionary_keywords.loc[46,selected_language], bg='white', font=NORMAL_FONT).grid(column=79, row=74, sticky='NSWE')
        #dup different:
        tk.Label(self, text=dictionary_keywords.loc[47,selected_language], bg='white', font=NORMAL_FONT).grid(column=79, row=75, sticky='NSWE')
        #negative:
        tk.Label(self, text=dictionary_keywords.loc[41,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=79, row=76, sticky='NSWE')
        
        #Abnormally high values
        tk.Label(self, text=dictionary_keywords.loc[23,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=79, row=77, sticky='NSWE')
        
        #Abnormally low values:
        tk.Label(self, text=dictionary_keywords.loc[24,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=79, row=78, sticky='NSWE')
        #Values in flat line
        tk.Label(self, text=dictionary_keywords.loc[44,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=79, row=79, sticky='NSWE')
        
        #null measurments:
        tk.Label(self, text=dictionary_keywords.loc[48,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=79, row=80, sticky='NSWE')
        #total:
        tk.Label(self, text=dictionary_keywords.loc[49,selected_language], bg='white', font=NORMAL_FONT).grid(
            column=79, row=81, sticky='NSWE')

        for x in range(8):
            tk.Label(self, text='', bg='white').grid(column=80, row=74 + x, sticky='NSWE')

    def upd_table_results(self, dup_equal, dup_diffs, nans, negative_peaks, high_peaks, low_peaks,
                          flat_points):  # Atualiza a tabela de resultados final
        tk.Label(self, text=dup_equal, bg='white').grid(column=80, row=74, sticky='NSWE')
        tk.Label(self, text=len(dup_diffs), bg='white').grid(column=80, row=75, sticky='NSWE')

        tk.Label(self, text=len(negative_peaks), bg='white').grid(column=80, row=76, sticky='NSWE')

        tk.Label(self, text=len(high_peaks), bg='white').grid(column=80, row=77, sticky='NSWE')
        tk.Label(self, text=len(low_peaks), bg='white').grid(column=80, row=78, sticky='NSWE')

        tk.Label(self, text=len(flat_points), bg='white').grid(column=80, row=79, sticky='NSWE')

        tk.Label(self, text=len(nans), bg='white').grid(column=80, row=80, sticky='NSWE')

        # Total de falhas
        n_falhas_tot = dup_equal + len(dup_diffs) + len(negative_peaks) + len(high_peaks) + len(low_peaks) + len(
            flat_points) + len(nans)

        tk.Label(self, text=n_falhas_tot, bg='white', font=NORMAL_FONT).grid(column=80, row=81, sticky='NSWE')

    #### Gráficos externos ####
    def G1(self):  # Série Original
        try:
            df = repo.get_dataset("dataset1")
            plt.figure(1)
            plt.cla()
            plt.plot(df['date'], df['value'], '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate 
            plt.gca().xaxis.set_major_formatter(DATE_FORM)
            plt.ylabel(dictionary_keywords.loc[28,selected_language]) # Label y - flowrate 
            plt.title(dictionary_keywords.loc[22,selected_language]) #original serie
            plt.legend()
            plt.show()
        except TypeError:
            plt.figure(1)
            plt.cla()
            plt.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                     ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label- flowrate 
            plt.ylabel(dictionary_keywords.loc[28,selected_language]) # Label y - flowrate 
            plt.title(dictionary_keywords.loc[22,selected_language]) #original serie
            plt.legend()
            plt.show()

    def G2(self):  # Picos altos
        df = repo.get_dataset_output("dataset1")
        temp_df = repo.get_dataset("plot")
        peaks = repo.get_peaks()
        plt.figure(2)
        plt.clf()

        # Plotting of all values
        plt.subplot(3, 1, 1)
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.plot(df['date'], df['value'], '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        plt.plot(df['date'][peaks['high_peaks']], temp_df['value'][peaks['high_peaks']], "xr",
                 label=dictionary_keywords.loc[50,selected_language]) #label for Abnormally high values  # Plotting of all peaks
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # Label y - flowrate 
        plt.title(dictionary_keywords.loc[23,selected_language])#Abnormally high values title
        plt.legend()

        # Plot the differences in the values
        plt.subplot(3, 1, 2)
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.plot(df['date'], peaks['flow_PH'], "#6F8EAF", label=dictionary_keywords.loc[39,selected_language]) # plot label - difference 
        plt.plot(df['date'][peaks['high_peaks']], peaks['flow_PH'][peaks['high_peaks']], "^r",
                 label=dictionary_keywords.loc[50,selected_language]) #label for Abnormally high values
        plt.ylabel(dictionary_keywords.loc[39,selected_language]) # yaxis label - difference 
        plt.legend()

        # Plot the slopes along with the threshold
        plt.subplot(3, 1, 3)
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.plot(df['date'], peaks['slopes_PH'], "#6F8EAF", label=dictionary_keywords.loc[38,selected_language]) # plot label - rate of change 
        plt.plot(df['date'][peaks['high_peaks']], peaks['slopes_PH'][peaks['high_peaks']], "^r",
                 label=dictionary_keywords.loc[50,selected_language]) #label for Abnormally high values
        plt.axhline(y=float(self.tPH.get()), linestyle="--", label="Threshold")
        plt.axhline(y=-float(self.tPH.get()), linestyle="--")
        plt.ylabel(dictionary_keywords.loc[38,selected_language]) # plot label - rate of change 
        plt.legend()

        plt.show()

    def G3(self):  # Picos baixos
        df = repo.get_dataset_output("dataset1")
        temp_df = repo.get_dataset("plot")
        peaks = repo.get_peaks()
        plt.figure(3)
        plt.clf()

        # Plotting of all values
        plt.subplot(3, 1, 1)
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.plot(df['date'], df['value'], '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        plt.plot(df['date'][peaks['low_peaks']], temp_df['value'][peaks['low_peaks']], "xm",
                 label=dictionary_keywords.loc[51,selected_language]) #label for Abnormally low values  # Plotting of all peaks
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # y axis label - flowrate 
        plt.title(dictionary_keywords.loc[24,selected_language])#low values
        plt.legend()

        # Plot the differences in the values
        plt.subplot(3, 1, 2)
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.plot(df['date'], peaks['flow_PL'], "#6F8EAF", label=dictionary_keywords.loc[39,selected_language]) # plot label - difference 
        plt.plot(df['date'][peaks['low_peaks']], peaks['flow_PL'][peaks['low_peaks']], "^m",
                 label=dictionary_keywords.loc[51,selected_language]) #label for Abnormally low values
        plt.ylabel(dictionary_keywords.loc[39,selected_language]) # yaxis label - difference
        plt.legend()

        # Plot the slopes along with the threshold
        plt.subplot(3, 1, 3)
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.plot(df['date'], peaks['slopes_PL'], "#6F8EAF", label=dictionary_keywords.loc[38,selected_language]) # plot label - rate of change 
        plt.plot(df['date'][peaks['low_peaks']], peaks['slopes_PL'][peaks['low_peaks']], "^m",
                 label=dictionary_keywords.loc[51,selected_language]) #label for Abnormally low values
        plt.axhline(y=float(self.tPL.get()), linestyle="--", label="Threshold")
        plt.axhline(y=-float(self.tPL.get()), linestyle="--")
        plt.ylabel(dictionary_keywords.loc[38,selected_language]) # yaxis label - rate of change 
        plt.legend()

        plt.show()

    def G4(self):  # Patamares
        df = repo.get_dataset_output("dataset1")
        temp_df = repo.get_dataset("plot")
        peaks = repo.get_peaks()
        plt.figure(4)
        plt.clf()

        plt.plot(df['date'], df['value'], '#6F8EAF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        plt.plot(df['date'][peaks['flat_points']], temp_df['value'][peaks['flat_points']], "^g",
                 label=dictionary_keywords.loc[40,selected_language]) #Flat line values
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # y axis label - flowrate
        plt.title(dictionary_keywords.loc[25,selected_language]) #Flat lines title
        plt.legend()
        plt.show()

    def G5(self):  # Série sem falhas
        df = repo.get_dataset_output("dataset1")
        temp_df = repo.get_dataset("plot")
        peaks = repo.get_peaks()

        plt.figure(5)
        plt.cla()
        plt.plot(df['date'], df['value'], '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        plt.plot(df['date'][peaks['negative_peaks']], temp_df['value'][peaks['negative_peaks']], linestyle='None',
                 marker="x", color='#D95221', label=dictionary_keywords.loc[41,selected_language]) #negative
        plt.plot(df['date'][peaks['high_peaks']], temp_df['value'][peaks['high_peaks']], "xr", label=dictionary_keywords.loc[23,selected_language]) #Abnormally high values
        plt.plot(df['date'][peaks['low_peaks']], temp_df['value'][peaks['low_peaks']], "xm", label=dictionary_keywords.loc[24,selected_language])#Abnormally low values
        plt.plot(df['date'][peaks['flat_points']], temp_df['value'][peaks['flat_points']], "xg", label=dictionary_keywords.loc[44,selected_language]) #Values in flat line

        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.title(dictionary_keywords.loc[26,selected_language]) #Time series with identified anomalous values 
        plt.legend()
        plt.show()


class Tab2(tk.Frame):  # Imputação dos valores pontuais
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Preparacao da janela
        self.configure(background='white')  # Background

        # Preparação de uma grelha 100 x 100 (colunas x linhas) com grossura de 1
        for x in range(100):
            self.columnconfigure(x, weight=1)
        for x in range(100):
            self.rowconfigure(x, weight=1)

        # Separadores - linhas que dividem o programa
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=2, row=33, columnspan=97, sticky='ew')

        # Buttons
        self.Btn_Sep = tk.Button(self, text=dictionary_keywords.loc[52,selected_language], #Short-duration gap reconstruction
                                 command=self.upd_graph_nas_separated,
                                 font=NORMAL_FONT, relief=GROOVE).grid(column=92, row=5, rowspan=2, columnspan=6,
                                                                       sticky='NSWE')
        self.Btn_imputation = tk.Button(self, text=dictionary_keywords.loc[53,selected_language], #Long-duration gap reconstruction
                                        command=self.imputation,
                                        font=NORMAL_FONT, relief=GROOVE).grid(column=90, row=45, columnspan=9,
                                                                              sticky='NSWE')
        self.Btn_Next = tk.Button(self, text=dictionary_keywords.loc[16,selected_language], command=self.next_tab, #next
                                  font=NORMAL_FONT, relief=GROOVE).grid(row=90, column=92, columnspan=4,
                                                                        sticky='NSEW')
        # self.Btn_Help = tk.Button(self, text=dictionary_keywords.loc[13,selected_language], command='',
        #                           font=NORMAL_FONT, bg='yellow').grid(row=90, column=1, sticky='NSEW')

        # Threshold para separar falhas de curta e longa duração
        self.tNA = tk.Entry(self, textvariable=tk.StringVar(self, None), justify='center')
        self.tNA.grid(column=95, row=3, columnspan=5, sticky='NS')

        # Combobox para os diferentes tipos de imputação
        self.imputation_box = ttk.Combobox(self, textvariable=tk.StringVar())
        self.imputation_box['values'] = (dictionary_keywords.loc[54,selected_language], #linear interpolation
                                         dictionary_keywords.loc[55,selected_language], #Polynomial interpolation
                                         'Back Fill',
                                         'Front Fill')
        self.imputation_box.grid(column=95, row=40, columnspan=5, sticky='NS')
        self.imputation_box.current(2)

        # Funcoes dos gráficos em branco
        self.graph_original()
        self.table_info_nan()
        self.graph_nas_separated_original()
        self.table_nas_separated_original()
        self.final_graph_original()
        self.table_inputation_original()

    def menubar(self, root):  # Menu, igual ao Tab 1, só muda os gráficos a visualizar (WIP)
        menubar = tk.Menu(root)
        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label=dictionary_keywords.loc[5,selected_language], command=lambda: root.file_input(Tab2))
        fileMenu.add_command(label=dictionary_keywords.loc[18,selected_language], command=self.clear) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[101,selected_language], command=lambda: root.clear_all()) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[19,selected_language], command=lambda: file_output("dataset2")) #export data
        fileMenu.add_separator()
        fileMenu.add_command(label=dictionary_keywords.loc[6,selected_language], command=self.quit)
        menubar.add_cascade(label=dictionary_keywords.loc[7,selected_language], menu=fileMenu)

        methodMenu = tk.Menu(menubar, tearoff=False)
        methodMenu.add_command(label=dictionary_keywords.loc[8,selected_language], #Anomaly identification and removal
                                command=lambda: root.show_frame(Tab1, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[9,selected_language], #Short-duration gap reconstruction
                               command=lambda: root.show_frame(Tab2, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[10,selected_language], command=lambda: root.show_frame(Tab3, from_menu=True)) #time step normalization
        methodMenu.add_command(label=dictionary_keywords.loc[11,selected_language], command=lambda: root.show_frame(Tab4, from_menu=True))
        menubar.add_cascade(label=dictionary_keywords.loc[12,selected_language], menu=methodMenu) #tools

        graphMenu = tk.Menu(menubar, tearoff=False)  # Gráficos de visualização
        graphMenu.add_command(label=dictionary_keywords.loc[22,selected_language], command=self.G1) #original serie
        graphMenu.add_command(label=dictionary_keywords.loc[56,selected_language], command=self.G2)#label for Time series with identified short and long duration gaps 
        graphMenu.add_command(label=dictionary_keywords.loc[57,selected_language], command=self.G3)#label for Time series with reconstructed short duration gaps
        menubar.add_cascade(label=dictionary_keywords.loc[27,selected_language], menu=graphMenu) #show graphs

        helpMenu = tk.Menu(menubar, tearoff=False)
        helpMenu.add_command(label=dictionary_keywords.loc[97,selected_language], command=lambda: manual(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[103,selected_language], command=lambda: research_paper(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[14,selected_language], command=lambda: about_dsc(dictionary_keywords, selected_language)) #about
        menubar.add_cascade(label=dictionary_keywords.loc[13,selected_language], menu=helpMenu)

        return menubar

    def tab_functions(self):  # Funcoes iniciais do separador
        df = repo.get_dataset("dataset2")
        values = df['value']
        dates = df['date']

        self.upd_graph_original(values, dates)
        self.upd_table_info_nan(values, dates)
        self.graph_nas_separated_original()
        self.final_graph_original()

        for x in range(2):
            tk.Label(self, text='', bg='white').grid(column=95, row=14 + x, columnspan=5, sticky='NSWE')
        plt.close('all')

    def clear(self):  # Para limpar todos os dados e gráficos
        repo.set_dataset("dataset2", None)
        repo.set_values_tab2(None, None)

        self.graph_original()
        self.table_info_nan()
        self.graph_nas_separated_original()
        self.final_graph_original()
        for x in range(2):
            tk.Label(self, text='', bg='white').grid(column=95, row=1 + x, columnspan=5, sticky='NSWE')

        for x in range(2):
            tk.Label(self, text='', bg='white').grid(column=95, row=14 + x, columnspan=5, sticky='NSWE')

        self.tNA.delete(0, "end")
        plt.close('all')

    def next_tab(self):  # Botão avançar
        # O que sai dos métodos é colocado no dataset de saída
        # E no de entrada para ser usado no método (Separador) seguinte
        repo.set_dataset("dataset3", repo.get_dataset_output("dataset2"))
        app.show_frame(Tab3)  # Muda de separador

    def graph_original(self):  # Série de input
        self.fig = Figure(figsize=(1, 1), dpi=50)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(dictionary_keywords.loc[22,selected_language]) #original serie

        self.ax.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                     ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax.legend()
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 

        FigureCanvasTkAgg(self.fig, master=self).get_tk_widget().grid(
            column=0, row=0, columnspan=90, rowspan=10, sticky='NSEW')

    def upd_graph_original(self, values, dates):  # Atualiza Gráfico original
        # Obter lista com index de nan's
        nans = []
        for i in range(len(values)):
            line = float(values[i])
            if math.isnan(line):
                nans.append(i)

        repo.set_values_tab2(nans, None)
        # clean graph
        self.ax.cla()

        # Gráfico original
        self.ax.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values

        if len(nans) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in dates[nans]:
                self.ax.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
            self.ax.axvline(x=i, color='k', linestyle='--', linewidth=0.3, label=dictionary_keywords.loc[58,selected_language], marker='|') #Label for gaps
        # formata o  grafico
        # self.ax.xaxis.set_major_formatter(self.date_form)
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax.set_title(dictionary_keywords.loc[22,selected_language]) #original serie
        self.ax.legend()
        self.fig.canvas.draw()

    def table_info_nan(self):  # Tabela de contagem de falhas e medicoes, bem como quantos segundos para dividir os tipos
        #count:
        tk.Label(self, text=dictionary_keywords.loc[59,selected_language], bg='white',
                 font=NORMAL_FONT).grid(column=95, row=0, columnspan=5, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[60,selected_language], bg='white',  # measurments Número de medições
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=1, columnspan=5, sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[61,selected_language], bg='white',  # Measurements within gaps / Número de Falhas
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=2, columnspan=5, sticky='NSWE')
        tk.Label(self, text="Threshold (s)", bg='white',  # Threshold para identificar tipos de falha
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=3, columnspan=5, sticky='NSWE')

    def upd_table_info_nan(self, values, dates):  # Atualiza gráfico
        nans = repo.get_values_tab2()['nans']

        tk.Label(self, text=len(values), bg='white').grid(column=95, row=1, columnspan=5, sticky='NSWE')
        tk.Label(self, text=len(nans), bg='white').grid(column=95, row=2, columnspan=5, sticky='NSWE')

        # Para obter a mediana do espaçamento
        time_spacing = np.zeros(len(values) - 1)

        # Espacamento temporal
        for line in range(1, len(values), 1):
            # Conversao ns para s
            time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))

        time_spacing = pd.DataFrame(time_spacing)
        self.spacing_detail = time_spacing.describe()  # Estatisticas do espacamento

        # Preenche a entry
        self.tNA.delete(0, "end")
        if int(self.spacing_detail[0][5]) > 900:
            self.tNA.insert(0, int(self.spacing_detail[0][5] * 3.5))
        else:
            self.tNA.insert(0, 900)
        repo.set_values_tab2(nans, time_spacing)

    def graph_nas_separated_original(self):  # Gráfico de onde estao os nan
        self.fig2 = Figure(figsize=(1, 1), dpi=50)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_title(dictionary_keywords.loc[56,selected_language]) #title for Time series with identified short and long duration gaps 
        # we plot y as a function of a, which parametrizes x
        self.ax2.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                      ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax2.legend()
        self.ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 

        FigureCanvasTkAgg(self.fig2, master=self).get_tk_widget().grid(
            column=0, row=10, columnspan=90, rowspan=20, sticky='NSEW')

    def upd_graph_nas_separated(self):  # Atualiza o gráfico dos nan
        df = repo.get_dataset("dataset2").to_numpy()
        values = [float(i[1]) for i in df]
        dates = [i[0].to_pydatetime() for i in df]

        dates = np.array(dates)
        values = np.array(values)

        self.ax2.cla()
        self.ax2.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values

        # self.ax2.xaxis.set_major_formatter(self.date_form)
        self.ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax2.set_title(dictionary_keywords.loc[56,selected_language]) #title for Time series with identified short and long duration gaps 
        self.ax2.legend()

        # GET NANS
        falhas_grandes = 0
        falhas_pequenas = 0
        nans = []

        # array com ID's dos nans
        for row in range(len(values)):
            if np.isnan(values[row]):
                nans.append(row)

        self.set_nans_long = []  # ids de nans pertencentes a falhas curtas
        self.set_nans_short = []  # ids de nans pertencentes a falhas longas
        self.set_nans = []  # lista de listas de nan consecutivos

        # Separo o array em multiplos arrays de nans consecutivos
        for k, g in groupby(enumerate(nans), lambda i_x: i_x[0] - i_x[1]):
            row = list(map(itemgetter(1), g))  # Cada minisérie de nans
            self.set_nans.append(row)

        # Para cada set de nans, avalia se o tempo entre a leitura anterior à 1º e depois da ultima é inferior a tsh
        for row in self.set_nans:
            last_date = datetime.datetime.now()
            if row[0] == 0:
                first_date = row[0]
                first_date = dates[first_date]
            else:
                first_date = row[0]
                first_date = dates[first_date - 1]
            if row[-1]:
                last_date = row[-1]
                last_date = dates[last_date]

            # difference btween first and last
            diff = (last_date - first_date).total_seconds()

            if diff > int(self.tNA.get()):  # Pinto de verde (Curto) ou vermelho (Longo), consoante o thsold
                falhas_grandes += 1
                self.set_nans_long.append(row)

                for i in range(len(row)):
                    self.ax2.axvline(x=dates[row[i]], color='r', linestyle='--', linewidth=0.3)  # Falhas longas
            else:
                self.set_nans_short.append(row)

                falhas_pequenas += 1
                for i in range(len(row)):
                    self.ax2.axvline(x=dates[row[i]], color='g', linestyle='--', linewidth=0.3)  # Falhas Curtas

        # tab2_values = repo.get_values_tab2()

        # for i in range(len(tab2_values['time_spacing'][0])):
        #     if int(tab2_values['time_spacing'][0][i]) > int(self.tNA.get()) and math.isnan(values[i]) is not True:
        #         self.ax2.axvline(x=dates[i], color='#000000', linestyle='--', linewidth=0.3)  # Falhas Curtas
        #         self.ax2.axvline(x=dates[i+1], color='#000000', linestyle='--', linewidth=0.3)  # Falhas Curtas
        # 1 lista de ptos de falha curta
        self.set_nans_short = [item for sublist in self.set_nans_short for item in sublist]

        self.set_nans_long = [item for sublist in self.set_nans_long for item in sublist]
        self.fig2.canvas.draw()

        self.upd_table_nas_separated(falhas_grandes, falhas_pequenas)
        plt.close(2)
        plt.close(3)
        self.final_graph_original()  # (para limpar o graph final)

    def table_nas_separated_original(self):  # Tabela de contagens de nans
        #count:
        tk.Label(self, text=dictionary_keywords.loc[59,selected_language], bg='white', font=NORMAL_FONT).grid(column=95, row=13, columnspan=5,
                                                                           sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[62,selected_language], bg='white', font=NORMAL_FONT, anchor='e',
                 fg='green').grid(column=90, row=14, columnspan=5, sticky='NSWE') #short duration gaps
        tk.Label(self, text=dictionary_keywords.loc[63,selected_language], bg='white', font=NORMAL_FONT, anchor='e', fg='red').grid(
            column=90, row=15, columnspan=5, sticky='NSWE') #Label for long duration gaps reconstructed
        # tk.Label(self, text="Períodos sem leitura", bg='white', font=NORMAL_FONT, anchor='e',fg='#000000').grid(column=90, row=16, columnspan=5, sticky='NSWE')

    def upd_table_nas_separated(self, falhas_grandes, falhas_pequenas):  # Atualiza tabela de nans
        # tab2_values = repo.get_values_tab2()
        # df = repo.get_dataset("dataset2")
        # values = df['value']

        # count = 0
        # for i, j in enumerate(tab2_values['time_spacing'][0]):
        #     if int(j) > int(self.tNA.get()) and math.isnan(values[i]) is not True:
        #        count += 1

        tk.Label(self, text=falhas_pequenas, bg='white', font=NORMAL_FONT, fg='green').grid(column=95, row=14,
                                                                                            columnspan=5, sticky='NSWE')
        tk.Label(self, text=falhas_grandes, bg='white',
                 font=NORMAL_FONT, fg='red').grid(column=95, row=15, columnspan=5, sticky='NSWE')
        # tk.Label(self, text=count, bg='white',
        #          font=NORMAL_FONT, fg='#000000').grid(column=95, row=16, columnspan=5, sticky='NSWE')

    def final_graph_original(self):  # Gráfico com falhas curtas preenchidas
        self.fig3 = Figure(figsize=(1, 1), dpi=50)
        self.ax3 = self.fig3.add_subplot(111)
        self.ax3.set_title(dictionary_keywords.loc[57,selected_language]) #title for Time series with reconstructed short duration gaps 
        # we plot y as a function of a, which parametrizes x
        self.ax3.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                      ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax3.legend()
        self.ax3.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 

        FigureCanvasTkAgg(self.fig3, master=self).get_tk_widget().grid(
            column=0, row=34, columnspan=90, rowspan=66, sticky='NSEW')

    def upd_final_graph(self):  # Atualiza gráfico final com falhas curtas imputadas
        self.ax3.cla()
        df = repo.get_dataset("dataset2").copy()

        values = [float(i[1]) for i in df.values]
        dates = [i[0].to_pydatetime() for i in df.values]

        dates = np.array(dates)
        values = np.array(values)

        for row in range(len(self.set_nans_short)):
            df['value'][self.set_nans_short[row]] = self.reconstructedData['value'][self.set_nans_short[row]]

        self.ax3.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax3.plot(dates[self.set_nans_short], self.reconstructedData['value'][self.set_nans_short],
                      "^g", label=dictionary_keywords.loc[62,selected_language]) #Label for short duration gaps reconstructed

        if len(self.set_nans_long) > 0:
            i = 0
            for i in range(len(self.set_nans_long)):
                self.ax3.axvline(x=dates[self.set_nans_long[i]], color='r', linestyle='--', linewidth=0.3)
            self.ax3.axvline(x=dates[self.set_nans_long[i]], color='r', linestyle='--', linewidth=0.3,
                             label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed

        # format graph
        self.ax3.xaxis.set_major_formatter(DATE_FORM)
        self.ax3.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax3.set_title(dictionary_keywords.loc[57,selected_language]) #title for Time series with reconstructed short duration gaps 
        self.ax3.legend()
        self.fig3.canvas.draw()

        return df

    def table_inputation_original(self):  # Metodos de imputacao a escolher
        tk.Label(self, text=dictionary_keywords.loc[64,selected_language], bg='white', font=NORMAL_FONT,
                 anchor='e', fg='black', wraplength=150).grid(column=90, row=40, columnspan=5, sticky='NSWE') #reconstruction method for short gaps

    def imputation(self):  # Métodos de imputacao a aplicar
        df = repo.get_dataset("dataset2").copy()
        df = df.set_index(list(df)[0])

        imputation_option = self.imputation_box.get()
        self.reconstructedData = None

        if imputation_option == dictionary_keywords.loc[54,selected_language]: #linear interpolation
            self.reconstructedData = df.astype(float).interpolate(method='linear')

        elif imputation_option == dictionary_keywords.loc[55,selected_language]: #Polynomial interpolation
            self.reconstructedData = df.astype(float).interpolate(method='polynomial', order=2)

        elif imputation_option == 'Back Fill':
            self.reconstructedData = df.fillna(method='backfill')

        elif imputation_option == 'Front Fill':
            self.reconstructedData = df.fillna(method='ffill')

        self.reconstructedData.reset_index(level=0, inplace=True)
        df_imputed = self.upd_final_graph()
        repo.set_dataset_output("dataset2", df_imputed)
        plt.close(3)

        # plt.close('all')#Apaga as imagens para não ficarmos com uma figura diferente da que está a ser apresentada na janela principal

    # Gráficos externos
    def G1(self):  # Série original com na identificados
        df = repo.get_dataset("dataset2")
        tab2_values = repo.get_values_tab2()
        nans = tab2_values['nans']
        plt.figure(1)
        plt.cla()
        plt.plot(df['date'], df['value'], '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        if len(nans) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in df['date'][nans]:
                plt.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
            plt.axvline(x=i, color='k', linestyle='--', linewidth=0.5, label=dictionary_keywords.loc[58,selected_language], marker='|') #Label for gaps
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.title(dictionary_keywords.loc[22,selected_language]) #original serie
        plt.legend()
        plt.show()

    def G2(self):  # Série original com Na's identificados como de curta ou longa duração
        try:
            df = repo.get_dataset("dataset2").to_numpy()
            values = [float(i[1]) for i in df]
            dates = [i[0].to_pydatetime() for i in df]

            dates = np.array(dates)
            values = np.array(values)

            # df = repo.get_dataset("dataset3")
            # dates = [i.to_pydatetime() for i in df['date'].to_numpy()]
            # dates = np.array(dates)

            plt.figure(2)
            plt.cla()
            plt.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values

            for row in self.set_nans:
                last_date = datetime.datetime.now()
                if row[0] == 0:
                    first_date = row[0]
                    first_date = dates[first_date]
                else:
                    first_date = row[0]
                    first_date = dates[first_date - 1]
                if row[-1]:
                    last_date = row[-1]
                    last_date = dates[last_date]

                # difference btween first and last
                diff = (last_date - first_date).total_seconds()

                if diff > int(self.tNA.get()):  # Pinto de verde ou vermelho, consoante o thsold
                    for i in range(len(row)):
                        plt.axvline(x=dates[row[i]], color='r', linestyle='--', linewidth=0.3)
                else:
                    for i in range(len(row)):
                        plt.axvline(x=dates[row[i]], color='g', linestyle='--', linewidth=0.3)

                    # tab2_values = repo.get_values_tab2()

                    # for i in range(len(tab2_values['time_spacing'][0])):
                    #     if int(tab2_values['time_spacing'][0][i]) > int(self.tNA.get()) and math.isnan(values[i]) is not True:
                    self.ax2.axvline(x=dates[i], color='#000000', linestyle='--', linewidth=0.3)  # Falhas Curtas
                    self.ax2.axvline(x=dates[i + 1], color='#000000', linestyle='--', linewidth=0.3)  # Falhas Curtas
            plt.title(dictionary_keywords.loc[56,selected_language]) #title for Time series with identified short and long duration gaps 
            plt.gca().xaxis.set_major_formatter(DATE_FORM)
            plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
            plt.legend()
            plt.show()
        except AttributeError:
            plt.cla()
            fig2 = Figure(figsize=(1, 1), dpi=50)
            ax2 = fig2.add_subplot(111)
            ax2.set_title(dictionary_keywords.loc[56,selected_language]) #title for Time series with identified short and long duration gaps 
            # we plot y as a function of a, which parametrizes x
            ax2.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                     ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
            ax2.legend()
            ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
            plt.show()

    def G3(self):  # série original com valores imputados e identificação de falhas de longa duração
        try:
            df = repo.get_dataset("dataset2").copy()

            values = [float(i[1]) for i in df.values]
            dates = [i[0].to_pydatetime() for i in df.values]

            dates = np.array(dates)
            values = np.array(values)

            plt.figure(3)
            plt.cla()
            for row in range(len(self.set_nans_short)):
                df['value'][self.set_nans_short[row]] = self.reconstructedData['value'][self.set_nans_short[row]]

            plt.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
            plt.plot(dates[self.set_nans_short], self.reconstructedData['value'][self.set_nans_short], "^g",
                     label=dictionary_keywords.loc[62,selected_language]) #Label for short duration gaps reconstructed

            if len(self.set_nans_long) > 0:
                i = 0
                for i in range(len(self.set_nans_long)):
                    plt.axvline(x=dates[self.set_nans_long[i]], color='r', linestyle='--', linewidth=0.3)
                plt.axvline(x=dates[self.set_nans_long[i]], color='r', linestyle='--', linewidth=0.3,
                            label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed

            # format graph
            plt.gca().xaxis.set_major_formatter(DATE_FORM)

            plt.title(dictionary_keywords.loc[57,selected_language]) #title for Time series with reconstructed short duration gaps 
            plt.gca().xaxis.set_major_formatter(DATE_FORM)
            plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
            plt.legend()
            plt.show()
        except AttributeError:
            pass


class Tab3(tk.Frame):  # Normalização temporal
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Preparacao da janela
        self.configure(background='white')  # Background

        # Todas as colunas e rows tem weight de 1 e cria uma matrix de 100 x 100
        for x in range(100):
            self.columnconfigure((x), weight=1)
        for x in range(100):
            self.rowconfigure((x), weight=1)

        # Separadores - linhas que dividem o programa
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            column=2, row=32, columnspan=97, sticky='ew')

        # Buttons
           #To Create uniform spacing and identify periods without measurements:
        self.Btn_Sep = tk.Button(self, text=dictionary_keywords.loc[66,selected_language],
                                 command=self.upd_graph_uniform_spacing,
                                 font=NORMAL_FONT, relief=GROOVE, wraplength=250).grid(column=92, row=11, columnspan=6,
                                                                                       sticky='NSWE')
            #to create uniform spacing:
        self.Btn_Spacing = tk.Button(self, text=dictionary_keywords.loc[67,selected_language],
                                     command=self.normalization_blocks, font=NORMAL_FONT, relief=GROOVE).grid(column=92,
                                                                                                              row=35,
                                                                                                              columnspan=6,
                                                                                                              sticky='NSWE')
            #next button    
        self.Btn_Next = tk.Button(self, text=dictionary_keywords.loc[16,selected_language], command=self.next_tab,
                                  font=NORMAL_FONT, relief=GROOVE).grid(row=90, column=93, columnspan=4,
                                                                        sticky='NSEW')


        # entry for thsold NA
        self.tNA = tk.Entry(self, textvariable=tk.StringVar(self, None), justify='center')
        self.tNA.grid(column=95, row=3, columnspan=5, sticky='NS')

        self.tPL = tk.Entry(self, textvariable=tk.StringVar(self, None), justify='center')
        self.tPL.grid(column=95, row=5, columnspan=5, sticky='NS')

        self.table_uniform_spacing()
        self.graph_original()
        self.table_info_nan()
        self.graph_uniform_spacing_original()
        self.final_graph_original()

    def menubar(self, root):  # Menu igual ao Tab1 e Tab2, mudando os gráficos
        menubar = tk.Menu(root)
        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label=dictionary_keywords.loc[5,selected_language], command=lambda: root.file_input(Tab3))
        fileMenu.add_command(label=dictionary_keywords.loc[18,selected_language], command=self.clear) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[101,selected_language], command=lambda: root.clear_all()) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[19,selected_language], command=lambda: file_output("dataset3"))#export data
        fileMenu.add_separator()
        fileMenu.add_command(label=dictionary_keywords.loc[6,selected_language], command=self.quit)
        menubar.add_cascade(label=dictionary_keywords.loc[7,selected_language], menu=fileMenu)

        methodMenu = tk.Menu(menubar, tearoff=False)
        methodMenu.add_command(label=dictionary_keywords.loc[8,selected_language], #Anomaly identification and removal
                                command=lambda: root.show_frame(Tab1, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[9,selected_language], #Short-duration gap reconstruction
                               command=lambda: root.show_frame(Tab2, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[10,selected_language], command=lambda: root.show_frame(Tab3, from_menu=True)) #time step normalization
        methodMenu.add_command(label=dictionary_keywords.loc[11,selected_language], command=lambda: root.show_frame(Tab4, from_menu=True))
        menubar.add_cascade(label=dictionary_keywords.loc[12,selected_language], menu=methodMenu) #tools

        graphMenu = tk.Menu(menubar, tearoff=False)  # Gráficos de visualização
        graphMenu.add_command(label=dictionary_keywords.loc[22,selected_language], command=self.G1) #original serie
        graphMenu.add_command(label=dictionary_keywords.loc[56,selected_language], command=self.G2)#label for Time series with identified short and long duration gaps 
        graphMenu.add_command(label=dictionary_keywords.loc[57,selected_language] , command=self.G3) #label for Time series with reconstructed short duration gaps
        menubar.add_cascade(label=dictionary_keywords.loc[27,selected_language], menu=graphMenu) #show graphs

        helpMenu = tk.Menu(menubar, tearoff=False)
        helpMenu.add_command(label=dictionary_keywords.loc[97,selected_language], command=lambda: manual(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[103,selected_language], command=lambda: research_paper(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[14,selected_language], command=lambda: about_dsc(dictionary_keywords, selected_language))#about

        menubar.add_cascade(label=dictionary_keywords.loc[13,selected_language], menu=helpMenu)

        return menubar

    def next_tab(self):  # Botão avançar
        # O que sai dos métodos é colocado no dataset de saída
        # E no de entrada para ser usado no método (Separador) seguinte
        repo.set_dataset("dataset4", repo.get_dataset_output("dataset3"))
        app.show_frame(Tab4)  # Muda de separador

    def tab_functions(self):
        plt.close('all')
        df = repo.get_dataset("dataset3")
        values = df['value']
        dates = df['date']
        self.upd_graph_original(values, dates)
        self.upd_table_info_nan(df)
        self.graph_uniform_spacing_original()
        self.final_graph_original()

    def clear(self):  # Limpa os dados e gráficos
        repo.set_dataset("dataset3", None)
        self.graph_original()
        self.table_info_nan()
        self.graph_uniform_spacing_original()
        self.final_graph_original()
        for x in range(2):
            tk.Label(self, text='', bg='white').grid(column=95, row=1 + x, columnspan=5, sticky='NSWE')

        tk.Label(self, text='', bg='white').grid(column=95, row=15, columnspan=5, sticky='NSWE')

        self.tNA.delete(0, "end")
        self.tPL.delete(0, "end")

    """ Ver round times se nao sao iguais"""

    def round_time(self, dt=None, date_delta=datetime.timedelta(seconds=60), to='average'):
        """
        Round a datetime object to a multiple of a timedelta
        dt : datetime.datetime object, default now.
        dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
        from:  http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
        """
        round_to = date_delta.total_seconds()
        if dt is None:
            dt = datetime.datetime.now()
        seconds = (dt - dt.min).seconds

        if seconds % round_to == 0 and dt.microsecond == 0:
            rounding = (seconds + round_to / 2) // round_to * round_to
        else:
            if to == 'up':
                # // is a floor division, not a comment on following line (like in javascript):
                rounding = (seconds + dt.microsecond / 1000000 + round_to) // round_to * round_to
            elif to == 'down':
                rounding = seconds // round_to * round_to
            else:
                rounding = (seconds + round_to / 2) // round_to * round_to

        return dt + datetime.timedelta(0, rounding - seconds, - dt.microsecond)

    def roundTime(self, dt=None, roundTo=900):
        """Round a datetime object to any time lapse in seconds
        dt : datetime.datetime object, default now.
        roundTo : Closest number of seconds to round to, default 1 minute.
        Author: Thierry Husson 2012 - Use it as you want but don't blame me.
        """
        if dt == None:
            dt = datetime.datetime.now()
        seconds = (dt.replace(tzinfo=None) - dt.min).seconds
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        return dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)

    """----------------------------------"""

    def group_runs(self, li, tolerance=1):  # DBocos de dados disponiveis para normalizar temporalmente
        out = []
        last = li[0]
        for x in li:
            if x - last > tolerance:
                yield out
                out = []
            out.append(x)
            last = x
        yield out

    # def custom_resample(self, ts):
    #
    #     ts = integrate.simps(ts, even='avg')
    #
    #     return ts

    def graph_original(self):  # Série original

        self.fig = Figure(figsize=(1, 1), dpi=50)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(dictionary_keywords.loc[22,selected_language]) #original serie
        # we plot y as a function of a, which parametrizes x
        self.ax.plot(['00:00:00', '06:00:00',
                      '12:00:00', '18:00:00', '24:00:00'], ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax.legend()
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # y axis label - flowrate

        FigureCanvasTkAgg(self.fig, master=self).get_tk_widget().grid(
            column=0, row=0, columnspan=90, rowspan=10, sticky='NSEW')

    def upd_graph_original(self, values, dates):  # Atualizacao da série original
        # Obter lista com index de nan's
        self.nan = []
        for i in range(len(values)):
            line = float(values[i])
            if math.isnan(line):
                self.nan.append(i)

        self.nan_val = []
        for i in range(len(self.nan)):
            self.nan_val.append(values.idxmin())

        self.ax.cla()
        self.ax.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values

        if len(self.nan) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in dates[self.nan]:
                self.vline = self.ax.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
            self.vline = self.ax.axvline(x=i, color='k', linestyle='--', linewidth=0.5, label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed

        # format graph
        self.ax.xaxis.set_major_formatter(DATE_FORM)
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate  
        self.ax.set_title(dictionary_keywords.loc[22,selected_language]) #original serie
        self.ax.legend()

        self.fig.canvas.draw()

    def table_info_nan(self):  # Tabela de medicoes e falhas
        #count:
        tk.Label(self, text=dictionary_keywords.loc[59,selected_language], bg='white',
                 font=NORMAL_FONT).grid(column=95, row=0, columnspan=5, sticky='NSWE')

        #Measurments:
        tk.Label(self, text=dictionary_keywords.loc[60,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=1, columnspan=5, sticky='NSWE')
        
        #Measurements within gaps:
        tk.Label(self, text=dictionary_keywords.loc[61,selected_language], bg='white', 
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=2, columnspan=5, sticky='NSWE')
        #desired spacing label:
        tk.Label(self, text=dictionary_keywords.loc[68,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=3, columnspan=5, sticky='NSWE')

        #Minimum duration of long period without measurements (s):
        tk.Label(self, text=dictionary_keywords.loc[69,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=5, columnspan=5, sticky='NSWE')

    def upd_table_info_nan(self, df):  # Atualiza a tabela de medicoes
        tk.Label(self, text=df.shape[0], bg='white').grid(column=95, row=1, columnspan=5, sticky='NSWE')
        tk.Label(self, text=len(self.nan_val), bg='white').grid(column=95, row=2, columnspan=5, sticky='NSWE')

        # Preenche a entry
        self.tNA.delete(0, "end")
        self.tNA.insert(0, 900)

        self.tPL.delete(0, "end")
        self.tPL.insert(0, 900)

    def graph_uniform_spacing_original(self):  # Gráfico da previsao do espacamento normalizado

        self.fig2 = Figure(figsize=(1, 1), dpi=50)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_title(dictionary_keywords.loc[70,selected_language]) # title of Time series with identification of uniform spacing 

        self.ax2.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                      ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax2.legend()
        self.ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 

        FigureCanvasTkAgg(self.fig2, master=self).get_tk_widget().grid(column=0, row=10,
                                                                       columnspan=90, rowspan=20, sticky='NSEW')
 
    def upd_graph_uniform_spacing(self):  # Atualiza gráfico do espacamento temporal
        df = repo.get_dataset("dataset3").to_numpy()
        values = [float(i[1]) for i in df]
        dates = [i[0].to_pydatetime() for i in df]

        dates = np.array(dates)
        values = np.array(values)

        self.ax2.cla()
        self.ax2.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values

        # format graph
        self.ax2.xaxis.set_major_formatter(DATE_FORM)
        self.ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax2.set_title(dictionary_keywords.loc[70,selected_language]) # title of Time series with identification of uniform spacing 

        # Plot da 'mancha' de falha com a legenda
        i = 0
        for i in dates[self.nan]:
            self.vline = self.ax2.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
        if len(self.nan) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            self.vline = self.ax2.axvline(x=i, color='k', linestyle='--', linewidth=0.3, label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed

        # Plot das linhas verticais com espaçamento uniforme
        dates_regular = pd.date_range(
            self.roundTime(dt=dates[0]) + datetime.timedelta(seconds=float(int(self.tNA.get()) / 2)),
            self.roundTime(dt=dates[-1]) - datetime.timedelta(seconds=float(int(self.tNA.get()) / 2)),
            freq=str(self.tNA.get()) + 's')  # obtem espaçamentos uniformes, certos com a hora
        for i in dates_regular:
            self.vline = self.ax2.axvline(x=i, color='r', linestyle='--', linewidth=0.3)
        self.vline = self.ax2.axvline(x=i, color='r', linestyle='--', linewidth=0.3, label=dictionary_keywords.loc[71,selected_language],
                                      marker='|') #uniform spacing

        ##Plot das linhas associadas ao periodo sem medição
        # Para obter a mediana do espaçamento
        df = repo.get_dataset("dataset3")
        values = df['value']
        dates = df['date']
        time_spacing = np.zeros(len(values) - 1)
        # Espacamento temporal
        for line in range(1, len(values), 1):
            # Conversao ns para s
            time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))
        time_spacing = pd.DataFrame(time_spacing)
        spacing_detail = time_spacing.describe()
        count = 0
        for i, j in enumerate(time_spacing[0]):
            if int(j) > int(self.tPL.get()) and math.isnan(values[i]) is not True:
                count += 1

        check = None
        for i in range(len(time_spacing[0])):
            if int(time_spacing[0][i]) > int(self.tPL.get()) and math.isnan(values[i]) is not True:
                self.vline = self.ax2.axvline(x=dates[i], color='indigo', linestyle='--', linewidth=1)  # Falhas Curtas
                self.vline = self.ax2.axvline(x=dates[i + 1], color='indigo', linestyle='--',
                                              linewidth=1)  # Falhas Curtas
                check = True
                lst_vlue = i
        if check:
            self.vline = self.ax2.axvline(x=dates[lst_vlue], color='indigo', linestyle='--', linewidth=1,
                                          label=dictionary_keywords.loc[72,selected_language],
                                          marker='|')  # Falhas Curtas and period without measurment

        plt.close(2)
        plt.close(3)
        self.upd_table_uniform_spacing()

        self.ax2.legend()
        self.fig2.canvas.draw()

    def table_uniform_spacing(self):  # Tabela com informações sobre o processo de normalização temporal
        #count:
        tk.Label(self, text=dictionary_keywords.loc[59,selected_language], bg='white',
                 font=NORMAL_FONT).grid(column=95, row=14, columnspan=5, sticky='NSWE')

        #label of periods without measurments:         
        tk.Label(self, text=dictionary_keywords.loc[73,selected_language], bg='white',
                 font=NORMAL_FONT, anchor='e').grid(column=90, row=15, columnspan=5, sticky='NSWE')

    def upd_table_uniform_spacing(self):  # Tabela com informações sobre o processo de normalização temporal
        ##Plot das linhas associadas ao periodo sem medição
        # Para obter a mediana do espaçamento
        df = repo.get_dataset("dataset3")
        values = df['value']
        dates = df['date']
        time_spacing = np.zeros(len(values) - 1)
        # Espacamento temporal
        for line in range(1, len(values), 1):
            # Conversao ns para s
            time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))
        time_spacing = pd.DataFrame(time_spacing)

        count = 0
        for i, j in enumerate(time_spacing[0]):
            if int(j) > int(self.tPL.get()) and math.isnan(values[i]) is not True:
                count += 1

        tk.Label(self, text=count, bg='white', fg='#000000').grid(column=95, row=15, columnspan=5, sticky='NSWE')

    def final_graph_original(self):  # Gráfico final com a normalizacao feita
        self.fig3 = Figure(figsize=(1, 1), dpi=50)
        self.ax3 = self.fig3.add_subplot(111)
        self.ax3.set_title(dictionary_keywords.loc[56,selected_language]) #title for Time series with identified short and long duration gaps 
        # we plot y as a function of a, which parametrizes x
        self.ax3.plot(['00:00:00', '06:00:00', '12:00:00', '18:00:00', '24:00:00'],
                      ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax3.legend()
        self.ax3.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate

        FigureCanvasTkAgg(self.fig3, master=self).get_tk_widget().grid(column=0, row=33,
                                                                       columnspan=90, rowspan=67, sticky='NSEW')

    def normalization_blocks(self):  # para simplificar a normalizacao é dividido em blocos de medicoes
        df = repo.get_dataset("dataset3")
        values = df['value']
        dates = df['date']
        time_spacing = np.zeros(len(values) - 1)
        ts_index = []
        # Espacamento temporal
        for line in range(1, len(values), 1):
            # Conversao ns para s
            time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))
            if time_spacing[line - 1] > int(self.tPL.get()) and math.isnan(values[line]) is not True:
                ts_index.append(line)  # Guardar os index das medições pertencentes a um PL
                ts_index.append(line + 1)
        time_spacing = pd.DataFrame(time_spacing)

        # Obter lista com index de medições sem nan's
        value_list = []
        for i in range(df.shape[0]):
            line = float(df['value'][i])
            if math.isnan(line) is False:
                value_list.append(i)

        # Retirar os ids de medições associadas a um PL
        value_list = list(filter(lambda x: x not in ts_index, value_list))

        # transformo a lista numa lista de listas com os blocos de dados disponiveis para normalizar temporalmente
        value_set = list(self.group_runs(value_list))

        normal_df = []
        count = 0
        while count < len(value_set):
            subset = value_set[count]
            # print((df.loc[subset[-1]]['date'] - df.loc[subset[0]]['date']).seconds, 2 * int(self.tPL.get()), (df.loc[subset[-1]]['date'] - df.loc[subset[0]]['date']).seconds < 2 * int(self.tPL.get()))
            if (df.loc[subset[-1]]['date'] - df.loc[subset[0]]['date']).value * 10**-9 < 2 * int(self.tPL.get()):
                delta = (df.loc[subset[-1]]['date'] - df.loc[subset[0]]['date'])
                value_set.remove(subset)
                # print("\t", (df.loc[subset[-1]]['date'] - df.loc[subset[0]]['date']).seconds, 2 * int(self.tPL.get()), (df.loc[subset[-1]]['date'] - df.loc[subset[0]]['date']).seconds < 2 * int(self.tPL.get()))
            else:
                set_df = pd.DataFrame(data=df.loc[subset])
                normal_df.append(self.normalization(set_df))
                count += 1

        normal_df = pd.concat(normal_df).reset_index()

        horas = pd.date_range(start=self.round_time(df['date'].iloc[0].to_pydatetime(),
                                                    date_delta=datetime.timedelta(seconds=int(self.tNA.get())),
                                                    to="up"),
                              end=self.round_time(df['date'].iloc[-1].to_pydatetime(),
                                                  date_delta=datetime.timedelta(seconds=int(self.tNA.get())),
                                                  to="down"),
                              freq=str(self.tNA.get()) + 's').to_frame(name='date').reset_index()

        del horas['index']
        del normal_df['index']

        self.mergin = pd.merge(horas, normal_df, how='left', on='date')
        self.mergin['date'] = self.mergin['date'] - datetime.timedelta(seconds=float(int(self.tNA.get()) / 2))

        repo.set_dataset_output("dataset3", self.mergin)

        self.upd_final_graph()

    def normalization(self, set_df):  # Funcao para normalizar temporalmente o dataset
        values = np.array([float(i) for i in set_df['value'].values])
        dates = [i for i in set_df['date']]

        #####Normalização temporal######
        deltaT = np.diff(dates)
        deltaT = [i.total_seconds() / 3600 for i in deltaT]
        deltaT.insert(0, 0)

        # Calculo Qmédio entre cada timestamp. Adiciono coluna Qmedio
        flow_average = [0] * len(values)
        for row_index in range(len(values)):
            if row_index == 0:  # corrijo o primeiro registo, assumo que caudal medio até ao primeiro registo foi o caudal instantaneo desse registo
                flow_average[row_index] = values[row_index]
            else:
                flow_average[row_index] = (values[row_index] + values[row_index - 1]) / 2

        # Calculo Volume associado a cada timestamp. Adiciono coluna Volume
        volume = [0] * len(values)
        for row_index in range(len(values)):
            if row_index == 0:  # corrijo o primeiro registo, assumo que caudal medio até ao primeiro registo foi o caudal instantaneo desse registo
                volume[row_index] = 0
            else:
                volume[row_index] = flow_average[row_index] * deltaT[row_index]

        # Calculo Volume acumulado associado a cada timestamp. Adiciono coluna Volume acumulado
        volume_ac = [0] * len(values)
        for row_index in range(len(values)):
            if row_index == 0:  # corrijo o primeiro registo, assumo que caudal medio até ao primeiro registo foi o caudal instantaneo desse registo
                volume_ac[row_index] = 0
            else:
                volume_ac[row_index] = volume[row_index] + volume_ac[row_index - 1]

        ts = pd.Series(data=volume_ac, index=dates)

        volume_acc_TS = traces.TimeSeries(ts)
        # USAR TRACES PARA OBTER Vac NAS VARIAS HORAS
        volume_spaced_TS = volume_acc_TS.sample(sampling_period=datetime.timedelta(seconds=int(self.tNA.get())),
                                                start=self.round_time(dates[0].to_pydatetime(), date_delta=datetime.timedelta(seconds=int(self.tNA.get())), to="up"),
                                                end=self.round_time(dates[-1].to_pydatetime(), date_delta=datetime.timedelta(seconds=int(self.tNA.get())), to="down"),
                                                interpolate='linear')
        volume_spaced_DF = pd.DataFrame(volume_spaced_TS)
        spaced_volume = [0] * len(volume_spaced_DF)

        for row_index in range(len(volume_spaced_DF)):
            if row_index == 0:  # corrijo o primeiro registo
                spaced_volume[row_index] = 0
            else:
                spaced_volume[row_index] = volume_spaced_DF[1][row_index] - volume_spaced_DF[1][row_index - 1]

        spaced_flow = [i / (int(self.tNA.get()) / 3600) for i in spaced_volume]

        dict_df = {
            'date': volume_spaced_DF[0],
            'value': spaced_flow
        }

        final_df = pd.DataFrame(dict_df, columns=["date", "value"])
        final_df = final_df.iloc[1:]  # remove first line since we cant calculate properly the first period
        # final_df = final_df.iloc[:-1]  # remove first line since we cant calculate properly the first period

        return final_df

    def upd_final_graph(self):  # Atualiza o gráfico final
        df = repo.get_dataset("dataset3").to_numpy()
        values = [float(i[1]) for i in df]  # Flow values, in float
        dates = [i[0] for i in df]

        dates = np.array(dates)
        values = np.array(values)

        self.ax3.cla()
        self.ax3.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[22,selected_language]) #original serie
        self.ax3.plot(self.mergin['date'], self.mergin['value'], marker="o", color='red', label=dictionary_keywords.loc[74,selected_language]) #plot for Time series after time step normalization

        # Fazer plot das linhas verticais nos nans
        nans = []  # array com ID's dos nans
        for row in range(len(self.mergin)):
            if np.isnan(self.mergin.iloc[row, 1]):
                nans.append(row)

        if len(nans) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in self.mergin['date'][nans]:
                self.vline = self.ax3.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
            self.vline = self.ax3.axvline(x=i, color='grey', linestyle='--', linewidth=0.5,
                                          label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed  # legenda

        # format graph
        self.ax3.xaxis.set_major_formatter(DATE_FORM)
        self.ax3.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax3.set_title(dictionary_keywords.loc[70,selected_language]) # title of Time series with identification of uniform spacing 

        self.ax3.legend()
        self.fig3.canvas.draw()

        plt.close(2)
        plt.close(3)
        # plt.plot(dates, values, '#4772FF', label='Série  original')
        # plt.plot(self.mergin['date'], self.mergin['value'], marker="*", color='#000000', label='Série normalizada')
        # plt.show()

    def G1(self):  # Série original com na identificados
        df = repo.get_dataset("dataset3")
        values = df['value']
        dates = df['date']

        plt.figure(1)
        plt.cla()
        plt.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        if len(self.nan) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in dates[self.nan]:
                plt.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
            plt.axvline(x=i, color='k', linestyle='--', linewidth=0.5, label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed  # legenda

        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.title(dictionary_keywords.loc[22,selected_language]) #original serie
        plt.legend()
        plt.show()

    def G2(self):  # Série original com Na's identificados como de curta ou longa duração
        df = repo.get_dataset("dataset3").to_numpy()
        values = [float(i[1]) for i in df]
        dates = [i[0].to_pydatetime() for i in df]

        dates = np.array(dates)
        values = np.array(values)

        plt.figure(2)
        plt.cla()
        plt.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values

        # Plot das linhas verticais com espaçamento uniforme
        dates_regular = pd.date_range(self.roundTime(dt=dates[0]), self.roundTime(dt=dates[-1]),
                                      freq=str(self.tNA.get()) + 's')  # obtem espaçamentos uniformes, certos com a hora
        for i in dates_regular:
            plt.axvline(x=i, color='r', linestyle='--', linewidth=0.3)
        plt.axvline(x=i, color='r', linestyle='--', linewidth=0.3, label=dictionary_keywords.loc[71,selected_language], marker='|') #uniform spacing plot

        # Plot da 'mancha' de falha com a legenda
        i = 0
        for i in dates[self.nan]:
            plt.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
        if len(self.nan) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            plt.axvline(x=i, color='k', linestyle='--', linewidth=0.5, label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed  # legenda

        ##Plot das linhas associadas ao periodo sem medição
        # Para obter a mediana do espaçamento
        df = repo.get_dataset("dataset3")
        values = df['value']
        dates = df['date']
        time_spacing = np.zeros(len(values) - 1)
        # Espacamento temporal
        for line in range(1, len(values), 1):
            # Conversao ns para s
            time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))
        time_spacing = pd.DataFrame(time_spacing)
        spacing_detail = time_spacing.describe()
        count = 0
        for i, j in enumerate(time_spacing[0]):
            if int(j) > int(self.tPL.get()) and math.isnan(values[i]) is not True:
                count += 1

        check = None
        for i in range(len(time_spacing[0])):
            if int(time_spacing[0][i]) > int(self.tPL.get()) and math.isnan(values[i]) is not True:
                plt.axvline(x=dates[i], color='indigo', linestyle='--', linewidth=1)  # Falhas Curtas
                plt.axvline(x=dates[i + 1], color='indigo', linestyle='--', linewidth=1)  # Falhas Curtas
                check = True
                lst_vlue = i
        if check:
            plt.axvline(x=dates[lst_vlue], color='indigo', linestyle='--', linewidth=1, label=dictionary_keywords.loc[72,selected_language],
                        marker='|')  # Falhas Curtas and period without measurments

        plt.title(dictionary_keywords.loc[56,selected_language]) #title for Time series with identified short and long duration gaps 
        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.legend()
        plt.show()

    def G3(self):  # série original com valores imputados e identificação de falhas de longa duração
        df = repo.get_dataset("dataset3").to_numpy()

        plt.figure(3)
        plt.cla()
        values = [float(i[1]) for i in df]  # Flow values, in float
        dates = [i[0] for i in df]

        dates = np.array(dates)
        values = np.array(values)

        plt.plot(dates, values, '#4772FF', label=dictionary_keywords.loc[22,selected_language]) #original serie
        plt.plot(self.mergin['date'], self.mergin['value'], marker="o", color='red', label=dictionary_keywords.loc[74,selected_language]) #plot for Time series after time step normalization

        # Fazer plot das linhas verticais nos nans
        nans = []  # array com ID's dos nans
        for row in range(len(self.mergin)):
            if np.isnan(self.mergin.iloc[row, 1]):
                nans.append(row)

        if len(self.nan) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in self.mergin['date'][nans]:
                plt.axvline(x=i, color='k', linestyle='--', linewidth=0.3)
            plt.axvline(x=i, color='k', linestyle='--', linewidth=0.5, label=dictionary_keywords.loc[63,selected_language], marker='|') #Label for long duration gaps reconstructed  # legenda

        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.legend()
        plt.show()


class Tab4(tk.Frame):  # Preenchimento de falhas (WIP)
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Preparacao da janela
        self.configure(background='white')  # Background

        # Separadores - linhas que dividem o programa
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=2, row=10, columnspan=98, sticky='ew')
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=2, row=52, columnspan=97, sticky='ew')

        # Todas as colunas e rows tem weight de 1 e cria uma matrix de 100 x 100
        for x in range(100):
            self.columnconfigure(x, weight=1)
        for x in range(100):
            self.rowconfigure(x, weight=1)

        #button for import of historical data:
        self.Btn_Import = tk.Button(self, text=dictionary_keywords.loc[75,selected_language], command=self.file_input,
                                  font=NORMAL_FONT, relief=GROOVE).grid(row=2, column=92, columnspan=6,
                                                                        sticky='NSEW')
        #button for Historical data seasonal decomposition:
        self.Btn_Decompose = tk.Button(self, text=dictionary_keywords.loc[76,selected_language], command=self.btn_series_decomposition,
                                  font=NORMAL_FONT, relief=GROOVE, wraplength=150).grid(row=18, column=92, columnspan=6, rowspan=2,
                                                                        sticky='NSEW')

        self.Btn_Reconstruction = tk.Button(self, text=dictionary_keywords.loc[11,selected_language], command=self.btn_reconstruction,
                                            font=NORMAL_FONT, relief=GROOVE).grid(row=70, column=92, columnspan=6,
                                                                                  sticky='NSEW')



        self.Period = tk.Entry(self, textvariable=tk.StringVar(self, None), width=10)
        self.Period.grid(column=97, row=15, rowspan=1, columnspan=2, sticky='EW')


        # Combobox para os diferentes tipos de decomposiçção
        self.decomposition_box = ttk.Combobox(
            self, textvariable=tk.StringVar(), width=10)
        self.decomposition_box['values'] = ('additive',
                                         'multiplicative')
        self.decomposition_box.grid(column=97, row=16, rowspan=1, columnspan=2, sticky='EW')
        self.decomposition_box.current(0)






        self.graph_original()
        self.table_info_measures()
        self.boxplot_hour()
        self.boxplot_wdwk()
        self.boxplot_day()
        self.boxplot_weekday()
        self.graph_seasonal_decomp()
        self.table_info_season()
        self.graph_forecast()


    def file_input(self):#history
        MainGUI.history_input(self)
        history = repo.get_dataset("history").copy()
        values_h = history['value']
        dates_h = history['date']

        df = repo.get_dataset("dataset4")
        values = df['value']
        dates = df['date']

        period_estimate = self.period_estimate(history)

        self.upd_graph_original2(values, dates, values_h, dates_h)
        self.upd_table_info_measures2(values, dates, values_h, dates_h, period_estimate)

        plt.close('all')

    def menubar(self, root):
        menubar = tk.Menu(root)
        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label=dictionary_keywords.loc[5,selected_language], command=lambda: root.file_input(Tab4))
        fileMenu.add_command(label=dictionary_keywords.loc[18,selected_language], command=self.clear) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[101,selected_language], command=lambda: root.clear_all()) #Clear data
        fileMenu.add_command(label=dictionary_keywords.loc[19,selected_language], command=lambda: file_output("dataset4")) #export data
        fileMenu.add_separator()
        fileMenu.add_command(label=dictionary_keywords.loc[6,selected_language], command=self.quit)
        menubar.add_cascade(label=dictionary_keywords.loc[7,selected_language], menu=fileMenu)

        methodMenu = tk.Menu(menubar, tearoff=False)
        methodMenu.add_command(label=dictionary_keywords.loc[8,selected_language], #Anomaly identification and removal
                                command=lambda: root.show_frame(Tab1, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[9,selected_language], #Short-duration gap reconstruction
                               command=lambda: root.show_frame(Tab2, from_menu=True))
        methodMenu.add_command(label=dictionary_keywords.loc[10,selected_language], command=lambda: root.show_frame(Tab3, from_menu=True)) #time step normalization
        methodMenu.add_command(label=dictionary_keywords.loc[11,selected_language], command=lambda: root.show_frame(Tab4, from_menu=True))
        menubar.add_cascade(label=dictionary_keywords.loc[12,selected_language], menu=methodMenu) #tools

        graphMenu = tk.Menu(menubar, tearoff=False)  # Gráficos de visualização
        graphMenu.add_command(label=dictionary_keywords.loc[77,selected_language], command=self.G1) #time series being processed and historical data
        graphMenu.add_command(label=dictionary_keywords.loc[78,selected_language], command=self.G2) #Boxplot for each time step (all days)
        graphMenu.add_command(label=dictionary_keywords.loc[79,selected_language], command=self.G3) #Boxplot for each time step (weekdays vs weekends)
        graphMenu.add_command(label=dictionary_keywords.loc[80,selected_language], command=self.G4) #Boxplot for each day in the historical data
        graphMenu.add_command(label=dictionary_keywords.loc[81,selected_language], command=self.G5) #boxplot for each weekday
        graphMenu.add_command(label=dictionary_keywords.loc[82,selected_language], command=self.G6) #Seasonality decomposition
        graphMenu.add_command(label=dictionary_keywords.loc[83,selected_language], command=self.G7) #processed time serie
        menubar.add_cascade(label=dictionary_keywords.loc[27,selected_language], menu=graphMenu) #show graphs

        helpMenu = tk.Menu(menubar, tearoff=False)
        helpMenu.add_command(label=dictionary_keywords.loc[97,selected_language], command=lambda: manual(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[103,selected_language], command=lambda: research_paper(selected_language))
        helpMenu.add_command(label=dictionary_keywords.loc[14,selected_language], command=lambda: about_dsc(dictionary_keywords, selected_language))#about

        menubar.add_cascade(label=dictionary_keywords.loc[13,selected_language], menu=helpMenu)

        return menubar

    def get_data(self):
        self.dataset = repo.get_dataset("dataset4")
        self.df = self.dataset.copy()  # oDF
        self.df_numpy = self.dataset.to_numpy()  # df
        self.tab_functions()

    def tab_functions(self):
        df = repo.get_dataset("dataset4")
        values = df['value']
        dates = df['date']

        self.boxplot_hour()
        self.boxplot_wdwk()
        self.boxplot_day()
        self.boxplot_weekday()
        self.graph_seasonal_decomp()
        self.table_info_season()
        self.Period.delete(0, "end")
        self.decomposition_box.current(0)
        self.graph_forecast()

        self.upd_graph_original(values, dates)
        self.upd_table_info_measures(values, dates)
        plt.close('all')


    def preparation_boxplot(self, history):
        df = history.copy()

        ## A data passa a ser o indice
        df.index = df['date']
        del df['date']
        df.index = pd.to_datetime(df.index)

        df['Week_Days'] = df.index.day_name()
        df['Day'] = df.index.date
        df['Hour'] = df.index.time
        df['Week_Day_VS_Weekend'] = (
            (pd.DatetimeIndex(df.index).dayofweek) // 5 == 1).astype(int)

        cats = ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday']
        cat_type = CategoricalDtype(categories=cats, ordered=True)
        df['Week_Days'] = df['Week_Days'].astype(cat_type)
        return df

    def period_estimate(self, history):
        history2 = history.copy()

        ###Estimar o periodo de um dia, ou seja, o nr de medições que ocorrem num dia
        ###Como o 1º dia do historico pode vir incompleto, vamos buscar a contagem do 2 dia
        history.index = history['date']
        del history['date']
        # print(df)
        history.index = pd.to_datetime(history.index)
        history_count_day = history.groupby(history.index.date).count()
        period_estimate = history_count_day.iloc[1]

        return period_estimate.value


    def clear(self):  # Limpa os dados e gráficos
        repo.set_dataset("dataset4", None)
        repo.set_history_dataset(None)
        repo.set_dataset_output("dataset4", None)

        self.graph_original()
        self.table_info_measures()
        self.boxplot_hour()
        self.boxplot_wdwk()
        self.boxplot_day()
        self.boxplot_weekday()
        self.graph_seasonal_decomp()
        self.table_info_season()
        self.graph_forecast()

        self.Period.delete(0, "end")
        self.decomposition_box.current(0)

        # for x in range(3):
        #     tk.Label(self, text='', bg='white').grid(
        #         column=95, columnspan=5, row=5 + x, sticky='NSWE')

        plt.close('all')


    def graph_original(self):  # Série de input
        self.fig = Figure(figsize=(1, 1), dpi=50)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(dictionary_keywords.loc[77,selected_language]) #Title for time series being processed and historical data
        # we plot y as a function of a, which parametrizes x
        self.ax.plot(['00:00:00', '06:00:00',
                      '12:00:00', '18:00:00', '24:00:00'], ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax.legend()
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 

        FigureCanvasTkAgg(self.fig, master=self).get_tk_widget().grid(column=0, row=0, columnspan=90, rowspan=10, sticky='NSEW')

    def table_info_measures(self):
        #count:
        tk.Label(self, text=dictionary_keywords.loc[59,selected_language], bg='white', font=NORMAL_FONT).grid(column=94, row=4, columnspan=3,
                                                                           sticky='NSWE')
        tk.Label(self, text=dictionary_keywords.loc[68,selected_language], bg='white', font=NORMAL_FONT).grid(column=97, row=4, columnspan=3,
                                                                           sticky='NSWE') #desired spacing label

        #values beeing processed label:
        tk.Label(self, text=dictionary_keywords.loc[84,selected_language], bg='white', font=NORMAL_FONT, anchor='e',
                 fg='red').grid(column=90, row=5, columnspan=4, sticky='NSWE')
        #historical data label:
        tk.Label(self, text=dictionary_keywords.loc[86,selected_language], bg='white', font=NORMAL_FONT, anchor='e', fg='#257AB5').grid(
            column=90, row=6, columnspan=4, sticky='NSWE')
        #missing values label:
        tk.Label(self, text=dictionary_keywords.loc[85,selected_language], bg='white', font=NORMAL_FONT, anchor='e', fg='black').grid(
            column=90, row=7, columnspan=4, sticky='NSWE')

        tk.Label(self, text="", bg='white', font=NORMAL_FONT, anchor='e', fg='#257AB5').grid(
            column=94, row=5, columnspan=3, sticky='NSWE')
        tk.Label(self, text="", bg='white', font=NORMAL_FONT, anchor='e', fg='#257AB5').grid(
            column=94, row=6, columnspan=3, sticky='NSWE')
        tk.Label(self, text="", bg='white', font=NORMAL_FONT, anchor='e', fg='black').grid(
            column=94, row=7, columnspan=3, sticky='NSWE')
        tk.Label(self, text="", bg='white', font=NORMAL_FONT, anchor='e', fg='#257AB5').grid(
            column=97, row=5, columnspan=3, sticky='NSWE')
        tk.Label(self, text="", bg='white', font=NORMAL_FONT, anchor='e', fg='#257AB5').grid(
            column=97, row=6, columnspan=3, sticky='NSWE')
        tk.Label(self, text="", bg='white', font=NORMAL_FONT, anchor='e', fg='black').grid(
            column=97, row=7, columnspan=3, sticky='NSWE')

    def upd_table_info_measures(self, values, dates):
        tk.Label(self, text=len(values), bg='white', font=NORMAL_FONT, fg='red').grid(column=94, row=5, columnspan=3, sticky='NSWE')

        spacing = (dates.iloc[1] - dates.iloc[0])
        tk.Label(self, text=spacing.seconds, bg='white', font=NORMAL_FONT, fg='red').grid(column=97, row=5, columnspan=3, sticky='NSWE')

    def upd_table_info_measures2(self, values, dates, values_h, dates_h, period_estimate):

        begin_time = dates_h.iloc[-1]
        end_time = dates.iloc[0]


        spacing = (dates.iloc[1] - dates.iloc[0])

        datelist = pd.date_range(start=begin_time + spacing, end=end_time - spacing, freq = spacing)

        datelist = pd.Series(datelist)
        new_dates = pd.concat([datelist, dates], ignore_index=True)

        values_list=[]
        for i in range(len(datelist)):
            values_list.append(np.nan)
        values_list = pd.Series(values_list)

        new_values = pd.concat([values_list, values], ignore_index=True)


        # Fazer plot das linhas verticais nos nans
        nans = []  # array com ID's dos nans
        for row in range(len(new_values)):
            if np.isnan(new_values[row]):
                nans.append(row)


        spacing_h = (dates_h.iloc[1] - dates_h.iloc[0])

        tk.Label(self, text=len(values_h), bg='white', font=NORMAL_FONT, fg='#257AB5').grid(column=94, row=6, columnspan=3, sticky='NSWE')
        tk.Label(self, text=spacing_h.seconds, bg='white', font=NORMAL_FONT, fg='#257AB5').grid(column=97, row=6, columnspan=3, sticky='NSWE')

        tk.Label(self, text=len(nans), bg='white', font=NORMAL_FONT, fg='black').grid(column=94, row=7, columnspan=3, sticky='NSWE')
        # tk.Label(self, text=spacing.seconds, bg='white', font=NORMAL_FONT, fg='black').grid(column=97, row=7, columnspan=3, sticky='NSWE')
        tk.Label(self, text='-', bg='white', font=NORMAL_FONT, fg='black').grid(column=97, row=7, columnspan=3, sticky='NSWE')

        self.Period.delete(0, "end")
        self.Period.insert(0, int(period_estimate))


    def upd_graph_original(self, values, dates):  # Atualiza o gráfico inicial

        self.ax.cla()
        self.ax.plot(dates, values, marker="o", color='red', label=dictionary_keywords.loc[74,selected_language]) #plot for Time series after time step normalization

        # format graph
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax.set_title(dictionary_keywords.loc[77,selected_language]) #Title for time series being processed and historical data

        # Fazer plot das linhas verticais nos nans
        nans = []  # array com ID's dos nans
        for row in range(len(values)):
            if np.isnan(values[row]):
                nans.append(row)

        if len(nans) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in range(len(nans)):
                self.vline = self.ax.axvline(x=dates[nans[i]], color='k', linestyle='--', linewidth=0.3)
            self.vline = self.ax.axvline(x=dates[nans[i]], color='grey', linestyle='--', linewidth=0.5,
                                          label=dictionary_keywords.loc[87,selected_language], marker='|')  # legend for missing values

        self.ax.legend()
        self.fig.canvas.draw()

    def upd_graph_original2(self, values, dates, values_h, dates_h):  # Atualiza o gráfico inicial
        self.ax.cla()
        self.ax.plot(dates, values, marker="o", color='red', label=dictionary_keywords.loc[74,selected_language]) #plot for Time series after time step normalization

        self.ax.plot(dates_h, values_h, marker="^", color='#257AB5', label=dictionary_keywords.loc[86,selected_language]) #historical data axis label


        # format graph
        self.ax.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax.set_title(dictionary_keywords.loc[77,selected_language]) #Title for time series being processed and historical data

        begin_time = dates_h.iloc[-1]
        end_time = dates.iloc[0]


        spacing = (dates.iloc[1] - dates.iloc[0])

        datelist = pd.date_range(start=begin_time + spacing, end=end_time - spacing, freq = spacing)

        datelist = pd.Series(datelist)
        new_dates = pd.concat([datelist, dates], ignore_index=True)

        values_list=[]
        for i in range(len(datelist)):
            values_list.append(np.nan)
        values_list = pd.Series(values_list)

        new_values = pd.concat([values_list, values], ignore_index=True)


        nans = []  
        for row in range(len(new_values)):
            if np.isnan(new_values[row]):
                nans.append(row)

        if len(nans) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in range(len(nans)):
                self.vline = self.ax.axvline(x=new_dates[nans[i]], color='k', linestyle='--', linewidth=0.3)
            self.vline = self.ax.axvline(x=new_dates[nans[i]], color='grey', linestyle='--', linewidth=0.5,
                                          label=dictionary_keywords.loc[87,selected_language], marker='|')  # legend for missing values

        self.ax.legend()
        self.fig.canvas.draw()


    def boxplot_hour(self):  # Série de input

        self.fig2 = Figure(figsize=(1, 1),dpi=50)
        self.ax2 = self.fig2.subplots()
        sns.boxplot(x=None, y=None, data=None, ax=self.ax2)
        self.ax2.set_title(dictionary_keywords.loc[78,selected_language]) #Boxplot for each time step (all days)
        self.ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax2.set_xlabel(r'Timestamp')

        FigureCanvasTkAgg(self.fig2, master=self).get_tk_widget().grid(
            column=0, row=11, columnspan=40, rowspan=20, sticky='NSEW')

        # fig2, ax2 = plt.subplots()
        # print(df)
        # sns.set_theme(style="whitegrid")
        # ax2 = sns.boxplot(x="Week_Days", y="value", data= df)
        # FigureCanvasTkAgg(fig2, master=self).get_tk_widget().grid(
        #     column=0, row=11, columnspan=30, rowspan=30, sticky='NSEW')

    def upd_boxplot_hour(self, df):
        df = df.sort_values(by=['Hour'])
        self.ax2.cla()
        sns.boxplot(x="Hour", y="value", data=df, ax=self.ax2)
        self.ax2.set_xticklabels(self.ax2.get_xticklabels(), rotation=45)
        self.ax2.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax2.set_xlabel(r'Timestamp')

        every_nth = 4
        for n, label in enumerate(self.ax2.xaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)


        self.ax2.set_title(dictionary_keywords.loc[78,selected_language]) #Boxplot for each time step (all days)
        self.fig2.canvas.draw()


    def boxplot_wdwk(self):  # Série de input

        self.fig3 = Figure(figsize=(1, 1), dpi=50)
        self.ax3 = self.fig3.subplots()
        sns.boxplot(x=None, y=None, data=None, ax=self.ax3)
        self.ax3.set_title(dictionary_keywords.loc[88,selected_language]) #title of boxplot for weekend and weekdays
        self.ax3.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax3.set_xlabel(r'Timestamp')

        FigureCanvasTkAgg(self.fig3, master=self).get_tk_widget().grid(
            column=0, row=31, columnspan=40, rowspan=20, sticky='NSEW')

        # fig2, ax2 = plt.subplots()
        # print(df)
        # sns.set_theme(style="whitegrid")
        # ax2 = sns.boxplot(x="Week_Days", y="value", data= df)
        # FigureCanvasTkAgg(fig2, master=self).get_tk_widget().grid(
        #     column=0, row=11, columnspan=30, rowspan=30, sticky='NSEW')

    def upd_boxplot_wdwk(self, df):
        df = df.sort_values(by=['Hour'])
        self.ax3.cla()
        sns.boxplot(x="Hour", y="value", hue="Week_Day_VS_Weekend", data=df, ax=self.ax3)
        self.ax3.set_xticklabels(self.ax3.get_xticklabels(), rotation=45)
        self.ax3.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax3.set_xlabel(r'Timestamp')

        handles, _= self.ax3.get_legend_handles_labels()
        self.ax3.legend(handles, [dictionary_keywords.loc[89,selected_language], dictionary_keywords.loc[90,selected_language]]) #legend of day of the week and weekend

        every_nth = 4
        for n, label in enumerate(self.ax3.xaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)
        
        self.ax3.set_title(dictionary_keywords.loc[88,selected_language]) #title of boxplot for weekend and weekdays
        self.fig3.canvas.draw()


    def boxplot_day(self):  # Série de input

        self.fig4 = Figure(figsize=(1, 1), dpi=50)
        self.ax4 = self.fig4.subplots()
        sns.boxplot(x=None, y=None, data=None, ax=self.ax4)
        self.ax4.set_title(dictionary_keywords.loc[80,selected_language]) #Boxplot for each day in the historical data
        self.ax4.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax4.set_xlabel(r'Timestamp')

        FigureCanvasTkAgg(self.fig4, master=self).get_tk_widget().grid(
            column=40, row=11, columnspan=30, rowspan=20, sticky='NSEW')

        # fig2, ax2 = plt.subplots()
        # print(df)
        # sns.set_theme(style="whitegrid")
        # ax2 = sns.boxplot(x="Week_Days", y="value", data= df)
        # FigureCanvasTkAgg(fig2, master=self).get_tk_widget().grid(
        #     column=0, row=11, columnspan=30, rowspan=30, sticky='NSEW')

    def upd_boxplot_day(self, df):

        self.ax4.cla()
        sns.boxplot(x="Day", y="value", data=df, ax=self.ax4)
        self.ax4.set_xticklabels(self.ax4.get_xticklabels(), rotation=45)
        self.ax4.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax4.set_xlabel(r'Timestamp')

        # every_nth = 2
        # for n, label in enumerate(self.ax4.xaxis.get_ticklabels()):
        #     if n % every_nth != 0:
        #         label.set_visible(False)

        self.ax4.set_title(dictionary_keywords.loc[80,selected_language]) #Boxplot for each day in the historical data
        self.fig4.canvas.draw()


    def boxplot_weekday(self):  # Série de input

        self.fig5 = Figure(figsize=(1, 1), dpi=50)
        self.ax5 = self.fig5.subplots()
        sns.boxplot(x=None, y=None, data=None, ax=self.ax3)
        self.ax5.set_title(dictionary_keywords.loc[81,selected_language]) #boxplot for each weekday
        self.ax5.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax5.set_xlabel(r'Timestamp')

        FigureCanvasTkAgg(self.fig5, master=self).get_tk_widget().grid(
            column=40, row=31, columnspan=30, rowspan=20, sticky='NSEW')

    def upd_boxplot_weekday(self, df):
        # print(df)
        # df = df.sort_values(by=['Hour'])
        # print(df)
        self.ax5.cla()
        sns.boxplot(x="Week_Days", y="value", data=df, ax=self.ax5)
        self.ax5.set_xticklabels(self.ax5.get_xticklabels(), rotation=45)
        self.ax5.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax5.set_xlabel(r'Timestamp')

        self.ax5.set_title(dictionary_keywords.loc[81,selected_language]) #boxplot for each weekday
        self.fig5.canvas.draw()


    def graph_seasonal_decomp(self):

        n = [0] * 100
        m = range(100)

        self.fig6 = Figure(figsize=(1, 1), dpi=50)
        self.ax61 = self.fig6.add_subplot(411)
        self.ax61.set_title(dictionary_keywords.loc[82,selected_language]) #seasonality decomposition
        self.ax61.plot(m, n, 'white')
        self.ax61.set_ylabel(r'observed')

        self.ax62 = self.fig6.add_subplot(412, sharex=self.ax61)
        self.ax62.plot(m, n, 'white')
        self.ax62.set_ylabel(r'trend')

        self.ax63 = self.fig6.add_subplot(413, sharex=self.ax61)
        self.ax63.plot(m, n, 'white')
        self.ax63.set_ylabel(r'seasonal')

        self.ax64 = self.fig6.add_subplot(414, sharex=self.ax61)
        self.ax64.plot(m, n, 'white')
        self.ax64.set_ylabel(r'residual')


        FigureCanvasTkAgg(self.fig6, master=self).get_tk_widget().grid(
            column=70, row=11, columnspan=20, rowspan=40, sticky='NSEW')

    def upd_graph_seasonal_decomp(self):
        history = repo.get_dataset("history").copy()

        decomposition_option = self.decomposition_box.get()
        period_option = self.Period.get()


        decomposed_24 = seasonal_decompose(x=history.value, model=decomposition_option, period=int(period_option))
        observed = decomposed_24.observed
        trend = decomposed_24.trend
        seasonal = decomposed_24.seasonal
        residual = decomposed_24.resid
        x = range(len(observed))

        self.ax61.cla()
        self.ax61.plot(x, observed)
        self.ax61.set_title(dictionary_keywords.loc[82,selected_language]) #seasonality decomposition

        self.ax62.cla()
        self.ax62.plot(x, trend)

        self.ax63.cla()
        self.ax63.plot(x, seasonal)

        self.ax64.cla()
        self.ax64.plot(x, residual)

        self.ax61.set_ylabel(r'observed')
        self.ax62.set_ylabel(r'trend')
        self.ax63.set_ylabel(r'seasonal')
        self.ax64.set_ylabel(r'residual')


        self.fig6.canvas.draw()


    def table_info_season(self):
        # tk.Label(self, text="Contagem", bg='white', font=NORMAL_FONT).grid(column=95, row=4, columnspan=5,
        #                                                                    sticky='NSWE')

        #Seasonality time course button label
        tk.Label(self, text=dictionary_keywords.loc[91,selected_language], bg='white', font=NORMAL_FONT, fg='black', anchor='e').grid(column=90, row=15, rowspan=1, columnspan=7, sticky='NSWE')

        #Decomposition method button label
        tk.Label(self, text=dictionary_keywords.loc[92,selected_language], bg='white', font=NORMAL_FONT, fg='black', anchor='e').grid(column=90, row=16, rowspan=1, columnspan=7, sticky='NSWE')
        # tk.Label(self, text="Medições em falta", bg='white', font=NORMAL_FONT, anchor='e', fg='black').grid(
        #     column=90, row=7, columnspan=5, sticky='NSWE')


    def btn_series_decomposition(self):
        history = repo.get_dataset("history").copy()

        df = self.preparation_boxplot(history)
        self.upd_boxplot_hour(df)
        self.upd_boxplot_wdwk(df)
        self.upd_boxplot_day(df)
        self.upd_boxplot_weekday(df)
        
        plt.close(13)

        self.upd_graph_seasonal_decomp()

    def btn_reconstruction(self):

        df = repo.get_dataset("dataset4").copy()
        # print(df.iloc[:3])

        values = df['value']
        dates = df['date']
        spacing = (dates.iloc[1] - dates.iloc[0])


        history = repo.get_dataset("history").copy()
        # print(history)

        history=self.normalization_hist(history,spacing.total_seconds())

        values_h = history['value']
        dates_h = history['date']


        # print(history)



        begin_time = dates_h.iloc[-1]
        end_time = dates.iloc[0]

        datelist = pd.date_range(start=begin_time + spacing, end=end_time - spacing, freq=spacing)
        datelist = pd.Series(datelist, name='date')
        new_dates_nan = pd.concat([datelist, dates], ignore_index=True)#dates from history(last + 1) until serie(-1)
        # print(new_dates.values)

        values_list = []
        for i in range(len(datelist)):
            values_list.append(np.nan)
        values_list = pd.Series(values_list, name='value')
        new_values_nan = pd.concat([values_list, values], ignore_index=True)#values from history(last + 1) until serie(-1)
        # print(new_values.values)

        t = pd.concat([new_dates_nan, new_values_nan], axis=1)
        history = pd.concat([history, t], ignore_index=True)
        # print(history)
        

        #lista de dias individuais que o quevedo vai receber 
        unique_days = []
        for x in new_dates_nan.dt.date:
            # check if exists in unique_list or not
            if x not in unique_days:
                unique_days.append(x)


        for x in range(len(unique_days)):#para cada um destes dias

            date1 = np.datetime64(unique_days[x]) + np.timedelta64(0, 's')#vou buscar o dia
   
            hist_temp = history[history['date'] < date1]#e filtro apenas as medições anteriores

            type_analysis = "original"
            # type_analysis = "grid"

            new_dates1, new_values1 = Quevedo(hist_temp, type_analysis, date1)  #chamo o quevedo para o historico temporario / recebo 1 dia inteiro
            tempDf1 = pd.DataFrame(columns=['date', 'value'])   #DF quevedo
            tempDf1['date'] = new_dates1
            tempDf1['value'] = new_values1
            # print(tempDf1)


            #Vlookup para ir buscar ao tempDf1 do quevedo os valores em falta para o unique day
            mergin = pd.merge(history, tempDf1, how='left', on='date')
            # print(mergin)

            mergin["value"] = mergin["value_x"]
            for row in range(len(mergin)):
                if math.isnan(mergin['value_x'][row]):
                    mergin['value'][row] = mergin['value_y'][row]
                else:
                    mergin['value'][row] = mergin['value_x'][row]
            mergin.drop(columns=["value_x", "value_y"], inplace=True)


            # no final atualizo historico
            history = mergin
        repo.set_dataset_output("dataset4", history)
        values_h = history['value']
        dates_h = history['date']
        self.upd_graph_forecast(history,dates)
        # print(new_pd)


    def graph_forecast(self):  # Série de input
        self.fig7 = Figure(figsize=(1, 1), dpi=50)
        self.ax7 = self.fig7.add_subplot(111)
        self.ax7.set_title(dictionary_keywords.loc[93,selected_language]) #title of graph - reconstructed long gaps
        # we plot y as a function of a, which parametrizes x
        self.ax7.plot(['00:00:00', '06:00:00',
                      '12:00:00', '18:00:00', '24:00:00'], ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'], 'white', label=dictionary_keywords.loc[28,selected_language]) # plot label - flowrate values
        self.ax7.legend()
        self.ax7.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 

        FigureCanvasTkAgg(self.fig7, master=self).get_tk_widget().grid(
            column=0, row=53, columnspan=90, rowspan=47, sticky='NSEW')

    def upd_graph_forecast(self, history,dates):
        self.ax7.cla()
        history_ = history.copy()
        history_ = history_[history_['date']>dates.iloc[0]]

        treated_v = history_['value']
        trated_d = history_['date']

        self.ax7.plot(trated_d, treated_v, marker="^", color='#257AB5', label=dictionary_keywords.loc[83,selected_language]) #preccessed time serie plot
        # self.ax7.plot(dates, values, marker="o", color='red', label=dictionary_keywords.loc[22,selected_language]) #original serie


        # self.ax7.plot(dates_h, values_h, marker="^", color='#257AB5', label='Histórico')


        # format graph
        self.ax7.set_ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        self.ax7.set_title(dictionary_keywords.loc[93,selected_language]) #original serie

        self.ax7.legend()
        self.fig7.canvas.draw()

    def normalization_hist(self, set_df,spacing):  # Funcao para normalizar temporalmente o dataset
        values = np.array([float(i) for i in set_df['value'].values])
        dates = [i for i in set_df['date']]

        #####Normalização temporal######
        deltaT = np.diff(dates)
        deltaT = [i.total_seconds() / 3600 for i in deltaT]
        deltaT.insert(0, 0)

        # Calculo Qmédio entre cada timestamp. Adiciono coluna Qmedio
        flow_average = [0] * len(values)
        for row_index in range(len(values)):
            if row_index == 0:  # corrijo o primeiro registo, assumo que caudal medio até ao primeiro registo foi o caudal instantaneo desse registo
                flow_average[row_index] = values[row_index]
            else:
                flow_average[row_index] = (
                    values[row_index] + values[row_index - 1]) / 2

        # Calculo Volume associado a cada timestamp. Adiciono coluna Volume
        volume = [0] * len(values)
        for row_index in range(len(values)):
            if row_index == 0:  # corrijo o primeiro registo, assumo que caudal medio até ao primeiro registo foi o caudal instantaneo desse registo
                volume[row_index] = 0
            else:
                volume[row_index] = flow_average[row_index] * deltaT[row_index]

        # Calculo Volume acumulado associado a cada timestamp. Adiciono coluna Volume acumulado
        volume_ac = [0] * len(values)
        for row_index in range(len(values)):
            if row_index == 0:  # corrijo o primeiro registo, assumo que caudal medio até ao primeiro registo foi o caudal instantaneo desse registo
                volume_ac[row_index] = 0
            else:
                volume_ac[row_index] = volume[row_index] + \
                    volume_ac[row_index - 1]

        ts = pd.Series(data=volume_ac, index=dates)

        volume_acc_TS = traces.TimeSeries(ts)
        # USAR TRACES PARA OBTER Vac NAS VARIAS HORAS
        volume_spaced_TS = volume_acc_TS.sample(sampling_period=datetime.timedelta(seconds=int(spacing)),
                                                start=self.round_time(dates[0].to_pydatetime(), date_delta=datetime.timedelta(
                                                    seconds=int(spacing)), to="up"),
                                                end=self.round_time(dates[-1].to_pydatetime(), date_delta=datetime.timedelta(
                                                    seconds=int(spacing)), to="down"),
                                                interpolate='linear')
        volume_spaced_DF = pd.DataFrame(volume_spaced_TS)
        spaced_volume = [0] * len(volume_spaced_DF)

        for row_index in range(len(volume_spaced_DF)):
            if row_index == 0:  # corrijo o primeiro registo
                spaced_volume[row_index] = 0
            else:
                spaced_volume[row_index] = volume_spaced_DF[1][row_index] - \
                    volume_spaced_DF[1][row_index - 1]

        spaced_flow = [i / (int(spacing) / 3600) for i in spaced_volume]

        dict_df = {
            'date': volume_spaced_DF[0],
            'value': spaced_flow
        }

        final_df = pd.DataFrame(dict_df, columns=["date", "value"])
        # remove first line since we cant calculate properly the first period
        final_df = final_df.iloc[1:]
        # final_df = final_df.iloc[:-1]  # remove first line since we cant calculate properly the first period

        final_df['date'] = final_df['date'] - \
            datetime.timedelta(seconds=float(int(spacing) / 2))


        return final_df

    def round_time(self, dt=None, date_delta=datetime.timedelta(seconds=60), to='average'):
        """
        Round a datetime object to a multiple of a timedelta
        dt : datetime.datetime object, default now.
        dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
        from:  http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
        """
        round_to = date_delta.total_seconds()
        if dt is None:
            dt = datetime.datetime.now()
        seconds = (dt - dt.min).seconds

        if seconds % round_to == 0 and dt.microsecond == 0:
            rounding = (seconds + round_to / 2) // round_to * round_to
        else:
            if to == 'up':
                # // is a floor division, not a comment on following line (like in javascript):
                rounding = (seconds + dt.microsecond / 1000000 +
                            round_to) // round_to * round_to
            elif to == 'down':
                rounding = seconds // round_to * round_to
            else:
                rounding = (seconds + round_to / 2) // round_to * round_to

        return dt + datetime.timedelta(0, rounding - seconds, - dt.microsecond)


    def G1(self):
        history = repo.get_dataset("history").copy()
        values_h = history['value']
        dates_h = history['date']
        
        df = repo.get_dataset("dataset4")
        values = df['value']
        dates = df['date']       


        plt.figure(8)
        plt.cla()

        plt.plot(dates, values, marker = 'o', color='red', label=dictionary_keywords.loc[74,selected_language]) #plot for Time series after time step normalization
        plt.plot(dates_h, values_h, marker="^", color='#257AB5', label=dictionary_keywords.loc[86,selected_language]) #historical data plot 

        begin_time = dates_h.iloc[-1]
        end_time = dates.iloc[0]


        spacing = (dates.iloc[1] - dates.iloc[0])

        datelist = pd.date_range(start=begin_time + spacing, end=end_time - spacing, freq = spacing)

        datelist = pd.Series(datelist)
        new_dates = pd.concat([datelist, dates], ignore_index=True)

        values_list=[]
        for i in range(len(datelist)):
            values_list.append(np.nan)
        values_list = pd.Series(values_list)

        new_values = pd.concat([values_list, values], ignore_index=True)


        nans = []  
        for row in range(len(new_values)):
            if np.isnan(new_values[row]):
                nans.append(row)

        if len(nans) != 0:  # Sem este if, o programa rebenta por não ter nan's para fazer a mancha
            # Plot da 'mancha' de falha com a legenda
            i = 0
            for i in range(len(nans)):
                plt.axvline(x=new_dates[nans[i]], color='k', linestyle='--', linewidth=0.3)
            plt.axvline(x=new_dates[nans[i]], color='grey', linestyle='--', linewidth=0.5,
                                          label=dictionary_keywords.loc[87,selected_language], marker='|')  # label for missing values

        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.title(dictionary_keywords.loc[77,selected_language]) #Title for time series being processed and historical data
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.legend()
        plt.show()

    def G2(self):
        history = repo.get_dataset("history").copy()
        df = self.preparation_boxplot(history)

        plt.figure(9)
        ax = sns.boxplot(x="Hour", y="value", data= df)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        plt.title(dictionary_keywords.loc[78,selected_language]) #Boxplot for each time step (all days)

        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.xlabel(r'Timestamp')
        plt.suptitle("")
        plt.show()

    def G3(self):
        history = repo.get_dataset("history").copy()
        df = self.preparation_boxplot(history)
        plt.figure(10)

        ax = sns.boxplot(x="Hour", y="value", hue="Week_Day_VS_Weekend", data=df)

        handles, _= ax.get_legend_handles_labels()
        ax.legend(handles, [dictionary_keywords.loc[89,selected_language], dictionary_keywords.loc[90,selected_language]])#legend of day of the week and weekend
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        plt.title(dictionary_keywords.loc[88,selected_language]) #title of boxplot for weekend and weekdays

        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.xlabel(r'Timestamp')
        # get rid of the automatic 'Boxplot grouped by group_by_column_name' title
        plt.suptitle("")
        plt.show()

    def G4(self):
        history = repo.get_dataset("history").copy()
        df = self.preparation_boxplot(history)
        plt.figure(11)

        ax = sns.boxplot(x="Day", y="value", data=df)


        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        plt.title(dictionary_keywords.loc[80,selected_language]) #Boxplot for each day in the historical data

        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.xlabel(r'Timestamp')
        # get rid of the automatic 'Boxplot grouped by group_by_column_name' title
        plt.suptitle("")
        plt.show()

    def G5(self):
        history = repo.get_dataset("history").copy()
        df = self.preparation_boxplot(history)
        plt.figure(12)

        ax = sns.boxplot(x="Week_Days", y="value", data=df)

        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        plt.title(dictionary_keywords.loc[81,selected_language]) #boxplot for each weekday

        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.xlabel(r'Timestamp')
        # get rid of the automatic 'Boxplot grouped by group_by_column_name' title
        plt.suptitle("")
        plt.show()

    def G6(self):
        history = repo.get_dataset("history").copy()

        decomposition_option = self.decomposition_box.get()
        period_option = self.Period.get()

        decomposed_24 = seasonal_decompose(x=history.value, model=decomposition_option, period=int(period_option))
        observed = decomposed_24.observed
        trend = decomposed_24.trend
        seasonal = decomposed_24.seasonal
        residual = decomposed_24.resid
        x = range(len(observed))

        
        fig = plt.figure(13)

        ax1 = fig.add_subplot(411)
        plt.title(dictionary_keywords.loc[82,selected_language]) #seasonality decomposition
        plt.plot(x, observed)
        plt.ylabel(r'observed')

        ax2 = fig.add_subplot(412, sharex=ax1)
        plt.plot(x, trend)
        plt.ylabel(r'trend')

        ax3 = fig.add_subplot(413, sharex=ax1)
        plt.plot(x, seasonal)
        plt.ylabel(r'seasonal')

        ax4 = fig.add_subplot(414, sharex=ax1)
        plt.plot(x, residual)
        plt.ylabel(r'residual')

        plt.show()

    def G7(self):  # série original com valores imputados e identificação de falhas de longa duração
        history = repo.get_dataset_output("dataset4").copy()
        values_h = history['value']
        dates_h = history['date']

        df = repo.get_dataset("dataset4")
        values = df['value']
        dates = df['date']

        plt.figure(14)
        plt.cla()

        plt.plot(dates_h, values_h, marker="^",
                 color='#257AB5', label=dictionary_keywords.loc[83,selected_language]) #processed time serie plot 

        plt.plot(dates, values, marker="o",
                 color='red', label=dictionary_keywords.loc[22,selected_language]) #original serie

        plt.gca().xaxis.set_major_formatter(DATE_FORM)
        plt.title(dictionary_keywords.loc[83,selected_language]) #title of processed time serie
        plt.ylabel(dictionary_keywords.loc[28,selected_language]) # yaxis label - flowrate 
        plt.legend()
        plt.show()





if __name__ == '__main__':
    repo = Repository()
    app = MainGUI()
    app.mainloop()
