
import asyncore #Import modules
import socket
import sys
import socket
from datetime import datetime, date, time
from nredarwin.webservice import DarwinLdbSession

#Connect to the database

                #Create instance that allows me to enter commands
#class Handle_Data(asyncore.dispatcher_with_send):

    #def handle_read(self):
        #data = self.recv(1024) #Recieve data from the client.

        #data2 = data.decode('ascii') #Decode the data recieved from ascii(since it was sent from c# code it will be in ascii).

        #if data2 == "test":
            #var = 
        #if data2: #If there is any data run a command.
                #if data2 == "REQUEST NAME":
                    #Do things.
                    #self.send(stringbuilder.encode()) #Send the data with defualt encoding.

                #elif "OTHER REQUEST NAME" in data2:
                    #Do something else.
                    #self.send(stringbuilder.encode()) #Send the data with defualt encoding.
        #else:
            #pass

#class Server(asyncore.dispatcher):

    #def __init__(self, host, port): #Create method that accepts self value and a host and port input.
        #asyncore.dispatcher.__init__(self) #Create instance of dispatcher class.
        #self.create_socket(socket.AF_INET, socket.SOCK_STREAM) #Create a blank socket.
        #self.set_reuse_addr() #Stop the socket from timing out.
        #self.bind((host, port)) #Create variable get set for host and port types.
        #self.listen(5) #Listen for a maximum of up to 5 queued connections

    #def handle_accept(self): #Create method for accepting connections.
        #pair = self.accept()
        #if pair is not None: #If the client isnt empty set the client variable.
            #sock, addr = pair
            #print (str.format("Incoming connection from '{0}'",repr(addr))) #Print client ip address.
            #handler = Handle_Data(sock) #Pass to the data class.
            #print("listening..")

#server = Server('0.0.0.0', 8000) #Create new instance of server, 0.0.0.0 means it will host on any port so both 127.0.0.1(local pc only) and 192.168.1.1 will be hosted so it can be accessed from other pcs.
#print("listening..") #State that the server is listening again. 

def initSession():
    newSession = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01", api_key="***REMOVED***")
    return newSession

session = initSession()

##Class creation##

#class GetDepartureBoard:
    #def __init__(board, boardName):
        #board.boardName = boardName
        
inputBoard = str(input("Please enter the name of the departure board you would like and press enter: "))

boardRequest = session.get_station_board(inputBoard)

arrStations = []

print("Trains go from here to: \n")

for a in boardRequest.train_services:
    arrStations.append(a.destination_text)

print(",".join(arrStations))
    
#asyncore.loop() #Call loop method of asyncore to begin listening for clients again.
