import os
import io
from sys import argv
import struct

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

def insere_na_arvore(chave: int, rrn_atual: int, byte_offset: int) -> tuple[int, int, bool, int]:
    '''
    Função que insere uma chave na árvore-B
    '''
    if rrn_atual == -1:
        chave_pro = chave
        filho_d_pro = -1
        return chave_pro, filho_d_pro, True, byte_offset
    else:
        pag = le_pagina(rrn_atual)
        achou, pos = busca_na_pagina(chave, pag)
    if achou:
        raise ValueError('Chave duplicada')
    chave_pro, filho_d_pro, promo, byte_offset = insere_na_arvore(chave, pag.filhos[pos], byte_offset)
    if not promo:
        return -1, -1, False, -1
    else:
        if pag.num_chaves < ORDEM - 1:
            insere_na_pagina(chave_pro, filho_d_pro, pag, byte_offset)
            escreve_pagina(rrn_atual, pag)
            return -1, -1, False, -1
        else:
            chave_pro, filho_d_pro, pag, nova_pag, byte_offset_pro = divide(chave_pro, filho_d_pro, pag, byte_offset)
            escreve_pagina(rrn_atual, pag)
            escreve_pagina(novo_rrn(), nova_pag)
            return chave_pro, filho_d_pro, True, byte_offset_pro

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

def insere_na_pagina(chave: int, filho_direito: int, pag: Pagina, byte_offset: int) -> None:
    '''
    Função que insere uma chave em uma página da árvore-B
    '''
    if pag.num_chaves >= ORDEM - 1:
        pag.chaves.append(-1)
        pag.filhos.append(-1)
        pag.offsets.append(-1)
    
    i = pag.num_chaves
    
    while i > 0 and chave < pag.chaves[i - 1]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        pag.offsets[i] = pag.offsets[i - 1]
        i -= 1
    
    pag.chaves[i] = chave
    pag.filhos[i + 1] = filho_direito
    pag.offsets[i] = byte_offset
    
    pag.num_chaves += 1

def divide(chave: int, filho_direito: int, pag: Pagina, byte_offset: int) -> tuple[int, int, Pagina, Pagina, int]:
    '''
    Função que divide uma página da árvore-B
    '''
    insere_na_pagina(chave, filho_direito, pag, byte_offset)
    meio = ORDEM // 2
    chave_promovida = pag.chaves[meio]
    byte_offset_pro = pag.offsets[meio]
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

    return chave_promovida, filho_d_pro, p_atual, p_nova, byte_offset_pro

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
    arquivo_registros = 'games20.dat'
    with open(arquivo_registros, 'rb') as arq_registros:
        arq_registros.seek(4) # Pula o cabeçalho
        byte_offset = arq_registros.tell()
        tam_registro = struct.unpack('h', arq_registros.read(2))[0] # Lê o tamanho do registro
        registro = arq_registros.read(tam_registro) # Lê o registro
        chave = int(registro.decode().split('|')[0])
        while chave: # Enquanto houver chaves
            chave_promovida, filho_d_pro, promo, byte_offset_pro = insere_na_arvore(chave, raiz, byte_offset) # Insere a chave na árvore
            if promo: # Se houve promoção
                p_nova = Pagina() # Cria uma nova página
                p_nova.num_chaves = 1
                p_nova.chaves[0] = chave_promovida
                p_nova.filhos[0] = raiz
                p_nova.filhos[1] = filho_d_pro
                p_nova.offsets[0] = byte_offset_pro
                raiz = novo_rrn() # Atualiza a raiz
                escreve_pagina(raiz, p_nova)
            byte_offset = arq_registros.tell()
            prox_tam = arq_registros.read(2)
            if not prox_tam:
                break
            tam_registro = struct.unpack('h', prox_tam)[0] # Lê o tamanho do registro
            registro = arq_registros.read(tam_registro)
            chave = int(registro.decode().split('|')[0])
    return raiz

def cria_indice() -> None:
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

    print('Índice "btree.dat" criado com sucesso!')

# ---------------Execução do arquivo de operações (funcionalidade -e)------------------------
def executa_operacoes(arq_operacoes: io.TextIOWrapper) -> None:
    '''
    Função que executa as operações de inserção e busca na árvore-B
    '''
    pass

def inserir_registro(reg: str) -> None:
    '''
    Função auxiliar que insere um registro no final do arquivo de registros
    '''
    try:
        with open('games20.dat', 'a+b') as arq_registros:
            tam_registro = len(reg)
            arq_registros.write(struct.pack('h', tam_registro))
            arq_registros.write(reg.encode())
    except FileNotFoundError:
        print('Arquivo de registros não encontrado')
# -------------------------------------------------------------------------------------------

# -------------Impressão das informações da árvore-B (funcionalidade -p)---------------------
def imprime_arvore_b(arq_arvb: io.BufferedRandom) -> None:
    '''
    Função que imprime a árvore-B
    '''
    arq_arvb.seek(0)
    raiz = struct.unpack('i', arq_arvb.read(4))[0]
    if raiz == -1:
        print('Árvore vazia')
        return
    else:
        num_paginas = 0
        while arq_arvb:
            arq_arvb.seek(TAM_CAB + (num_paginas * TAM_PAG))
            pagina = le_pagina(num_paginas)
            if num_paginas == raiz:
                print('\n- - - - - - - - - - Raiz  - - - - - - - - - -')
                print(f"Pagina {num_paginas}:")
                imprime_pagina(pagina)
                print('- - - - - - - - - - - - - - - - - - - - - - -')
            else:
                print(f"\nPagina {num_paginas}:")
                imprime_pagina(pagina)
            num_paginas += 1
    
def imprime_pagina(pagina: Pagina) -> None:
    '''
    Função que imprime uma página da árvore-B
    '''
    print('Chaves:', pagina.chaves)
    print('Offsets:', pagina.offsets)
    print('Filhos:', pagina.filhos)
# ------------------------------------------------------------------------------------------

def main() -> None:
    '''
    Função principal
    '''
    modoDeUso = '''Modo de uso: 
    -> python lorenzo_zanetti_matheus_jacomini_2.py -c
    -> python lorenzo_zanetti_matheus_jacomini_2.py -e <arquivo_de_operacoes>
    -> python lorenzo_zanetti_matheus_jacomini_2.py -p'''
    if len(argv) < 2 or len(argv) > 3:
        raise TypeError("Número de argumentos inválido\n" + modoDeUso)
    elif argv[1] == '-c':
        cria_indice()
    elif argv[1] == '-e':
        try:
            arq_operacoes = open(argv[2], 'r')
            executa_operacoes(arq_operacoes)
        except FileNotFoundError:
            raise FileNotFoundError('Arquivo de operações não encontrado')
    elif argv[1] == '-p':
        try:
            arq_arvb = open('btree.dat', 'rb')
            imprime_arvore_b(arq_arvb)
        except FileNotFoundError:
            raise FileNotFoundError('Arquivo da árvore-B não encontrado')
    else:
        raise ValueError('Argumento inválido\n' + modoDeUso)

if __name__ == '__main__':
    main()