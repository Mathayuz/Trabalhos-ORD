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
    return int.from_bytes(header, signed=True)

def escreve_cabecalho(dados: io.TextIOWrapper, topo: int) -> None:
    '''
    Escreve o valor do topo da lista de espaços livres (LED) no cabeçalho do arquivo de dados.dat.
    '''
    dados.seek(0, os.SEEK_SET) # Volta para o início do arquivo
    dados.write(topo.to_bytes(4, signed=True)) # type: ignore

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

def busca_chave(chave: int, dados: io.TextIOWrapper) -> None:
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
    Inserção do registro de chave "181" (35 bytes) 
    Tamanho do espaço reutilizado: 94 bytes (Sobra de 57 bytes) 
    Local: offset = 6290 bytes (0x1892) 
    '''
    try:
        insercao_led(registro, dados)
    except ValueError:
        insercao_fim(registro, dados)


def insercao_fim(registro: str, dados: io.TextIOWrapper) -> None:
    '''
    Insere um novo registro no final do arquivo de dados.dat.
    '''
    dados.seek(0, os.SEEK_END) # Coloca o seek no final do arquivo
    tamanho = len(registro) # Calcula o tamanho do registro
    dados.write(tamanho.to_bytes(2)) # Escreve o tamanho do registro
    dados.write(registro.encode()) # Escreve o registro no arquivo

    # printa a mensagem
    reg = ''
    letra = registro[0]
    cont = 0
    while letra != '|':
        reg += letra
        cont += 1
        letra = registro[cont]

    print(f'Inserção do registro de chave "{reg}" ({tamanho} bytes)')
    print('Local: fim do arquivo')


def insercao_led(registro: str, dados: io.TextIOWrapper) -> None:
    '''
    Tenta inserir um novo registro no arquivo de dados.dat utilizando a estratégia 'worst-fit'.
    '''
    cab = le_cabecalho(dados) # Lê o valor do topo da lista de espaços livres (LED)
    if cab == -1: # Se a LED estiver vazia, não é possível inserir
        tam = -1
    else: # Se a LED não estiver vazia, lê o tamanho do primeiro espaço livre
        dados.seek(cab, os.SEEK_SET) # Coloca o seek no primeiro espaço livre
        tam = int.from_bytes(dados.read(2)) # Lê o tamanho do espaço livre

    if tam < len(registro): # Se o espaço livre for menor que o registro, não é possível inserir
        raise ValueError('Espaço insuficiente para inserir o registro.')
    
    elif tam - len(registro) < 12: # Se o espaço livre for suficiente, mas restar menos de 12 bytes, o espaço restante será preenchido.
        dados.seek(1, os.SEEK_CUR) # Pula o caractere '*' que marca o espaço livre
        prox_led = dados.read(4) # lê o próximo offset da LED
        escreve_cabecalho(dados, int.from_bytes(prox_led, signed=True)) # Atualiza o topo da LED

        dados.seek(cab, os.SEEK_SET) # Volta para o início do espaço livre
        dados.read(2) # Pula o tamanho do espaço livre
        registro = registro.encode() # Converte o registro para bytes
        registro = registro.ljust(tam, b'\0') # preenche o espaço restante com bytes nulos
        dados.write(registro) # Escreve o registro no espaço livre

    else: # Se o espaço livre for suficiente e restar mais de 12 bytes, o espaço será dividido.
        dados.seek(1, os.SEEK_CUR) # Pula o caractere '*' que marca o espaço livre
        prox_led = dados.read(4) # lê o próximo offset da LED
        escreve_cabecalho(dados, int.from_bytes(prox_led, signed=True)) # Atualiza o topo da LED
        
        dados.seek(cab, os.SEEK_SET) # Volta para o início do espaço livre
        dados.write((len(registro)).to_bytes(2)) # Escreve o tamanho do novo registro
        dados.write(registro.encode()) # Escreve o registro no espaço livre

        novo_led = cab + len(registro) + 2 # Calcula o offset do novo espaço livre
        dados.seek(novo_led, os.SEEK_SET) # Coloca o seek no novo espaço livre
        dados.write((tam - len(registro) - 2).to_bytes(2)) # Escreve o tamanho do novo espaço livre
        dados.write(b'*') # Marca o espaço livre
        atualiza_led(dados, novo_led) # Atualiza a LED

    # printa a mensagem
    reg = ''
    letra = registro[0]
    cont = 0
    while letra != '|':
        reg += letra
        cont += 1
        letra = registro[cont]

    print(f'Inserção do registro de chave "{reg}" ({len(registro)} bytes)')
    print(f'Tamanho do espaço reutilizado: {tam} bytes (Sobra de {tam - len(registro) - 2} bytes)')
    print(f'Local: offset = {cab} bytes (0x{cab:04X})')
    

def atualiza_led(dados: io.TextIOWrapper, offset: int) -> None:
    '''
    Atualiza a lista de espaços livres (LED) inserindo um novo espaço livre. A LED é organizada em ordem decrescente.
    '''
    dados.seek(offset, os.SEEK_SET) # Coloca o seek no novo espaço livre
    tam = int.from_bytes(dados.read(2)) # Lê o tamanho do novo espaço livre

    led = le_cabecalho(dados) # Lê o valor do topo da LED
    tam_led = -1 # Inicializa o tamanho da LED

    if led == -1: # Se a LED estiver vazia, o novo espaço livre será o único
        escreve_cabecalho(dados, offset) # Atualiza o topo da LED
        dados.seek(offset + 3, os.SEEK_SET) # Pula o tamanho do espaço livre e o caractere '*'
        dados.write(led.to_bytes(4, signed=True)) # Escreve -1 no próximo offset da LED
        return
    else:
        dados.seek(led, os.SEEK_SET)
        tam_led = int.from_bytes(dados.read(2)) # Lê o tamanho do primeiro espaço livre da LED

    if tam >= tam_led: # Se o novo espaço livre for maior que o primeiro espaço livre da LED, o novo espaço será o primeiro
        escreve_cabecalho(dados, offset) # Atualiza o topo da LED
        dados.seek(offset + 3, os.SEEK_SET) # Pula o tamanho do espaço livre e o caractere '*'
        dados.write(led.to_bytes(4, signed=True)) # Escreve o próximo offset da LED
        return
    
    # aqui, o seek está logo após o tamanho do primeiro espaço livre da LED
    while True: # Procura o lugar correto para inserir o novo espaço livre
        dados.seek(1, os.SEEK_CUR) # Pula o caractere '*' que marca o espaço livre
        prox_led = int.from_bytes(dados.read(4), signed=True) # Lê o próximo offset da LED

        if prox_led == -1: # Se o próximo offset for -1, o novo espaço livre será o último
            dados.seek(-4, os.SEEK_CUR) # Volta para o próximo offset
            dados.write(offset.to_bytes(4, signed=True)) # Escreve o offset do novo espaço livre
            dados.seek(offset + 3, os.SEEK_SET) # Pula o tamanho do espaço livre e o caractere '*'
            dados.write(-1 .to_bytes(4, signed=True)) # Escreve -1 no próximo offset da LED
            return
        
        else: # Se o próximo offset não for -1, lê o tamanho do próximo espaço livre
            dados.seek(prox_led, os.SEEK_SET)
            tam_prox_led = int.from_bytes(dados.read(2)) # Lê o tamanho do próximo espaço livre
            
            if tam >= tam_led: # Se o novo espaço livre for maior que o próximo espaço livre, o novo espaço será inserido
                dados.seek(led + 3, os.SEEK_SET) # Volta para o primeiro espaço livre da LED
                dados.write(offset.to_bytes(4, signed=True)) # Escreve o offset do novo espaço livre
                dados.seek(offset + 3, os.SEEK_SET) # Pula o tamanho do espaço livre e o caractere '*'
                dados.write(prox_led.to_bytes(4, signed=True)) # Escreve o próximo offset do novo espaço livre
                return

            else: # Se o novo espaço livre não for maior que o próximo espaço livre, continua procurando
                led = prox_led
                tam_led = tam_prox_led


def remocao_registro(chave: int, dados: io.TextIOWrapper):
    '''
    Remove o registro com a chave especificada do arquivo de dados.dat utilizando
    a estratégia 'worst-fit'.
    '''
    # busca o registro



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