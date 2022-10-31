import socket

pivot_server_ip = "localhost"
port = 8880

# setup the socket
#addr = socket.getaddrinfo(pivot_server_ip, 8880)[0][-1]
s = socket.socket()
s.connect((pivot_server_ip, port))

# post request to report signal strengths
payload = '{"SourceName": "SourceName-ganymede", "Numbers": [24, 41, 115]}'
content = 'POST /p/ HTTP/1.1\r\n' + \
    'Host: ' + pivot_server_ip + '\r\n' + \
    'Accept: application/json\r\n' + \
    'Content-Type: application/json\r\n' + \
    'Content-Length: ' + str(len(payload)) + '\r\n\r\n' + \
    payload

s.send(content.encode('utf-8'))

data = s.recv(1000)
print(data)
s.close()
