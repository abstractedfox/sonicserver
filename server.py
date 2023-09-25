import socket

host = "localhost"
port = 6969

def bytesToString(bytes):
    asBytes = bytearray()
    asBytes.extend(bytes)
    byteToStr = ""
    for byte in asBytes:
        byteToStr += str(byte.to_bytes().hex())
        byteToStr += " "
    return byteToStr
    
#this is O(bad) we'll clean it up later
def listCompare(arr1, arr2):
    if (len(arr1) != len(arr2)):
        return False
    for x in range(len(arr1)):
        if (arr1[x] != arr2[x]):
            return False
    return True
    
def responseFork(req):
    reqHead = [0x43, 0x4d, 0x44, 0x20] #"CMD "
    msgHi = [0x68, 0x69] #"hi"

    message = ""
    responseHead = [ord('R'), ord('E'), ord('S'), ord('P'), ord(' ')]
    responseTail = [0x0d, 0x0a, 0x0d, 0x0a]
    
    try:
        if (listCompare(req[0:4], reqHead) == False):
            print("Unfamiliar message header:" + bytesToString(req[0:4]))
            return [0]
    except:
        print("Unfamiliar message syntax (header)")
    
    try:
        message = req[4:req.index(responseTail[0])]
    except:
        print("Unfamiliar message syntax (body)")
        return [0]
    
    if (listCompare(message, msgHi)):
        return responseHead + msgHi + responseTail
        
    print("No output for this request")
    return [0]

print("welcome to sonic drive in @ " + host + ":" + str(port) + " (real)")
while(True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as jawn:
        jawn.bind((host, port))
        jawn.listen()
        conn, addr = jawn.accept()
        with conn:
            while True:
                data = conn.recv(1024)
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
                conn.sendall(bytes(response))
