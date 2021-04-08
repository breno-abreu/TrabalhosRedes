# UTFPR - 2021/1
# Bacharelado em Sistemas de Informação
# Redes de Computadores
# Trabalho 1 - Servidor Web Multithread
# Autor: Breno Moura de Abreu
# RA: 1561286
# Python 3

import threading
import socket
import os

def main():
    """ Função principal que inicia a execução do servidor """

    print('[INICIALIZANDO SERVIDOR]')

    try:
        # Tenta executar o servidor
        print('[RODANDO SERVIDOR]')
        executar_servidor()
    except KeyboardInterrupt:
        # Finaliza a execução do programa caso ^C seja pressionado no Terminal
        print('\n[DESLIGANDO SERVIDOR]')
    except Exception as exc:
        print('[ERRO] ' + str(exc))


def executar_servidor():
    """ Função que cria o socket do servidor e executa o loop principal """

    # Cria o socket do servidor, sendo AF_INET relativo ao IPv4
    # E SOCK_STREAM relativo a TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite que a mesma porta possa ser usada novamente após a execução
    # do programa. Caso essa linha não exista, deve-se trocar a porta a cada
    # vez que o programa é executado
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Descobre o IPv4 da máquina
    hostname = socket.gethostname()
    ip_servidor = socket.gethostbyname(hostname + ".local")

    # Associa o socket com um IP e uma porta
    server_socket.bind((ip_servidor, 5000))
    print('IPv4 do Servidor: ' + ip_servidor)

    # Servidor passa a ouvir requisições de clientes
    server_socket.listen()

    while True:
        # Servidor espera a requisição de um cliente
        # Socket do cliente que fez uma requisição é criado
        # A variável 'addr' guarda o IP e porta do cliente
        client_socket, addr = server_socket.accept()

        # Objeto da classe HttpRequest é criado recebendo o socket do cliente
        # A requisição do cliente então é tratada com os métodos da classe
        http_request = HttpRequest(client_socket, addr)

        # Thread é criada para tratar a requisição de cada cliente paralelamente
        thread = threading.Thread(target=http_request.run)

        # Desliga uma thread caso a thread principal seja desligada
        thread.daemon = True

        # Inicia o tratamente da requisição do cliente
        thread.start()

    # Fecha o socket do servidor
    server_socket.close()


class HttpRequest:
    """ Classe contendo os métodos para tratar uma requisição de um cliente
        e enviar os dados necessários """

    def __init__(self, client_socket, addr):
        """ Armazena o socket de um cliente e seu endereço """

        self.client_socket = client_socket
        self.addr = addr

        # Variáveis auxiliares para indicar o fim de uma linha
        self.CRLF = '\r\n'
        self.CRLF2 = '\r\n\r\n'

    def run(self):
        """ Tenta tratar a requisição de um cliente """

        try:
            self.process_request()
        except Exception as exc:
            print('[ERRO] ' + str(exc))

    def process_request(self):
        """ Trata a requisição de um cliente e retorna os dados necessários """

        # Recebe a mensagem de requisição de um cliente
        request_msg = self.client_socket.recv(4096).decode()

        # Divide a mensagem em partes
        request_vec = request_msg.split("\n")
        nome_arquivo = ''

        print('IP cliente: ' + self.addr[0])
        print('Porta cliente: ' + str(self.addr[1]))

        if len(request_vec) > 0:
            # Descobre o nome do arquivo requerido pelo cliente
            print('Requisição: ' + request_vec[0] + '\n')
            nome_arquivo = request_vec[0].split(' ')
            nome_arquivo = '.' + nome_arquivo[1]

        if self.arquivo_existe(nome_arquivo):
            # Caso o arquivo exista, envia o arquivo para o cliente

            # Adiciona a linha de status
            texto = self.status_line(200) + self.CRLF

            # Adiciona a linha contendo o tipo de conteúdo a ser enviado
            texto += 'Content-Type: ' + self.content_type_line(nome_arquivo) + self.CRLF

            # Adiciona o tamanho do arquivo a ser enviado
            texto += 'Content-Length: ' + str(os.path.getsize(nome_arquivo)) + self.CRLF2

            # Envia o cabeçalho para o cliente
            self.client_socket.sendall(texto.encode())

            # Recebe o arquivo requerido como byte stream
            arquivo = self.ler_arquivo(nome_arquivo)

            # Envia o arquivo para o cliente
            self.client_socket.sendall(arquivo)
        
        else:
            # Caso o arquivo não exista, devolve uma página com o erro 404 Not Found
            texto = self.status_line(404) + self.CRLF
            texto += "Content-Type: text/html; charset=utf-8"  + self.CRLF2
            texto += "<html><head><title>404 Not Found</title></head><body>"
            texto += "<h1>404 Not Found</h1><h2>Arquivo Não Encontrado</h2></body></html>"
            self.client_socket.sendall(texto.encode())

        # Desliga a conexão do socket do cliente
        self.client_socket.shutdown(socket.SHUT_WR)

        # Fecha o socket do cliente
        self.client_socket.close()

    def status_line(self, status):
        """ Retorna a linha de texto adequada para diferentes status de uma página """

        if status == 200:
            return "HTTP/1.0 200 OK"
        elif status == 404:
            return "HTTP/1.0 404 Not Found"

    def content_type_line(self, nome_arquivo):
        """ Identifica o tipo de conteúdo de um arquivo e retorna seu tipo MIME """

        if nome_arquivo.endswith('.htm') or nome_arquivo.endswith('.html'):
            return 'text/html; charset=utf-8'

        elif nome_arquivo.endswith('.txt'):
            return 'text/plain'

        elif nome_arquivo.endswith('.jpg'):
            return 'image/jpeg'

        elif nome_arquivo.endswith('.png'):
            return 'image/png'

        elif nome_arquivo.endswith('.gif'):
            return 'image/gif'

        elif nome_arquivo.endswith('.ogg'):
            return 'audio/ogg'
        
        elif nome_arquivo.endswith('.webm'):
            return 'audio/webm'

        elif nome_arquivo.endswith('.wav'):
            return 'video/wav'

        elif nome_arquivo.endswith('.mpeg'):
            return 'audio/mpeg'
        
        elif nome_arquivo.endswith('.pdf'):
            return 'application/pdf'
        
        return 'application/octet-stream'

    def arquivo_existe(self, nome_arquivo):
        """ Verifica se um arquivo existe ou não """

        try:
            if nome_arquivo != './':
                arquivo = open(nome_arquivo)
                arquivo.close()
                
            return True
            
        except IOError as exc:
            print('[ERRO] ' + str(exc))
            return False

    def ler_arquivo(self, nome_arquivo):
        """ Abre um arquivo e retorna seu conteúdo como byte stream """

        if(nome_arquivo != './favicon.ico'):
            if nome_arquivo == './':
                arquivo = open('./index.html', 'rb')
            else:
                arquivo = open(nome_arquivo, 'rb')

            conteudo = arquivo.read()
            arquivo.close()
            return conteudo
        
        return ''


if __name__=="__main__":
    main()