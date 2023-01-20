

# This Python file sends an image to a server using the TCP protocol.
#
# It takes one parameter, the path of the image to be sent.
#
# It establishes a connection with the server and sends the image in blocks of size 10000 bytes. After each block is sent, it receives an acknowledgement from the server.
#
# When the image is completely sent, it sends a stop signal to the server to indicate the end of the transmission. 
#
# Finally, it continuously pings the server until it is closed.