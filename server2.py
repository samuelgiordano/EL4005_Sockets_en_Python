#!/usr/bin/python3
import socket
import sys
import select

# Message Buffer size
MSG_BUFFER = 1024

#Lista de sockets
SOCKET_LIST = []

# Obtaining the arguments using command line
try:
    HOST = sys.argv[1]
except:
    HOST = 'localhost'
try:
    PORT = int(sys.argv[2])
except:
    PORT = 9998

# Creating the client socket. AF_INET IP Family (v4)
# and STREAM SOCKET Type.
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((HOST, PORT))
serverSocket.listen(10)

# Incluir objeto socket del servidor a la lista de conexiones
SOCKET_LIST.append(serverSocket)

# lista con nombres de usuario y identificadores
Identif = []
Nicknames = []

# Función para enviar mensajes a todos los clientes
def transmitir (server_socket, sock, nombre, msj):
    for socket in SOCKET_LIST:
        # descarte de destinatarios: servidor y self
        if socket != server_socket and socket != sock :
            try :
            	comp = '<'+nombre+'>: '+msj
            	socket.send(comp.encode('utf8'))
            except :
                # cierra el socket si esta inactivo
                socket.close()
                # y se remueve de la lista de sockets
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

print('\nServidor escuchando en %s: %s' % (HOST, PORT))

while True:
	
	# usamos select para delegar del mantenenimiento el estado del socket al sistema operativo
	readers, _ , _ = select.select(SOCKET_LIST,[],[])
		
	for actual in readers:
		if actual is serverSocket:
			# cuando la iteración pasa por el servidor revisamos las nuevas conexiones
			sclient, addr = serverSocket.accept()  # Acepting client
	
			#sclient.setblocking(0)
			SOCKET_LIST.append(sclient)
			
			# mensaje de bienvenida para el nuevo cliente
			welc = 'Welcome to the best chat in the universe!'
			sclient.send(welc.encode('utf8'))
			
			Nick = sclient.recv(MSG_BUFFER).decode('utf8')

			while Nick in Nicknames:
				in_use = 'yes'
				sclient.send(in_use.encode('utf8'))
				Nick = sclient.recv(MSG_BUFFER).decode('utf8')

			in_use = 'no'
			sclient.send(in_use.encode('utf8'))
			
			# agregamos el identificador y el nombre del nuevo cliente a las listas respectivas
			Identif.append(addr[1])
			Nicknames.append(Nick)

			print("\n[SERVER] Cliente <%s,%s> connectado!\n" % (Nick, addr[1]))

		else:
			addr = actual.getpeername() # obtenemos a la tupla que contiene al identificador del cliente
			lugar = Identif.index(addr[1]) # obtenemos el indice del identificador
			nombre = Nicknames[lugar] # como es el mismo, usamos el indice del indentificador para obtener el nombre
			
			msg = actual.recv(MSG_BUFFER).decode('utf8') 

			# Si el mensaje es alguno de los comandos:

			# solicitud de desconexión 
			if msg == ':q':
				print('El usuario <%s,%s> solicitó desconectarse del chat' % (nombre, addr[1]))
				desp = '<Servidor>: Te has desconectado. Vuelve pronto!' # me despido
				actual.send(desp.encode('utf8'))
				actual.close() #cierro el socket del cliente y saco sus datos de los registros
				SOCKET_LIST.remove(actual)
				Nicknames.remove(nombre)
				Identif.remove(addr[1])
				continue

			# solicitud de comandos
			if msg == ':h': 
				print('El usuario <%s,%s> solicitó los comandos del chat' % (nombre, addr[1]))
				comnd = '<Servidor>: Los comandos disponibles son\n\n        :q = Desconectarse del chat\n        :h = Mostrar comandos\n        :i = Usuarios conectados\n        :add = Identificador interno\n        :p-name-msg = Envía mensaje privado msg a name'
				actual.send(comnd.encode('utf8'))
				continue

			# solicitud lista de usuarios
			if msg == ':i':
				print('El usuario <%s,%s> solicitó la lista de usuarios' % (nombre, addr[1]))
				lista_users='User              Indentificator'
				u=0
				while u < len(Nicknames): #creo lista de datos para enviar
					lista_users+='\n' + Nicknames[u] +'	           '+ str(Identif[u])
					u+=1
				users = '<Servidor>: \nLos usuarios disponibles son\n' + lista_users
				actual.send(users.encode('utf8'))
				continue

			# solicitud de identificador
			if msg == ':add':
				print('El usuario <%s,%s> solicitó su identificador' % (nombre, addr[1]))
				ident = 'Tu identificador es '+str(addr[1])
				actual.send(ident.encode('utf8'))
				continue

			# mensaje privado
			if msg[:3] == ':p-':
				c_nom = msg[3:] # nombre-msg
				end = c_nom.find('-') # posicion final del nombre
				destino = c_nom[:end] # despejo nombre
				print('El usuario <%s> ha enviado un mensaje privado a <%s>' % (nombre,destino))
				
				s_nom = '<Mensaje privado de: '+nombre+ '>: ' + c_nom[end+1:] # despejo y arreglo msg

				#Reviso si el usuario de destino está conectado
				if destino in Nicknames:
					s_destino = SOCKET_LIST[Nicknames.index(destino)+1]
					s_destino.send(s_nom.encode('utf8'))


				# de lo contrario notifico al emisor					
				else:
					no_esta = 'Usuario no conectado'
					actual.send(no_esta.encode('utf8'))



			#otros mensajes
			else:
				print('[' + nombre + ']: ' + msg)
				continue

serverSocket.close()