import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog
import pandas as pd

# Tornar a variável conn global
conn = None

def executar_query_sql(query, treeview):
    global conn  # Adicionar a declaração global para acessar a variável conn
    try:
        # Executar a consulta SQL
        df = pd.read_sql_query(query, conn)

        # Mostrar o resultado no Treeview
        exibir_resultado_no_treeview(df, treeview)
    except Exception as e:
        # Mostrar mensagens de erro se ocorrerem
        treeview.delete(*treeview.get_children())  # Limpar o Treeview
        treeview["columns"] = ()
        treeview.insert("", "end", values=(f"Erro ao executar a consulta SQL: {str(e)}",))

def exibir_resultado_no_treeview(df, treeview):
    # Limpar o Treeview
    treeview.delete(*treeview.get_children())
    treeview["columns"] = tuple(df.columns)

    # Configurar as colunas no Treeview
    for coluna in df.columns:
        treeview.heading(coluna, text=coluna, anchor="center")
        treeview.column(coluna, anchor="center", width=150, minwidth=150)  # Ajustar a largura das colunas

    # Inserir os dados no Treeview
    for indice, linha in df.iterrows():
        treeview.insert("", "end", values=tuple(linha))

    # Configurar o evento de clique para editar células
    treeview.bind("<ButtonRelease-1>", lambda event: editar_celula(event, treeview, df))

def editar_celula(event, treeview, df):
    item_selecionado = treeview.selection()[0]

    if item_selecionado:
        coluna_clicada_id = treeview.identify_column(event.x)
        coluna_idx = int(coluna_clicada_id.split("#")[-1]) - 1 
        coluna_nome = treeview.heading(coluna_idx, "text")

        valor_atual = treeview.item(item_selecionado, "values")[coluna_idx]
        novo_valor = simpledialog.askstring("Editar Célula", f"Editar {coluna_nome}:", initialvalue=valor_atual)

        if novo_valor is not None:
            # Atualizar o DataFrame
            df.at[item_selecionado, coluna_nome] = novo_valor

            # Atualizar o Treeview
            treeview.set(item_selecionado, coluna_idx, novo_valor)

def carregar_tabelas(combo):
    global conn  # Adicionar a declaração global para acessar a variável conn
    # Limpar as opções existentes
    combo['values'] = ()

    # Verificar se a conexão está estabelecida
    if conn:
        # Ler as tabelas
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tabelas = conn.execute(query).fetchall()

        # Atualizar as opções do combobox
        combo['values'] = [t[0] for t in tabelas]

def abrir_tabela_selecionada(combo, treeview):
    global conn  # Adicionar a declaração global para acessar a variável conn
    tabela_escolhida = combo.get()

    # Verificar se a tabela escolhida existe
    if tabela_escolhida:
        # Chamar a função para ler o conteúdo da tabela
        executar_query_sql(f"SELECT * FROM {tabela_escolhida};", treeview)
    else:
        # Limpar o Treeview se nenhuma tabela for selecionada
        treeview.delete(*treeview.get_children())
        treeview["columns"] = ()

def selecionar_arquivo():
    global conn, tabela_combobox  # Adicionar a declaração global para acessar a variável conn e tabela_combobox
    arquivo_sqlite = filedialog.askopenfilename(filetypes=[("SQLite files", "*.sqlite")])
    if arquivo_sqlite:
        conn = sqlite3.connect(arquivo_sqlite)
        carregar_tabelas(tabela_combobox)

# Função principal
def main():
    global conn, tabela_combobox  # Adicionar a declaração global para acessar a variável conn e tabela_combobox
    # Criar a janela principal
    root = tk.Tk()
    root.title("Leitor e Editor de Bancos de Dados SQLite")

    # Resolução inicial
    resolucao_inicial = "1000x1000"
    root.geometry(resolucao_inicial)
    root.minsize(width=500, height=500)  # Resolução mínima

    # Criar combobox para escolher a tabela
    tabela_combobox = ttk.Combobox(root, state="readonly")
    tabela_combobox.grid(row=2, column=0, padx=10, pady=10, columnspan=2)
    carregar_tabelas(tabela_combobox)

    # Adicionar um botão para selecionar o arquivo de banco de dados
    selecionar_arquivo_button = ttk.Button(root, text="Selecionar Arquivo", command=selecionar_arquivo)
    selecionar_arquivo_button.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

    # Adicionar um texto acima da parte de seleção de tabela
    label_selecione_arquivo = tk.Label(root, text="Selecione o Arquivo do Banco de Dados")
    label_selecione_arquivo.grid(row=0, column=0, padx=10, pady=5, columnspan=2)

    # Treeview para exibir colunas e conteúdo da tabela
    treeview = ttk.Treeview(root)
    treeview.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Barras de rolagem horizontal e vertical para o Treeview
    scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=treeview.yview)
    scrollbar_y.grid(row=3, column=2, sticky="ns")

    scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=treeview.xview)
    scrollbar_x.grid(row=4, column=0, columnspan=2, sticky="ew")

    treeview.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Widget de entrada para inserir consultas SQL
    sql_entry = tk.Entry(root, width=50)
    sql_entry.grid(row=5, column=0, padx=10, pady=10)

    # Botão para executar consulta SQL
    executar_sql_button = ttk.Button(root, text="Executar SQL", command=lambda: executar_query_sql(sql_entry.get(), treeview))
    executar_sql_button.grid(row=5, column=1, padx=10, pady=10)

    # Botão para abrir tabela selecionada
    abrir_tabela_button = ttk.Button(root, text="Abrir Tabela", command=lambda: abrir_tabela_selecionada(tabela_combobox, treeview))
    abrir_tabela_button.grid(row=2, column=1, padx=10, pady=10)

    # Permitir redimensionamento
    root.columnconfigure(0, weight=1)
    root.rowconfigure(3, weight=1)

    # Iniciar o loop principal da interface gráfica
    root.mainloop()

    # Fechar a conexão ao fechar a janela
    if conn:
        conn.close()

# Executar a função principal
if __name__ == "__main__":
    main()
