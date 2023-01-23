import random
import socket
import sys

from setuptools import sic

HOST = '127.0.0.1'
PORT = 5008

NAME = 'Dime tu nombre por favor ...: '
CHOOSE = '¿Quieres JUGAR o ver la PUNTUACIÓN? ...: '
PLAY = 'Indica qué quieres jugar: PIEDRA, PAPEL o TIJERA ...: '
CONTINUE = 'Si quieres terminar de jugar escribe: [bye] ...: '

PLAYS = 'jugar'
POINTS = 'puntuacion'
POINTSS = 'puntuación'
BYE = 'bye'


def client_program():
    try:
        # 1- Creamos el Socket.
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket cliente creado')
    except socket.error:
        print('Fallo en la creación del socket cliente')
        sys.exit()

    # 2- Conectamos el Socket cliente al servidor
    socket_cliente.connect((HOST, PORT))

    execute(socket_cliente)


def execute(socket_cliente):
    
    init_message = 'Conectado con el servidor' # El programa cliente escribe esto al servidor

    with socket_cliente:
        while init_message != BYE:
        
            # Recieve data
            data = socket_cliente.recv(1024)

            # Get message
            message = treatMessage(data.decode())

            if message == BYE:
                init_message = BYE

            # Recieve data
            socket_cliente.sendall(message.encode())

            
def treatMessage(message):

    send_message = ''

    if message == NAME or message == PLAY or message == CONTINUE or message == CHOOSE:
        send_message = input(message)
        return send_message.lower()
    elif message != '':
        print(message)
        return message


if __name__ == '__main__':
    client_program()
