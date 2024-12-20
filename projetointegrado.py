# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GuUFj-qVN77Y66DgwaQQHVflsIcxUIgx
"""

import sqlite3
import json

class Estoque:
    def __init__(self):
        self.conn = sqlite3.connect("estoque.db")
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            senha TEXT,
            tipo TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto TEXT PRIMARY KEY,
            nome_produto TEXT,
            categoria_id INTEGER,
            quantidade INTEGER,
            preco REAL,
            localizacao TEXT,
            FOREIGN KEY(categoria_id) REFERENCES categorias(id)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id TEXT,
            quantidade INTEGER,
            tipo TEXT,
            nota_fiscal TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        self.conn.commit()

    def carregar_usuarios(self):
        self.cursor.execute("SELECT * FROM usuarios")
        usuarios_db = self.cursor.fetchall()
        return [Usuario(usuario[1], usuario[2], usuario[3]) for usuario in usuarios_db]

    def autenticar_usuario(self):
        nome = input("Digite seu nome de usuário: ")
        senha = input("Digite sua senha: ")
        for usuario in self.carregar_usuarios():
            if usuario.nome == nome and usuario.senha == senha:
                return usuario
        print("Usuário ou senha incorretos.")
        return None

    def cadastrar_categoria(self, usuario):
        if usuario.tipo in ["estoquista", "gerente_setor"]:
            nome_categoria = input("Digite o nome da categoria: ")
            self.cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome_categoria,))
            self.conn.commit()
            print(f"Categoria '{nome_categoria}' cadastrada com sucesso!")
        else:
            print("Acesso negado. Apenas estoquistas e gerentes de setor podem cadastrar categorias.")

    def cadastrar_produto(self, usuario):
        if usuario.tipo in ["estoquista", "gerente_setor"]:
            id_produto = input("Digite o ID do produto: ")
            nome_produto = input("Digite o nome do produto: ")
            nome_categoria = input("Digite o nome da categoria: ")
            quantidade = int(input("Digite a quantidade: "))
            preco = float(input("Digite o preço: "))
            localizacao = input("Digite a localização: ")

            self.cursor.execute("SELECT id FROM categorias WHERE nome = ?", (nome_categoria,))
            categoria = self.cursor.fetchone()
            if categoria:
                self.cursor.execute('''
                    INSERT INTO produtos (id_produto, nome_produto, categoria_id, quantidade, preco, localizacao)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (id_produto, nome_produto, categoria[0], quantidade, preco, localizacao))
                self.conn.commit()
                print(f"Produto '{nome_produto}' cadastrado com sucesso!")
            else:
                print("Categoria não encontrada.")
        else:
            print("Acesso negado. Apenas estoquistas e gerentes de setor podem cadastrar produtos.")

    def consultar_produto(self, usuario):
        if usuario.tipo in ["estoquista", "gerente_setor", "usuario"]:
            id_produto = input("Digite o ID do produto: ")
            self.cursor.execute('''
                SELECT p.id_produto, p.nome_produto, c.nome, p.quantidade, p.preco, p.localizacao
                FROM produtos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE p.id_produto = ?
            ''', (id_produto,))
            produto = self.cursor.fetchone()
            if produto:
                print(f"ID: {produto[0]}, Nome: {produto[1]}, Categoria: {produto[2]}, Quantidade: {produto[3]}, Preço: {produto[4]}, Localização: {produto[5]}")
            else:
                print("Produto não encontrado.")
        else:
            print("Acesso negado. Apenas estoquistas, gerentes de setor e usuários podem consultar produtos.")

    def registrar_movimentacao(self, usuario):
        if usuario.tipo == "estoquista":
            id_produto = input("Digite o ID do produto: ")
            quantidade = int(input("Digite a quantidade: "))
            nota_fiscal = input("Digite a nota fiscal: ")
            self.cursor.execute('''
                SELECT quantidade FROM produtos WHERE id_produto = ?
            ''', (id_produto,))
            produto = self.cursor.fetchone()
            if produto:
                nova_quantidade = produto[0] + quantidade
                self.cursor.execute('''
                    UPDATE produtos SET quantidade = ? WHERE id_produto = ?
                ''', (nova_quantidade, id_produto))
                self.cursor.execute('''
                    INSERT INTO movimentacoes (produto_id, quantidade, tipo, nota_fiscal)
                    VALUES (?, ?, ?, ?)
                ''', (id_produto, quantidade, "entrada", nota_fiscal))
                self.conn.commit()
                print(f"Entrada de {quantidade} unidades do produto {id_produto} registrada.")
            else:
                print("Produto não encontrado.")
        else:
            print("Acesso negado. Apenas estoquistas podem registrar movimentações.")

    def gerar_relatorio_estoque(self, usuario):
            self.cursor.execute('''
                SELECT p.id_produto, p.nome_produto, c.nome, p.quantidade, p.preco, p.localizacao
                FROM produtos p
                JOIN categorias c ON p.categoria_id = c.id
            ''')
            produtos = self.cursor.fetchall()
            for produto in produtos:
                print(f"ID: {produto[0]}, Nome: {produto[1]}, Categoria: {produto[2]}, Quantidade: {produto[3]}, Preço: {produto[4]}, Localização: {produto[5]}")

    def gerar_relatorio_movimentacoes(self, usuario):
            self.cursor.execute('''
                SELECT m.produto_id, p.nome_produto, m.quantidade, m.tipo, m.nota_fiscal, m.data
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id_produto
            ''')
            movimentacoes = self.cursor.fetchall()
            for mov in movimentacoes:
                print(f"ID Produto: {mov[0]}, Nome Produto: {mov[1]}, Quantidade: {mov[2]}, Tipo: {mov[3]}, Nota Fiscal: {mov[4]}, Data: {mov[5]}")

    def solicitar_compra(self, usuario):
        if usuario.tipo == "usuario":
            id_produto = input("Digite o ID do produto que deseja comprar: ")
            quantidade = int(input("Digite a quantidade que deseja comprar: "))
            self.cursor.execute('''
                SELECT quantidade FROM produtos WHERE id_produto = ?
            ''', (id_produto,))
            produto = self.cursor.fetchone()
            if produto and produto[0] >= quantidade:
                print(f"Compra solicitada para o produto {id_produto}, quantidade: {quantidade}.")
            else:
                print("Quantidade insuficiente em estoque.")
        else:
            print("Acesso negado. Apenas usuários podem solicitar compras.")

    def autorizar_compra(self, usuario):
        if usuario.tipo == "gerente_setor":
            id_produto = input("Digite o ID do produto para autorizar compra: ")
            quantidade = int(input("Digite a quantidade para autorizar: "))
            nota_fiscal = input("Digite a nota fiscal da compra autorizada: ")

            self.cursor.execute('''
                SELECT quantidade FROM produtos WHERE id_produto = ?
            ''', (id_produto,))
            produto = self.cursor.fetchone()
            if produto:
                nova_quantidade = produto[0] - quantidade
                if nova_quantidade < 0:
                    print("Quantidade insuficiente em estoque para autorizar a compra.")
                    return

                self.cursor.execute('''
                    UPDATE produtos SET quantidade = ? WHERE id_produto = ?
                ''', (nova_quantidade, id_produto))

                # Registro de movimentação de saída
                self.cursor.execute('''
                    INSERT INTO movimentacoes (produto_id, quantidade, tipo, nota_fiscal)
                    VALUES (?, ?, 'saida', ?)
                ''', (id_produto, quantidade, nota_fiscal))
                self.conn.commit()
                print(f"Compra de {quantidade} unidades do produto {id_produto} autorizada e registrada como saída.")
            else:
                print("Produto não encontrado.")
        else:
            print("Acesso negado. Apenas gerentes de setor podem autorizar compras.")

class Usuario:
    def __init__(self, nome, senha, tipo):
        self.nome = nome
        self.senha = senha
        self.tipo = tipo

def exibir_menu():
    estoque = Estoque()

    if not estoque.carregar_usuarios():
        estoque.cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES ('estoquista', '123', 'estoquista'), ('usuario', '123', 'usuario'), ('gerente', '123', 'gerente_setor')")
        estoque.conn.commit()

    while True:
        print("\nEscolha uma opção:")
        print("1) Cadastrar Categoria")
        print("2) Cadastrar Produto")
        print("3) Consultar Produto")
        print("4) Registrar Entrada de Produto")
        print("5) Gerar Relatório de Estoque")
        print("6) Gerar Relatório de Movimentações")
        print("7) Solicitar Compra")
        print("8) Autorizar Compra")
        print("9) Sair")

        opcao = input("Digite o número da opção desejada: ")

        usuario = estoque.autenticar_usuario()
        if not usuario:
            continue

        if opcao == "1":
            estoque.cadastrar_categoria(usuario)
        elif opcao == "2":
            estoque.cadastrar_produto(usuario)
        elif opcao == "3":
            estoque.consultar_produto(usuario)
        elif opcao == "4":
            estoque.registrar_movimentacao(usuario)
        elif opcao == "5":
            estoque.gerar_relatorio_estoque(usuario)
        elif opcao == "6":
            estoque.gerar_relatorio_movimentacoes(usuario)
        elif opcao == "7":
            estoque.solicitar_compra(usuario)
        elif opcao == "8":
            estoque.autorizar_compra(usuario)
        elif opcao == "9":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

exibir_menu()