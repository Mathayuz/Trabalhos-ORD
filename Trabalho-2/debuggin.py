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

# Constantes
ORDEM = 5
TAM_PAG = 4 + ((ORDEM-1) * 4) + ((ORDEM-1) * 4) + (ORDEM * 4)
TAM_CAB = 4

# Estrutura de uma página da árvore-B
class Pagina:
    def __init__(self) -> None:
        self.num_chaves: int = 0
        self.chaves: list = [-1] * (ORDEM - 1)
        self.filhos: list = [-1] * ORDEM
        self.offsets: list = [-1] * (ORDEM - 1)
  
def busca_na_arvore(chave: int, rrn: int) -> tuple[bool, int, int]:
    '''
    Função que busca uma chave na árvore-B
    '''
    if rrn == -1:
        return False, -1, -1
    else:
        pag = le_pagina(rrn)
        achou, pos = busca_na_pagina(chave, pag)
        if achou:
            return True, rrn, pos
        else:
            return busca_na_arvore(chave, pag.filhos[pos])

def busca_na_pagina(chave: int, pag: Pagina) -> tuple[bool, int]:
    '''
    Função que busca uma chave em uma página da árvore-B
    '''
    pos = 0
    while pos < pag.num_chaves and chave > pag.chaves[pos]:
        pos += 1
    if pos < pag.num_chaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos

def insere_na_arvore(chave: int, rrn_atual: int) -> tuple[int, int, bool]:
    '''
    Função que insere uma chave na árvore-B
    '''
    if rrn_atual == -1:
        chave_promovida = chave
        filho_d_pro = -1
        return chave_promovida, filho_d_pro, True
    else:
        pag = le_pagina(rrn_atual)
        achou, pos = busca_na_pagina(chave, pag)
    if achou:
        raise ValueError('Chave duplicada')
    chave_promovida, filho_d_pro, promo = insere_na_arvore(chave, pag.filhos[pos])
    if not promo:
        return -1, -1, False
    else:
        if pag.num_chaves < ORDEM - 1:
            insere_na_pagina(chave_promovida, filho_d_pro, pag)
            escreve_pagina(rrn_atual, pag)
            return -1, -1, False
        else:
            chave_promovida, filho_d_pro, pag, nova_pag = divide(chave_promovida, filho_d_pro, pag)
            escreve_pagina(rrn_atual, pag)
            escreve_pagina(novo_rrn(), nova_pag)
            return chave_promovida, filho_d_pro, True

def le_pagina(rrn: int) -> Pagina:
    offset = TAM_CAB + (rrn * TAM_PAG)
    with open('btree.dat', 'rb') as arq_arvb:
        arq_arvb.seek(offset)
        dados = arq_arvb.read(TAM_PAG)

        desempacotados = struct.unpack(f'<i{ORDEM - 1}i{ORDEM}i{ORDEM - 1}i', dados)

        pag = Pagina()
        pag.num_chaves = desempacotados[0]
        pag.chaves = list(desempacotados[1:ORDEM])
        pag.filhos = list(desempacotados[ORDEM:2 * ORDEM])
        pag.offsets = list(desempacotados[2 * ORDEM:])
    return pag

def escreve_pagina(rrn: int, pag: Pagina) -> None:
    '''
    Função que escreve uma página da árvore-B
    '''
    offset = TAM_CAB + (rrn * TAM_PAG)
    with open('btree.dat', 'r+b') as arq_arvb:
        arq_arvb.seek(offset, os.SEEK_SET)
        empacotados = struct.pack(f'<i{ORDEM - 1}i{ORDEM}i{ORDEM - 1}i', pag.num_chaves, *pag.chaves, *pag.filhos, *pag.offsets)
        arq_arvb.write(empacotados)

def insere_na_pagina(chave: int, filho_direito: int, pag: Pagina) -> None:
    '''
    Função que insere uma chave em uma página da árvore-B
    '''
    if pag.num_chaves >= ORDEM - 1:
        pag.chaves.append(-1)
        pag.filhos.append(-1)
    
    i = pag.num_chaves
    
    while i > 0 and chave < pag.chaves[i - 1]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        i -= 1
    
    pag.chaves[i] = chave
    pag.filhos[i + 1] = filho_direito
    
    pag.num_chaves += 1

def divide(chave: int, filho_direito: int, pag: Pagina) -> tuple[int, int, Pagina, Pagina]:
    '''
    Função que divide uma página da árvore-B
    '''
    insere_na_pagina(chave, filho_direito, pag)
    meio = ORDEM // 2
    chave_promovida = pag.chaves[meio]
    filho_d_pro = novo_rrn()

    p_atual = Pagina()
    p_nova = Pagina()

    p_atual.num_chaves = meio
    p_atual.chaves = pag.chaves[:meio]
    p_atual.filhos = pag.filhos[:meio + 1]
    p_atual.offsets = pag.offsets[:meio]

    p_nova.num_chaves = ORDEM - meio - 1
    p_nova.chaves = pag.chaves[meio + 1:]
    p_nova.filhos = pag.filhos[meio + 1:]
    p_nova.offsets = pag.offsets[meio + 1:]

    while len(p_atual.chaves) < ORDEM - 1:
        p_atual.chaves.append(-1)
    while len(p_atual.filhos) < ORDEM:
        p_atual.filhos.append(-1)
    while len(p_atual.offsets) < ORDEM - 1:
        p_atual.offsets.append(-1)
    
    while len(p_nova.chaves) < ORDEM - 1:
        p_nova.chaves.append(-1)
    while len(p_nova.filhos) < ORDEM:
        p_nova.filhos.append(-1)
    while len(p_nova.offsets) < ORDEM - 1:
        p_nova.offsets.append(-1)

    return chave_promovida, filho_d_pro, p_atual, p_nova

def novo_rrn() -> int:
    '''
    Função que retorna um novo RRN para uma página nova da árvore-B
    '''
    with open('btree.dat', 'r+b') as arq_arvb:
        arq_arvb.seek(0, io.SEEK_END)
        offset = arq_arvb.tell()
        rrn = (offset - TAM_CAB) // TAM_PAG
    return rrn

def gerenciador_de_insercao(raiz: int) -> int:
    '''
    Função que gerencia a inserção de chaves na árvore-B
    '''
    arquivo_registros = 'games.dat'
    with open(arquivo_registros, 'rb') as arq_registros:
        arq_registros.seek(4) # Pula o cabeçalho
        tam_registro = struct.unpack('h', arq_registros.read(2))[0] # Lê o tamanho do registro
        # possui um erro aqui, pois estamos lendo o valor do tamanho do registro, mas não estamos lendo o registro em si
        chave = struct.unpack('h', arq_registros.read(2))[0] # Lê a chave do registro
        while chave: # Enquanto houver chaves
            chave_promovida, filho_d_pro, promo = insere_na_arvore(chave, raiz) # Insere a chave na árvore
            if promo: # Se houve promoção
                p_nova = Pagina()
                p_nova.num_chaves = 1
                p_nova.chaves[0] = chave_promovida
                p_nova.filhos[0] = raiz
                p_nova.filhos[1] = filho_d_pro
                escreve_pagina(raiz, p_nova)
                raiz = novo_rrn()
            arq_registros.seek(tam_registro - 4, io.SEEK_CUR) # Pula o restante do registro
            chave = struct.unpack('h', arq_registros.read(2))[0] # Lê a chave do próximo registro
    return raiz

def principal() -> None:
    '''
    Função responsável por abrir (ou criar) o arquivo da árvore-B e chamar o gerenciador
    '''
    with open('btree.dat', 'w+b') as arq_arvb:
        raiz = 0
        arq_arvb.write(struct.pack('<i', raiz))
        pag = Pagina()
        arq_arvb.write(struct.pack('<i', pag.num_chaves))
        arq_arvb.write(struct.pack(f'<{ORDEM - 1}i', *pag.chaves))
        arq_arvb.write(struct.pack(f'<{ORDEM}i', *pag.filhos))
        arq_arvb.write(struct.pack(f'<{ORDEM - 1}i', *pag.offsets))
    
    raiz = gerenciador_de_insercao(raiz)
    with open('btree.dat', 'r+b') as arq_arvb:
        arq_arvb.seek(0)
        arq_arvb.write(struct.pack('<i', raiz))

def executa_operacoes(arq_operacoes: io.BufferedRandom) -> None:
    '''
    Função que executa as operações de busca e inserção de um arquivo de operações
    '''
    pass

def imprime_arvore_b(arq_arvore: io.BufferedRandom) -> str:
    '''
    Função que imprime a árvore-B
    '''
    pass

principal()