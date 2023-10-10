import socket
import base64
import json

host = "localhost"
port = 8000

def bytesToString(bytes):
    asBytes = bytearray()
    asBytes.extend(bytes)
    byteToStr = ""
    for byte in asBytes:
        byteToStr += str(byte.to_bytes().hex())
        byteToStr += " "
    return byteToStr
    
def stringToByte(string):
    output = []
    for char in string:
        output.append(ord(char))
    return output
    
#this is O(bad) we'll clean it up later
def listCompare(arr1, arr2):
    if (len(arr1) != len(arr2)):
        return False
    for x in range(len(arr1)):
        if (arr1[x] != arr2[x]):
            return False
    return True
    
def responseFork(req):
    crlf = [0x0d, 0x0a]
    cmdHead = stringToByte("CMD ")
    dataHead = stringToByte("DATA")
    
    msgHi = stringToByte("hi") + crlf + crlf #handshake
    
    msgNope = stringToByte("nope")#'nope', use to aid in finding data in memory
    
    responseHead = stringToByte("RESP ")
    responseTail = [0x0d, 0x0a, 0x0d, 0x0a]
    
    message = ""
    requestType = ""
    
    #Parse the rest of the message from the header
    try:
        if listCompare(req[0:4], cmdHead) == True:
            try:
                message = req[4:len(req)]
                requestType = cmdHead
            except:
                print("Unfamiliar message syntax (body)")
                return [0]
        if listCompare(req[0:4], dataHead) == True:
            try:
                message = req[4:len(req)]
                requestType = dataHead
            except:
                print("Unfamiliar message syntax (body)")
                return [0]
    except:
        print("Unfamiliar message syntax (header)")
    
    if listCompare(message, msgHi):
        return responseHead + msgHi
        
    if listCompare(message[0:12], stringToByte("capabilities")):
        #It seems like it doesn't actually care what the response contains?
        return responseHead + stringToByte("capabilities") + crlf + stringToByte("Content-Length:12") + crlf + stringToByte("Content-Type: text/json") + crlf + crlf + stringToByte('{"asdf": 0}') + [0x0a]
        

    #"DATA" means the content of the message is (most likely) in a json string
    if requestType == dataHead:
        message = str(message)
        
        #Verify that the type is json
        if message.find("text/json") == -1:
            print("Unknown DATA message type")
            return msgNope
        
        indexAfterFor = message.find('"For":"')
        indexAfterFor += 7 #find gets the index of the beginning of the substring, not the end
        
        contentLengthStart = message.find("Content-Length: ") + len("Content-Length: ")
        contentLengthEnd = message.find("\\r\\n", contentLengthStart)
        
        contentLength = int(message[contentLengthStart:contentLengthEnd]) 
        
        jsonString = message[message.find("{"):message.find("{") + contentLength]
        payloadStart = jsonString.find('"Payload":"') + 11
        payloadEnd = jsonString.find('"', payloadStart)
        payload = jsonString[payloadStart:payloadEnd]
        
        #The devicetype command doesn't actually care what the response contains as long as it's 'devicetype' and formed correctly
        if message[indexAfterFor:indexAfterFor + 10] == "devicetype":
            deviceTypeResponse = '{"For":"devicetype","Payload":"STALL DEVICE","Type":"RESP"}'
            return dataHead + stringToByte(" ") + crlf + stringToByte("Content-Length:" + str(len(deviceTypeResponse))) + crlf + stringToByte("Content-Type: text/json") + crlf + crlf + stringToByte(deviceTypeResponse) + [0x0a]
            
        if message[indexAfterFor:indexAfterFor + 10] == "stalllogin":
            print("login stuff goes here! json time:")
            print(base64.b64decode(payload))
            
    print("No output for this request")
    return msgNope


print("welcome to sonic drive in @ " + host + ":" + str(port) + " (real)")
while(True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as jawn:
        jawn.bind((host, port))
        jawn.listen()
        conn, addr = jawn.accept()
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                except Exception as e:
                    print("Exception thrown from conn.recv: ")
                    print(e)
                
                if not data:
                    break
                
                #Print what we received
                print("RECEIVED:")
                print("str  :" + str(data))
                asBytes = bytearray()
                asBytes.extend(data)
                byteToStr = ""
                for byte in asBytes:
                    byteToStr += str(byte.to_bytes().hex())
                    byteToStr += " "
                print("bytes:" + byteToStr)
                
                #Respond!!!
                print("Responding with:")
                response = responseFork(data)
                stringresp = ""
                for char in response:
                    stringresp += chr(char)
                print("str  :" + stringresp)
                print("bytes:" + bytesToString(response))
                try:
                    conn.sendall(bytes(response))
                except Exception as e:
                    print("Exception thrown from conn.sendall: ")
                    print(e)
                    
