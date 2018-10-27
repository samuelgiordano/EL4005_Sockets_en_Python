#!/usr/bin/python3
import sys
import socket
import select

cSocket = socket.socket()
try:
    host = sys.argv[1]
except:
    host = 'localhost'
try:
    port = sys.argv[2]
except:
    port = 9998

# Connecting
cSocket.connect((host, port))

socket = [cSocket]

print('\nConnected to %s: %s \n' % (host, port))

# contacto inicial
saludo = cSocket.recv(1024).decode('utf8')
print (saludo)
Nick = input('\nIngresa tu nombre: ')
cSocket.send(Nick.encode('utf8'))

# verificamos que el nick no esté en uso
in_use = cSocket.recv(1024).decode('utf8')
while in_use == 'yes':
	Nick = input('Nombre en uso. Escoge otro nombre: ')
	cSocket.send(Nick.encode('utf8'))
	in_use = cSocket.recv(1024).decode('utf8')


while True:

	# usamos select para delegar el mantenenimiento del estado del socket al sistema operativo
	timeout_expired = False
	readable, writable , _ = select.select(socket,socket,[], timeout_expired)

	for actual in readable:
		
		if not readable:
			timeout_expired = True
		else:
			msj_rcb = actual.recv(1024).decode('utf8')
			print (msj_rcb)


	for actual in writable:
		if not writable:
			timeout_expired = True

		else:
			message = input('<'+Nick+'>: ')
			if message == '':
				continue
			cSocket.send(message.encode('utf8'))
			

cSocket.close()