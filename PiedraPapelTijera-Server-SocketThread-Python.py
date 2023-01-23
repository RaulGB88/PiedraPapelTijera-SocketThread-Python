from curses import ERR
from optparse import OptParseError
import random
import socket
import sys
import threading
from xxlimited import Str

# Decidimos la IP y el puerto del servidor
HOST = '127.0.0.1'  # La IP del servidor es la loca de la máquina
PORT = 5008  # El puerto tiene que ser superior a 1024, por debajo estan reservados
fin_mensaje = b''

NAME = 'Dime tu nombre por favor ...: '
CHOOSE = '¿Quieres JUGAR o ver la PUNTUACIÓN? ...: '
PLAY = 'Indica qué quieres jugar: PIEDRA, PAPEL o TIJERA ...: '
ERROR_MESSAGE = 'Error. Se ha producido un error insesperado.'
CONTINUE = 'Si quieres terminar de jugar escribe: [bye] ...: '

PIEDRA = 'piedra'
PAPEL = 'papel'
TIJERA = 'tijera'
NOT_GAME = 'Error, introduce un juego válido.'

WINNER = 'Gana: '
SAME = 'Empate.'
MACHINE = 'la máquina.'
PLAYER_STR = 'jugador'

ERROR = 'ERROR'
PLAYS = 'jugar'
POINTS = 'puntuacion'
POINTSS = 'puntuación'
BYE = 'bye'

global player_count, machine_count

def server_program():

    global player_count, machine_count

    try:
        socket_escucha = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket servidor creado')
    except socket.error:
        print('Fallo en la creación del socket servidor')
        sys.exit()

    try:
        # Definimosel punto de enlace del ervidor. El servidor está preparado en la IP 127.0.0.1 y puerto 5000
        socket_escucha.bind((HOST, PORT))
    except socket.error as e:
        print('Error socket: %s' % e)
        sys.exit()
        
    # El servidor puede escuchar hasta 5 clientes. En este ejmeplo sólo escuchará a 1 y se rompe la conexión
    socket_escucha.listen(5)

    while True:
        # El Servidor queda bloquedo en esta línea esperando a que un cliente se conecte a su IP y puerto
        # Si un cliente se conecta guardamos en conn del socket y en addr la información del cliente (IP y puerto del cliente)
        socket_atiende, addr_cliente = socket_escucha.accept()

        # Ejecución con Threads.
        lock = threading.Lock()
        t = threading.Thread(target=execute, args=(lock,socket_atiende,addr_cliente))
        t.start()


def messageRecieved(socket_atiende, message):

    # Send message
    socket_atiende.sendall(message.encode())

    # Recieve message
    data = socket_atiende.recv(1024)

    mensaje = data.decode()
    return mensaje


def execute(lock, socket_atiende, addr_cliente):

    with lock:
        with socket_atiende:

            cerrar = False
            global player_count, machine_count

            while not cerrar:
                print(f'Conexión exitosa con el cliente. {addr_cliente}')

                # ---- INSCRIBIR ---- #
                # Get name of Client
                name = messageRecieved(socket_atiende, NAME)

                # Send message for name of Client
                send_message = f'[{addr_cliente}] Hola: {name}'
                messageRecieved(socket_atiende, send_message)

                player_count = 0
                machine_count = 0

                while player_count < 3 and machine_count < 3:

                    # ---- ELEGIR ---- #
                    option_selected = optionMessage(socket_atiende)

                    # ---- PUNTUACIÓN ---- # 
                    if option_selected == POINTS or option_selected == POINTSS:
                        points_message = f'Esta es la puntuación actual: JUGADOR/A: ' + str(player_count) + ' - MÁQUINA: ' + str(machine_count)
                        messageRecieved(socket_atiende, points_message)

                    # ---- JUGADA ---- #     
                    if option_selected == PLAYS:

                        game = ERROR
                        while game == ERROR:
                            # Get game of Client
                            play = messageRecieved(socket_atiende, PLAY)
                            game = playerGame(play)

                        # Send game for play of Client
                        send_message = f'[{addr_cliente}] El jugador/a: {name} ha elegido: {play}'
                        messageRecieved(socket_atiende, send_message)
                        
                        
                        randomPlay = randomGame()
                        send_message = f'La máquina ha elegido: {randomPlay}'
                        messageRecieved(socket_atiende, send_message)

                        # Turn to play player
                        winner = executePlay(play, randomPlay)

                        # Counter of games
                        if winner == MACHINE:
                            machine_count = machine_count + 1
                        elif winner == PLAYER_STR:
                            player_count = player_count + 1
                            winner = name

                        # Send winner
                        if winner != SAME:
                            winner = WINNER + winner
                        else:
                            winner = SAME
                        messageRecieved(socket_atiende, winner)

                # Puntuación final
                points_message = f'Esta es la puntuación final: JUGADOR/A: ' + str(player_count) + ' - MÁQUINA: ' + str(machine_count)
                messageRecieved(socket_atiende, points_message)

                if machine_count == 3:
                    points_message = f'Ha ganado la máquina: ' + str(machine_count) + ' a ' + str(player_count)
                else:
                    points_message = f'Ha ganado el jugador/a {name}: ' + str(player_count) + ' a ' + str(machine_count)

                messageRecieved(socket_atiende, points_message)

                # Get message to disable of Client
                message = messageRecieved(socket_atiende, CONTINUE)

                if message == fin_mensaje or message == BYE:
                    cerrar = True


def optionMessage(socket_atiende):
    option = ERROR

    while option == ERROR:
        option = messageRecieved(socket_atiende, CHOOSE)
        option = option.lower()
    
        if option != POINTS and option != POINTSS and option != PLAYS:
            option = ERROR

    return option


def playerGame(game):
    game = game.lower()

    if game == PIEDRA or game == PAPEL or game == TIJERA:
        return game
    else:
        game = ERROR
        return game


def randomGame():
    pos = random.randrange(3)
    game = PIEDRA

    if pos == 0:
        game = PIEDRA
    elif pos == 1:
        game = PAPEL
    elif pos == 2:
        game = TIJERA
    else:
        print(ERROR_MESSAGE)

    return game


def executePlay(play_one, play_two):
    global player_count, machine_count
    # PIEDRA
    if play_one == PIEDRA and play_two == PIEDRA:
        result = SAME
    elif play_one == PIEDRA and play_two == PAPEL:
        result = MACHINE
    elif play_one == PIEDRA and play_two == TIJERA:
        result = PLAYER_STR
    # PAPEL
    if play_one == PAPEL and play_two == PIEDRA:
        result = PLAYER_STR
    elif play_one == PAPEL and play_two == PAPEL:
        result = SAME
    elif play_one == PAPEL and play_two == TIJERA:
        result = MACHINE
    # TIJERA
    if play_one == TIJERA and play_two == PIEDRA:
        result = MACHINE
    elif play_one == TIJERA and play_two == PAPEL:
        player_count = player_count + 1
        result = PLAYER_STR
    elif play_one == TIJERA and play_two == TIJERA:
        result = SAME

    return result
    

if __name__ == '__main__':
    server_program()
