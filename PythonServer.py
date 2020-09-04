
import threading
import socket
import argparse
import os
import datetime
import xml.etree.ElementTree as ET

#Add activity type "JOIN" to DataBase
def addUserToDB(username):
    tree = ET.parse("database.xml")
    xmlRoot = tree.getroot()
    activity = ET.Element('activity')
    activity.set('Type','Join')
    #Generating date
    date = ET.SubElement(activity, 'Date')
    current_date = str(datetime.datetime.now().month) +"/"+ str(datetime.datetime.now().day) + "/" + str(datetime.datetime.now().year)
    date.text = current_date
    #Generating time
    time = ET.SubElement(activity,'Time')
    current_time = str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)+":"+str(datetime.datetime.now().second)
    time.text= current_time
    #Generating Username
    tempusername = ET.SubElement(activity,'UserName')
    tempusername.text=username
    #Generating Message
    msg = ET.SubElement(activity,'Message')
    msg.text = 'Joined the Group Chat.'
    xmlRoot.append(activity)
    tree.write("database.xml")
    
#Add activity type "QUIT" to DataBase   
def addQuitToDB(username):
    tree = ET.parse("database.xml")
    xmlRoot = tree.getroot()
    activity = ET.Element('activity')
    activity.set('Type','Quit')
    #Generating date
    date = ET.SubElement(activity, 'Date')
    current_date = str(datetime.datetime.now().month) +"/"+ str(datetime.datetime.now().day) + "/" + str(datetime.datetime.now().year)
    date.text = current_date
    #Generating time
    time = ET.SubElement(activity,'Time')
    current_time = str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)+":"+str(datetime.datetime.now().second)
    time.text= current_time
    #Generating Username
    tempusername = ET.SubElement(activity,'UserName')
    tempusername.text=username
    #Generating Mmessage
    msg = ET.SubElement(activity,'Message')
    msg.text = 'left the Group Chat.'
    xmlRoot.append(activity)
    tree.write("database.xml")

#Add activity type "Message" to DataBase
def addMsgToDB(username,message):
    tree = ET.parse("database.xml")
    xmlRoot = tree.getroot()
    activity = ET.Element('activity')
    activity.set('Type','Message')
    #Generating date
    date = ET.SubElement(activity, 'Date')
    current_date = str(datetime.datetime.now().month) +"/"+ str(datetime.datetime.now().day) + "/" + str(datetime.datetime.now().year)
    date.text = current_date
    #Generating time
    time = ET.SubElement(activity,'Time')
    current_time = str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)+":"+str(datetime.datetime.now().second)
    time.text= current_time
    #Generating Username
    tempusername = ET.SubElement(activity,'UserName')
    tempusername.text=username
    #Generating MSG
    msg = ET.SubElement(activity,'Message')
    msg.text = message
    xmlRoot.append(activity)
    tree.write("database.xml")
#Function for getting current Time
def getCurrentTime():
    return str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)+":"+str(datetime.datetime.now().second)
#Function for getting current Date
def getCurrentDate():
    return str(datetime.datetime.now().month) +"/"+ str(datetime.datetime.now().day) + "/" + str(datetime.datetime.now().year)
#Function for Extracting message
def messageExtractor(string):
    newstring=(str(string))
    extracted=newstring.split('-')
    return extracted
#Function for make a 4byte message in format of (length of message that server wants to send to client + "-") to make it 4 bit
def convertDigit(digit):
    if len(digit) == 1:
        return digit + '-' + '-' + '-'
    elif len(digit) == 2:
        return digit + '-' + '-'
    elif len(digit) == 3:
        return digit + '-'

class Server(threading.Thread):
    """
    Supports management of server connections.
    Attributes:
        connections (list): A list of ServerSocket objects representing the active connections.
        host (str): The IP address of the listening socket.
        port (int): The port number of the listening socket.
    """
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
    
    def run(self):
        """
        Creates the listening socket. The listening socket will use the SO_REUSEADDR option to
        allow binding to a previously-used socket address. This is a small-scale application which
        only supports one waiting connection at a time. 
        For each new connection, a ServerSocket thread is started to facilitate communications with
        that particular client. All ServerSocket objects are stored in the connections attribute.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print('Listening at', sock.getsockname())

        while True:

            # Accept new connection
            sc, sockname = sock.accept()
            print('Accepted a new connection from {} to {}'.format(sc.getpeername(), sc.getsockname()))

            # Create new thread
            server_socket = ServerSocket(sc, sockname, self)
            
            # Start new thread
            server_socket.start()

            # Add thread to active connections
            self.connections.append(server_socket)
            print('Ready to receive messages from', sc.getpeername())

    def broadcast(self, message, source):
        """
        Sends a message to all connected clients, except the source of the message.
        Args:
            message (str): The message to broadcast.
            source (tuple): The socket address of the source client.
        """
        for connection in self.connections:

            connection.send(message)
    
    def remove_connection(self, connection):
        """
        Removes a ServerSocket thread from the connections attribute.
        Args:
            connection (ServerSocket): The ServerSocket thread to remove.
        """
        self.connections.remove(connection)


class ServerSocket(threading.Thread):
    """
    Supports communications with a connected client.
    Attributes:
        sc (socket.socket): The connected socket.
        sockname (tuple): The client socket address.
        server (Server): The parent thread.
    """
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
    
    def run(self):
        """
        Receives data from the connected client and broadcasts the message to all other clients.
        If the client has left the connection, closes the connected socket and removes itself
        from the list of ServerSocket threads in the parent Server thread.
        """
        while True:
            message = self.sc.recv(1024).decode('ascii')
            if message:
                print('{} says {!r}'.format(self.sockname, message))
                print(messageExtractor(message)[0])
                #sending the "JOIN" message
                if messageExtractor(message)[0]=='JOIN':
                
                    currentTime = getCurrentTime()
                    currentDate = getCurrentDate()
                
                    currentUsername = messageExtractor(message)[1]
                    addUserToDB(currentUsername)
                    joinNotification ="[" + currentDate + " - " + currentTime +"] "+ currentUsername +' is Joined.'
                    notificationLen  = convertDigit(str(len(joinNotification)))
                    #sending length of message to all the clients
                    self.server.broadcast(notificationLen, self.sockname)
                    #sending the "JOIN" message to all the clients
                    self.server.broadcast(joinNotification, self.sockname)
                #sending the messages
                if messageExtractor(message)[0]=='SEND':
                    currentTime = getCurrentTime()
                    currentDate = getCurrentDate()
                    #format : SEND-username-message
                    currentMessage = messageExtractor(message)[2]
                    currentUsername = messageExtractor(message)[1]
                    messageNotification ="[" + currentDate + " - " + currentTime +"] "+ currentUsername +' : '+ currentMessage
                    notificationLen  = convertDigit(str(len(messageNotification)))
                    addMsgToDB(currentUsername,currentMessage)
                    #sending length of message to all the clients
                    self.server.broadcast(notificationLen, self.sockname)
                    #sending the message to all the clients
                    self.server.broadcast(messageNotification, self.sockname)
                    #sending the "Quit" message
                if messageExtractor(message)[0]=='QUIT':
                    currentTime = getCurrentTime()
                    currentDate = getCurrentDate()
                    #format : QUIT-username
                    currentUsername = messageExtractor(message)[1]
                    addQuitToDB(currentUsername)
                    leaveNotification ="[" + currentDate + " - " + currentTime +"] "+ currentUsername +' left the group.'
                    notificationLen  = convertDigit(str(len(leaveNotification)))
                    #sending length of message to all the clients
                    self.server.broadcast(notificationLen, self.sockname)
                    #sending the "Quit" message to all the clients
                    self.server.broadcast(leaveNotification, self.sockname)
                    
                    print('{} has closed the connection and left the group'.format(self.sockname))
                    self.sc.close()
                    server.remove_connection(self)
                    return
                
                    
            
            else:
                # Client has closed the socket, exit the thread
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                server.remove_connection(self)
                return
    
    def send(self, message):
        """
        Sends a message to the connected server.
        Args:
            message (str): The message to be sent.
        """
        self.sc.sendall(message.encode('ascii'))


def exit(server):
    """
    Allows the server administrator to shut down the server.
    Typing 'q' in the command line will close all active connections and exit the application.
    """
    while True:
        ipt = input('')
        if ipt == 'q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)

# Create and start server thread
server = Server('127.0.0.1', 8089)
server.start()

exit = threading.Thread(target = exit, args = (server,))
exit.start()
