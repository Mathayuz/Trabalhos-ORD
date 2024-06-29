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
    dados.seek(0)
    header = dados.read(4)
    return int.from_bytes(header)

def escreve_cabecalho(dados: io.TextIOWrapper, topo: int) -> None:
    '''
    Escreve o valor do topo da lista de espaços livres (LED) no cabeçalho do arquivo de dados.dat.
    '''
    dados.seek(0)
    dados.write(topo.to_bytes(4))

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
    pass
    
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

def mostrar_led(dados: io.TextIOWrapper) -> str:
    '''
    Mostra o estado atual da lista de espaços livres (LED) no terminal da seguinte forma:
    LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
    Total: 3 espacos disponiveis.
    '''
    pass

def main() -> None:
    '''
    Função principal do programa.
    '''
    modoDeUso = 'Modo de uso: python lorenzo_zanetti_matheus_jacomini.py -e arquivo_operacoes'

    if len(argv) != 3:
        raise TypeError('Número incorreto de argumentos.'+ modoDeUso)
    
    opera_dados(open(argv[2], 'r'), open('dados.dat', 'r+b'))

if __name__ == '__main__':
    main()