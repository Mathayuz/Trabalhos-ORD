import os
from sys import argv
import io

# O arquivo dados.dat possui informações sobre jogos. Os dados dos jogos estão armazenados
# em registros de tamanho variável. O arquivo possui um cabeçalho de 4 bytes e os campos de
# tamanho dos registros têm 2 bytes. Cada jogo possui os seguintes campos:
# 1. IDENTIFICADOR do jogo (utilizado como chave primária);
# 2. TÍTULO;
# 3. ANO;
# 4. GÊNERO;
# 5. PRODUTORA;
# 6. PLATAFORMA.
# Dado o arquivo dados.dat, o programa oferece as seguintes funcionalidades principais:
#   • Busca de um jogo pelo IDENTIFICADOR;
#   • Inserção de um novo jogo;
#   • Remoção de um jogo.
# As operações a serem realizadas em determinada execução serão especificadas em um arquivo de operações, o qual
# será passado ao programa como um parâmetro. Dessa forma, o programa não possuirá interface com o usuário e
# executará as operações na sequência em que estiverem especificadas no arquivo de operações.
# Exemplo de registro de um jogo:
#   IDENTIFICADOR: 1
#   NOME: Super Mario World
#   ANO: 1990
#   GÊNERO: Plataforma
#   PRODUTORA: Nintendo
#   PLATAFORMA: Super Nintendo
# Exemplo de arquivo de operações:
#   b 1
#   i 2|Super Mario Bros|1990|Plataforma|Nintendo|NES|
#   r 2
# O programa deverá gerar um arquivo de saída com o resultado de cada operação. Caso a operação seja de busca, o
# arquivo de saída deverá conter o registro do jogo encontrado. Caso a operação seja de inserção, o arquivo de saída
# deverá conter a mensagem “Registro inserido com sucesso”. Caso a operação seja de remoção, o arquivo de saída
# deverá conter a mensagem “Registro removido com sucesso”. Caso o registro não seja encontrado, o arquivo de saída
# deverá conter a mensagem “Registro não encontrado”.

def le_cabecalho(dados: io.TextIOWrapper) -> int:
    '''
    Lê o cabeçalho do arquivo de dados.dat que armazena o valor do topo da lista de espaços livres (LED).
    '''
    dados.seek(0, os.SEEK_SET) # Volta para o início do arquivo
    header = dados.read(4)
    return int.from_bytes(header)

def escreve_cabecalho(dados: io.TextIOWrapper, topo: int) -> None:
    '''
    Escreve o valor do topo da lista de espaços livres (LED) no cabeçalho do arquivo de dados.dat.
    '''
    dados.seek(0, os.SEEK_SET) # Volta para o início do arquivo
    dados.write(topo.to_bytes(4)) # type: ignore

def opera_dados(arquivo_operacoes: io.TextIOWrapper, dados: io.TextIOWrapper):
    '''
    Executa as operações de busca, inserção e remoção de registros no arquivo de dados.dat.
    '''
    for linha in arquivo_operacoes:
        comando = linha[0]
        if comando == 'b':
            busca_chave(int(linha[2:]), dados)
        elif comando == 'i':
            insercao_registro(linha[2:], dados)
        elif comando == 'r':
            remocao_registro(int(linha[2:]), dados)

def busca_chave(chave: int, dados: io.TextIOWrapper):
    '''
    Busca um registro com a chave especificada no arquivo de dados.dat.
    '''
    dados.seek(4, os.SEEK_SET) # Coloca o seek no primeiro registro (pula o cabeçalho)
    while True:
        offset = dados.tell() # Salva a posição atual do ponteiro
        tamanho = int.from_bytes(dados.read(2)) # type: ignore
        
        if tamanho == 0: # Se o tamanho do registro for 0, chegou ao final do arquivo
            print('Registro não encontrado')
            return
        
        identificador = -1
        aux = ''
        leitura = dados.read(1)
        while leitura != b'|': # Lê o identificador do registro
            aux += leitura.decode() # type: ignore
            leitura = dados.read(1)
        
        if aux[0] == '*': # Se o registro estiver marcado como removido, pula para o próximo registro
            identificador = -1
        else: # Caso contrário, converte o identificador para inteiro
            identificador = int(aux)

        if identificador == chave:
            print(f'Busca pelo registro com chave {chave} encontrada.')
            dados.seek(offset + 2, os.SEEK_SET) # Voltar para o início do registro caso encontrado
            print(f'{dados.read(tamanho).decode()} ({tamanho} bytes)') # type: ignore
            return
        dados.seek(offset + 2 + tamanho) # Pula para o próximo registro
    
def insercao_registro(registro: str, dados: io.TextIOWrapper):
    '''
    Insere um novo registro no arquivo de dados.dat utilizando.
    '''
    pass

def remocao_registro(chave: int, dados: io.TextIOWrapper):
    '''
    Remove o registro com a chave especificada do arquivo de dados.dat utilizando
    a estratégia 'worst-fit'.
    '''
    pass

def mostrar_led(dados: io.TextIOWrapper) -> None:
    '''
    Mostra o estado atual da lista de espaços livres (LED) no terminal da seguinte forma:
    LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
    Total: 3 espacos disponiveis.
    '''
    LED = 'LED'
    offset = le_cabecalho(dados) # Lê o valor do topo da lista de espaços livres (LED)
    espacos = 0 # Contador de espaços livres

    while offset != 4294967295: # este numero é o maior numero que pode ser representado por 4 bytes, logo é o limite do offset utilizado nesse método de organização e considerado nosso fim de pilha
        dados.seek(offset,os.SEEK_SET)
        byt = dados.read(2) # Lê o tamanho do espaço livre
        tamanho = int.from_bytes(byt) # type: ignore
        LED += f' -> [offset: {offset}, tam: {tamanho}]' # Adiciona o offset e o tamanho do espaço livre na string LED
        dados.seek(1, os.SEEK_CUR) # Pula o caractere '*' que marca o espaço livre
        byt = dados.read(4) # Lê o próximo offset
        offset = int.from_bytes(byt) # type: ignore

        
    LED += f' -> [offset: -1]\nTotal: {espacos} espacos disponiveis' # Adiciona o offset -1 e o total de espaços livres na string LED
    print(LED)


def main() -> None:
    '''
    Função principal do programa.
    '''
    modoDeUso = 'Modo de uso: \n-> python lorenzo_zanetti_matheus_jacomini.py -e arquivo_operacoes\n-> python lorenzo_zanetti_matheus_jacomini.py -p'

    if len(argv) != 3 or len(argv) != 2:
        raise TypeError('Número incorreto de argumentos.'+ modoDeUso)
    elif argv[1] == '-e':
        opera_dados(open(argv[2], 'r'), open('dados.dat', 'r+b')) # type: ignore
    elif argv[1] == '-p':
        mostrar_led(open('dados.dat', 'r+b')) # type: ignore
    else:
        raise TypeError('Argumento inválido.'+ modoDeUso)

if __name__ == '__main__':
    main()