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
TAM_PAG = 1 + ((ORDEM-1)*2) + (3*ORDEM) # será arredondado para cima para garantir que o tamanho da página seja múltiplo de 4
TAM_CAB = 4

# Estrutura de uma página da árvore-B
class Pagina:
    def __init__(self) -> None:
        self.num_chaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM
        self.offsets: list = [None] * (ORDEM - 1)

def criar_indice(registros: io.BufferedRandom) -> None:
    '''
    Função que cria o índice (árvore-B) a partir do arquivo de registros
    ''' 
    pass
    
def busca_na_arvore(chave: int, rrn: int | None) -> tuple[bool, int | None, int | None]:
    '''
    Função que busca uma chave na árvore-B
    '''
    if rrn is None:
        return False, None, None
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

def insere_na_arvore(chave: int, rrn_atual: int | None) -> tuple[int, int, bool]:
    '''
    Função que insere uma chave na árvore-B
    '''
    if rrn_atual is None:
        chave_promovida = chave
        filho_d_pro = None
        return chave_promovida, filho_d_pro, True
    else:
        pag = le_pagina(rrn_atual)
        achou, pos = busca_na_pagina(chave, pag)
    if achou:
        raise ValueError('Chave duplicada')
    chave_promovida, filho_d_pro, promo = insere_na_arvore(chave, pag.filhos[pos])
    if not promo:
        return None, None, False
    else:
        if pag.num_chaves < ORDEM - 1:
            insere_na_pagina(chave_promovida, filho_d_pro, pag)
            escreve_pagina(rrn_atual, pag)
            return None, None, False
        else:
            chave_promovida, filho_d_pro, pag, nova_pag = divide(chave_promovida, filho_d_pro, pag)
            escreve_pagina(rrn_atual, pag)
            escreve_pagina(novo_rrn(), nova_pag)
            return chave_promovida, filho_d_pro, True

def le_pagina(rrn: int) -> Pagina:
    '''
    Função que lê uma página da árvore-B
    '''
    offset = TAM_CAB + (rrn * TAM_PAG)
    with open('btree.dat', 'rb') as arq_arvb:
        arq_arvb.seek(offset)
        pag = Pagina()
        pag.num_chaves = struct.unpack('B', arq_arvb.read(1))[0]
        pag.chaves = struct.unpack(f'{ORDEM - 1}I', arq_arvb.read((ORDEM - 1) * 4))
        pag.filhos = struct.unpack(f'{ORDEM}I', arq_arvb.read(ORDEM * 4))
        pag.offsets = struct.unpack(f'{ORDEM - 1}I', arq_arvb.read((ORDEM - 1) * 4))
    return pag

def escreve_pagina(rrn: int, pag: Pagina) -> None:
    '''
    Função que escreve uma página da árvore-B
    '''
    offset = TAM_CAB + (rrn * TAM_PAG)
    with open('btree.dat', 'r+b') as arq_arvb:
        arq_arvb.seek(offset)
        arq_arvb.write(struct.pack('B', pag.num_chaves))
        arq_arvb.write(struct.pack(f'{ORDEM - 1}I', *pag.chaves))
        arq_arvb.write(struct.pack(f'{ORDEM}I', *pag.filhos))
        arq_arvb.write(struct.pack(f'{ORDEM - 1}I', *pag.offsets))

def insere_na_pagina(chave: int, filho_direito: int, pag: Pagina) -> None:
    '''
    Função que insere uma chave em uma página da árvore-B
    '''
    if pag.num_chaves >= ORDEM - 1:
        pag.chaves.append(None)
        pag.filhos.append(None)
    
    i = pag.num_chaves
    
    while i > 0 and chave < pag.chaves[i - 1]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        pag.offsets[i] = pag.offsets[i - 1]
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
    Função que gerencia a inserção de uma chave na árvore-B
    '''
    arquivo_registros = 'games.dat'
    with open(arquivo_registros, 'rb') as arq_registros:
        chave = struct.unpack('I', arq_registros.read(4))[0]
        while chave != 0:
            chave_pro, filho_D_pro, promo = insere_na_arvore(chave, raiz)
            if promo:
                p_nova = Pagina()
                p_nova.chaves[0] = chave_pro
                p_nova.filhos[0] = raiz
                p_nova.filhos[1] = filho_D_pro
                p_nova.num_chaves += 1
                escreve_pagina(raiz, p_nova)
                raiz = novo_rrn()
            chave = struct.unpack('I', arq_registros.read(4))[0]
    return raiz

def principal() -> None:
    '''
    Função responsável por abrir (ou criar) o arquivo da árvore-B e chamar o gerenciador
    '''
    arquivo_arvore_b = 'btree.dat'
    pos_pagina_inicial = 4
    
    if os.path.exists(arquivo_arvore_b):
        with open(arquivo_arvore_b, 'r+b') as arq_arvb:
            raiz = struct.unpack('I', arq_arvb.read(4))[0]
            pag = le_pagina(arq_arvb, pos_pagina_inicial)
    
    else:
        with open(arquivo_arvore_b, 'w+b') as arq_arvb:
            raiz = 0
            arq_arvb.write(struct.pack('I', raiz))
            pag = Pagina()
            escreve_pagina(arq_arvb, pag, pos_pagina_inicial)
    
    raiz = gerenciador_de_insercao(raiz)
    
    with open(arquivo_arvore_b, 'r+b') as arq_arvb:
        arq_arvb.seek(0)
        arq_arvb.write(struct.pack('I', raiz))

def imprime_arvore_b(arq_arvore: io.BufferedRandom) -> str:
    '''
    Função que imprime a árvore-B
    '''
    pass

def main() -> None:
    pass

if __name__ == '__main__':
    main()