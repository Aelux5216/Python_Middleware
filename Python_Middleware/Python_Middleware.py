
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

class Service():
    pass

def GetAll(dep_code, arr_code):
        
    session = None
    error = ""
    
    try:
        session = initSession()

    except:
        error = "NoConn"

    if session is not None:

        depBoardRequest = session.get_station_board(dep_code,destination_crs=arr_code)
        
        services = depBoardRequest.train_services
        
        if len(services) > 0 :
            allServices = []
            for y in services:
                depServiceId = y.service_id
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

                service1 = Service()

                service1.service_id = y.service_id
                service1.operator = y.operator_name
                service1.dep_name = y.origin_text
                service1.dep_code = depServiceDet.crs
                service1.dep_time = y.std
                service1.dep_platform = y.platform
                service1.arr_name = arrDest.location_name
                service1.arr_code = arr_code
                service1.arr_time = arrDest.st
                service1.arr_platform = arr_platform
                service1.status = y.etd
                service1.disrupt_reason = depServiceDet.disruption_reason 
                service1.calls_at = []

                for b in arrDestPoints:
                    p1 = Calling_Points(b.location_name,b.crs,b.st,b.et)
                    p1s = json.dumps(vars(p1))
            
                service1.calls_at.append(str(p1s))

                service1.stops = len(service1.calls_at)

                jsonObject = json.dumps(vars(service1))

                allServices.append(str(jsonObject))
            return allServices
        else:
            error = "NoServices"
            return error
    else:
        return error

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

        if "GetAll" in decodedData:
            
            session = initSession()

            splitData = decodedData.split("{")
            
            depStation = splitData[1]

            arrStation = splitData[2]
            
            result = GetAll(depStation,arrStation)

            if "NoServices" not in result and "NoConn" not in result:
                
                jsonObject = json.dumps(result)
                self.send(jsonObject.encode())

            else:

                self.send(result.encode())
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

server = Server('0.0.0.0', 8001) #Create new instance of server, 0.0.0.0 means it will host on any port so both 127.0.0.1(local pc only) and 192.168.1.1 will be hosted so it can be accessed from other pcs.
print("listening..") #State that the server is listening again. 

asyncore.loop() #Call loop method of asyncore to begin listening for clients again.
