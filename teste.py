import os
from sys import argv
import io

def le_cabecalho(dados: io.TextIOWrapper) -> int:
    '''
    Lê o cabeçalho do arquivo de dados.dat que armazena o valor do topo da lista de espaços livres (LED).
    '''
    dados.seek(0, os.SEEK_SET) # Volta para o início do arquivo
    header = dados.read(4)
    return int.from_bytes(header, signed=True)

def opera_dados(arquivo_operacoes: io.TextIOWrapper, dados: io.TextIOWrapper):
    '''
    Executa as operações de busca, inserção e remoção de registros no arquivo de dados.dat.
    '''
    for linha in arquivo_operacoes:
        comando = linha[0]
        if comando == 'b':
            #busca_chave(int(linha[2:]), dados)
            print("forgers")
        elif comando == 'i':
            #insercao_registro(linha[2:], dados)
            print("foggers")
        elif comando == 'r':
            #remocao_registro(int(linha[2:]), dados)
            print("forggers")

def busca_chave(chave: int, dados: io.TextIOWrapper):
    '''
    Busca um registro com a chave especificada no arquivo de dados.dat.
    '''
    dados.seek(4, os.SEEK_SET) # Coloca o seek no primeiro registro (pula o cabeçalho)
    while True:
        offset = dados.tell() # Salva a posição atual do ponteiro
        tamanho = int.from_bytes(dados.read(2))
        
        if tamanho == 0: # Se o tamanho do registro for 0, chegou ao final do arquivo
            print('Registro não encontrado')
            return
        
        identificador = -1
        aux = ''
        leitura = dados.read(1)
        while leitura != b'|': # Lê o identificador do registro
            aux += leitura.decode()
            leitura = dados.read(1)
        
        if aux[0] == '*': # Se o registro estiver marcado como removido, pula para o próximo registro
            identificador = -1
        else: # Caso contrário, converte o identificador para inteiro
            identificador = int(aux)

        if identificador == chave:
            print(f'Busca pelo registro com chave {chave} encontrada.')
            dados.seek(offset + 2, os.SEEK_SET) # Voltar para o início do registro caso encontrado
            print(f'{dados.read(tamanho).decode()} ({tamanho} bytes)')
            return
        dados.seek(offset + 2 + tamanho) # Pula para o próximo registro

def mostrar_led(dados: io.TextIOWrapper) -> None:
    '''
    Mostra o estado atual da lista de espaços livres (LED) no terminal da seguinte forma:
    LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
    Total: 3 espacos disponiveis.
    '''
    LED = 'LED'
    offset = le_cabecalho(dados) # Lê o valor do topo da lista de espaços livres (LED)
    espacos = 0 # Contador de espaços livres

    while offset != -1: # este numero é o maior numero que pode ser representado por 4 bytes, logo é o limite do offset utilizado nesse método de organização e considerado nosso fim de pilha
        dados.seek(offset,os.SEEK_SET)
        byt = dados.read(2) # Lê o tamanho do espaço livre
        tamanho = int.from_bytes(byt)
        LED += f' -> [offset: {offset}, tam: {tamanho}]' # Adiciona o offset e o tamanho do espaço livre na string LED
        dados.seek(1, os.SEEK_CUR) # Pula o caractere '*' que marca o espaço livre
        byt = dados.read(4) # Lê o próximo offset
        offset = int.from_bytes(byt, signed=True)
        espacos += 1

        
    LED += f' -> [offset: -1]\nTotal: {espacos} espacos disponiveis' # Adiciona o offset -1 e o total de espaços livres na string LED
    print(LED)


op = open("arquivo_operacoes", "r")
dados = open("dados.dat", "r+b")
busca_chave(22, dados)
mostrar_led(dados)