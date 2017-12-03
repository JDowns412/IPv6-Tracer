import socket
import time

host = "tvn-2.com"
get_object = "/videos/noticias/Vice-Ecuador-detenido-acusado-Odebrecht_11353605.jpg"
# host = "aljazeera.net"
# get_object = "/Content/images/headerlogo.png"

# # IPv4
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, 80))

# # IPv6
# sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
# # print(socket.has_ipv6) # True
# addrs = socket.getaddrinfo(host, port, socket.AF_INET6, 0, socket.SOL_TCP)
# # print(addrs)
# sockaddr = addrs[0][-1]
# # print(sockaddr)
# sock.connect(sockaddr)
# # sock.connect((host, port, 0, 0))

# sock.close()

# Good
# sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
# # start the socket connection
# # print(data["valid"][domain]["best6"])
# # sock.connect((data["valid"][domain]["best6"], 80, 0, 0))

# addrs = socket.getaddrinfo(host, 80, socket.AF_INET6, 0, socket.SOL_TCP)
# # print(addrs)
# sockaddr = addrs[0][-1]
# # print(sockaddr)
# sock.connect(sockaddr)
    
# construct the message we'll be sending
message =  'GET ' + get_object + ' HTTP/1.0\r\n'
message += 'Host: ' + host + '\r\n'
message += 'Connection: keep-alive\r\n'
message += 'User-Agent: Mozilla/5.0\r\n'
#this double CR-LF is the standard HTTP way of indicating the end of any HTTP header fields
message += '\r\n'

#record the time the request takes
start = time.time()
sock.send(message.encode('utf-8'))
# receive the response and parse it into it's different header fields

size = 0
buf = sock.recv(4096)
while buf:
    size += len(buf)
    print(len(buf))
    buf = sock.recv(1024)

# record the time it takes for the object to be fetched (in seconds)
timer = time.time() - start

# close the socket once we're done with it
sock.close()

print(timer, size)