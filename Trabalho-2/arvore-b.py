import os
import io
from sys import argv
import struct

'''
O  objetivo  deste  trabalho  é  criar  um  programa  que,  a  partir  de  um  arquivo  de  registros,  construa  e  mantenha  um 
índice estruturado como uma árvore-B.  
O  arquivo  de  registros  conterá  informações  sobre  jogos  e  estará  armazenado  no  arquivo  games.dat  no  mesmo 
formato do arquivo dados.dat utilizado no 1º trabalho prático. Para cada registro lido, a chave (o identificador do jogo) 
deverá ser inserida em uma árvore-B de determinada ORDEM, juntamente com o byte-offset do registro 
correspondente.  Para  facilitar  a  experimentação  com  árvores  de  diferentes  ordens,  defina  ORDEM  como  uma 
constante e use-a ao longo do código sempre que precisar referenciar a ordem da árvore. Esteja ciente de que o seu 
programa será testado com árvores de diferentes ordens. 
A estrutura interna das páginas da árvore-B será similar à vista em aula, porém deverá conter, adicionalmente, uma 
lista para o armazenamento dos byte-offsets dos registros. A árvore-B deverá ser criada e mantida em arquivo, logo, 
nunca estará completamente carregada na memória. 
O programa deverá oferecer as seguintes funcionalidades: 
● Criação do índice (árvore-B) a partir do arquivo de registros (opção -c); 
● Execução de um arquivo de operações (apenas busca e inserção) (opção -e); 
● Impressão das informações do índice, i.e., da árvore-B (opção -p).
sendo programa o nome do arquivo executável do seu programa. Sempre que ativada, essa funcionalidade fará a
leitura do arquivo games.dat para a construção do índice, i.e., inserção dos pares {chave, byte-offset} na árvore-B que
deverá ser armazenada no arquivo btree.dat. Caso o arquivo btree.dat exista, ele deverá ser sobrescrito. Note que o
formato do arquivo games.dat será sempre o mesmo, porém o número de registros nesse arquivo pode variar. Para
simplificar o processamento do arquivo de registros, considere que ele sempre será fornecido corretamente (i.e., o
seu programa não precisa verificar a integridade desse arquivo) e que ele armazenará o total de registros do arquivo
no cabeçalho como um número inteiro de 4 bytes. Neste trabalho, não serão feitas remoções e, consequentemente,
não haverá gerenciamento de espaços disponíveis.
Ao final da criação do índice, o programa deverá apresentar uma mensagem na tela indicando se essa operação foi
concluída com sucesso ou não.
Dados os arquivos games.dat e btree.dat, o seu programa deverá executar as seguintes operações:
• Busca de um jogo pelo IDENTIFICADOR;
• Inserção de um novo jogo.
As operações a serem realizadas em determinada execução serão especificadas em um arquivo de operações no
mesmo formato utilizado no 1o trabalho. Dessa forma, o programa não possuirá interface com o usuário e executará
as operações na sequência em que estiverem especificadas no arquivo de operações.
A execução do arquivo de operações será acionada pela linha de comando, no seguinte formato:
$ programa -c

sendo programa o nome do arquivo executável do seu programa, -e a flag que sinaliza o modo de execução e
nome_arquivo_operacoes o nome do arquivo que contém as operações a serem executadas. Para simplificar o
processamento do arquivo de operações, considere que ele sempre será fornecido corretamente (i.e., o seu programa
não precisa verificar a integridade desse arquivo).
Observe que, para esse tipo de execução, os arquivos games.dat e btree.dat devem existir. Caso eles não existam, o
programa deve apresentar uma mensagem de erro e terminar.
'''

# constante ORDEM da árvore
ORDEM = 5

# Estrutura de uma página da árvore-B
class Pagina:
    def __init__(self) -> None:
        self.num_chaves = 0
        self.chaves = [None] * (ORDEM - 1)
        self.filhos = [None] * ORDEM
        self.offsets = [None] * (ORDEM - 1)

def criar_indice():
    pass

def busca_na_arvore(chave, rrn):
    pass

def busca_na_pagina(chave, pag):
    pass

def insere_na_arvore(chave, rrn_atual):
    pass

def le_pagina(rrn):
    pass

def escreve_pagina(rrn, pag):
    pass

def insere_na_pagina(chave, filho_direito, pag):
    pass

def divide(chave, filho_direito, pag):
    pass

def novo_rrn():
    pass

def gerenciador_de_insercao(raiz):
    pass

def principal():
    pass

def main():
    pass