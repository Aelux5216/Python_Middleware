
import asyncore #Import modules
import socket
import sys
import copy
import json
from nredarwin.webservice import DarwinLdbSession

#Connect to API
def initSession():
    newSession = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01", api_key="***REMOVED***")
    return newSession

##Class creation##

class Service:
    def __init__(self, service_no, dep_code, arr_code):
        
        session = initSession()

        depBoardRequest = session.get_station_board(dep_code,destination_crs=arr_code)
        service = depBoardRequest.train_services[service_no]
        depServiceId = service.service_id
        depServiceDet = session.get_service_details(depServiceId)
        arrDestPoints = depServiceDet.subsequent_calling_points
        
        for e in arrDestPoints:
            if arr_code in e.crs:
                arrDest = e
            pass

        for a in depBoardRequest.train_services:
            if depServiceId in a.service_id:
                arr_platform = a.platform
            pass

        self.service_id = service.service_id
        self.operator = service.operator_name
        self.dep_name = service.origin_text
        self.dep_code = depServiceDet.crs
        self.dep_time = service.std
        self.dep_platform = service.platform
        self.arr_name = arrDest.location_name
        self.arr_code = arr_code
        self.arr_time = arrDest.st
        self.arr_platform = arr_platform
        self.status = service.etd
        self.disrupt_reason = depServiceDet.disruption_reason 
        #self.calls_at = []

        #for b in arrDestPoints:
            #p1 = Calling_Points(b.location_name,b.crs,b.st,b.et)
            #self.calls_at.append(copy.copy(p1))

        #self.stops = len(self.calls_at)

class Calling_Points:
    def __init__(self, name, code, time, status):
        
        self.name = name
        self.code = code
        self.time = time
        self.status = status

class Tickets:
    def __init__(self, reference, ticket_type, cost):

        self.reference = reference
        self.ticket_type = ticket_type
        self.cost = cost


#Create instance that allows me to enter commands
class Handle_Data(asyncore.dispatcher_with_send):

    def handle_read(self):
        rawData = self.recv(1024) #Recieve data from the client.

        decodedData = rawData.decode('ascii') #Decode the data recieved from ascii(since it was sent from c# code it will be in ascii).

        if "test" in decodedData:

            session = initSession()

            splitData = decodedData.split("{")

            serviceNo = int(splitData[1])
            
            depStation = splitData[2]

            arrStation = splitData[3]

            #Will use selected value service for service no, for now defaulting to first service index of 0
            result = Service(serviceNo,depStation,arrStation)

            jsonObject = json.dumps(vars(result))

            self.send(jsonObject.encode())

        if data2: #If there is any data run a command.
                if data2 == "REQUEST NAME":
                    #Do things.
                    self.send(stringbuilder.encode()) #Send the data with defualt encoding.

                elif "OTHER REQUEST NAME" in data2:
                    #Do something else.
                    self.send(stringbuilder.encode()) #Send the data with defualt encoding.
        else:
            pass

class Server(asyncore.dispatcher):

    def __init__(self, host, port): #Create method that accepts self value and a host and port input.
        asyncore.dispatcher.__init__(self) #Create instance of dispatcher class.
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM) #Create a blank socket.
        self.set_reuse_addr() #Stop the socket from timing out.
        self.bind((host, port)) #Create variable get set for host and port types.
        self.listen(5) #Listen for a maximum of up to 5 queued connections

    def handle_accept(self): #Create method for accepting connections.
        pair = self.accept()
        if pair is not None: #If the client isnt empty set the client variable.
            sock, addr = pair
            print (str.format("Client '{0}' has connected successfully",repr(addr))) #Print client ip address.
            handler = Handle_Data(sock) #Pass to the data class
            print("listening..")

server = Server('0.0.0.0', 8000) #Create new instance of server, 0.0.0.0 means it will host on any port so both 127.0.0.1(local pc only) and 192.168.1.1 will be hosted so it can be accessed from other pcs.
print("listening..") #State that the server is listening again. 

asyncore.loop() #Call loop method of asyncore to begin listening for clients again.
