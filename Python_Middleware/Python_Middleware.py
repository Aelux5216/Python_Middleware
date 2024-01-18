
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

def GetAll(dep_code, arr_code): #Method that returns all services based on input values 
        
    session = None #Initalise variables
    error = ""
    
    try:
        session = initSession() #Try and make a connection with darwin and return NoConn error string if it fails.

    except:
        error = "NoConn"

    if session is not None: 

        depBoardRequest = session.get_station_board(dep_code,destination_crs=arr_code,rows=150) #If the session is not null get 
                                                                                                #the stationboard related to 
        services = depBoardRequest.train_services                                               #the choosen departurestation and arrival station
                                                                                                
        if len(services) > 0 :                         #If services are available  
            allServices = []                           #Get the individual objects and values from within the one object recieved
            for y in services:
                depServiceId = y.service_id
                depServiceDet = session.get_service_details(depServiceId)
                arrDestPoints = depServiceDet.subsequent_calling_points #Get related calling points
        
                for e in arrDestPoints:
                    if arr_code in e.crs:
                        arrDest = e
                    pass

                service1 = Service() #Create a blank class and set the values to related ones extracted above.

                service1.service_id = y.service_id 
                service1.operator = y.operator_name
                service1.dep_name = depBoardRequest.location_name
                service1.dep_code = depServiceDet.crs
                service1.dep_time = y.std
                service1.dep_platform = y.platform
                service1.arr_name = arrDest.location_name
                service1.arr_code = arr_code
                service1.arr_time = arrDest.st
                service1.status = y.etd
                service1.disrupt_reason = depServiceDet.disruption_reason 
                service1.calls_at = []

                for b in arrDestPoints:  #For every calling point set values and serialize to json string
                    p1 = Calling_Points(b.location_name,b.crs,b.st,b.et)  
                    p1s = json.dumps(vars(p1))
                    service1.calls_at.append(str(p1s)) #Add object to string within service
                    
                service1.stops = len(service1.calls_at) #Calculate amount of calling points

                jsonObject = json.dumps(vars(service1)) #Serialize whole service into jason string 

                allServices.append(str(jsonObject)) #Add service to list of services
            return allServices
        else:
            error = "NoServices" #If no train times then set error string
            return error
    else:
        return error

def GetOne(serviceNo,arrCode): #Get one service only
    session = None
    service = None
    error = ""
    
    try:
        session = initSession()

    except:
        error = "NoConn"

    if session is not None:
        try:
            service = session.get_service_details(serviceNo) #Get specifc details for one service from x to y
        except:
            pass
        if service is not None :
            
            arrDestPoints = service.subsequent_calling_points #Instance creation and value setting
            
            for e in arrDestPoints:
                    if arrCode in e.crs:
                        arrDest = e
                    pass

            service1 = Service()

            service1.operator = service.operator_name
            service1.dep_name = service.location_name
            service1.dep_code = service.crs
            service1.dep_time = service.std
            service1.dep_platform = service.platform
            service1.arr_name = arrDest.location_name
            service1.arr_code = arrCode
            service1.arr_time = arrDest.st
            service1.status = service.etd
            service1.disrupt_reason = service.disruption_reason 
            service1.calls_at = []

            for b in arrDestPoints:
                p1 = Calling_Points(b.location_name,b.crs,b.st,b.et)
                p1s = json.dumps(vars(p1))
                service1.calls_at.append(str(p1s))

            service1.stops = len(service1.calls_at)

            jsonObject = json.dumps(vars(service1))

            allServices = []

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

#Create instance that allows it to recieve commands
class Handle_Data(asyncore.dispatcher_with_send):

    def handle_read(self):
        rawData = self.recv(1024) #Recieve data from the client.

        decodedData = rawData.decode('ascii') #Decode the data recieved from ascii(since it was sent from c# code it will be in ascii).
        
        print(str.format("Command recieved: '{0}'",decodedData))

        if "GetAll" in decodedData: #If string is inside of string
            
            splitData = decodedData.split("{") #Split based on custom protocol parameters
            
            depStation = (splitData[1])[-4:].strip(')') 

            arrStation = (splitData[2])[-4:].strip(')')
            
            result = GetAll(depStation,arrStation) #Pass variables

            if result != "NoServices" and result != "NoConn": #If no errors serialize array of services into json string
                jsonObject = json.dumps(result)               #and send over the network
                self.send(jsonObject.encode()) 

                print("All services sent back to client")

            else:
                self.send(result.encode()) #else send as it is as it will just be a string

                print("No services or Darwin down")

        elif "GetOne" in decodedData:


            splitData = decodedData.split("{")

            serviceNo = splitData[1]

            arrCode = splitData[2]

            #Use selected service by user and destination code to get the service related to their service_id 
            result = GetOne(serviceNo,arrCode)

            if result != "NoServices" and result != "NoConn":
                jsonObject = json.dumps(result)
                self.send(jsonObject.encode())

                print("Single service sent back to client")

            else:
                print("No services or Darwin Down")

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

server = Server('0.0.0.0', 8001) #Create new instance of server, 0.0.0.0 means it will host on any port.
print("listening..") #State that the server is listening again. 

asyncore.loop() #Call loop method of asyncore to begin listening for clients again.
