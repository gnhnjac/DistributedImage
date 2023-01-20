import socket, sys
from PIL import Image
import io, pickle
from tcp_by_size import *

if len(sys.argv) != 2:
    print("You didn't supply enough parameters")

img_path = sys.argv[1]

BLK_SIZE = 10000

sock = socket.socket()

sock.connect(('127.0.0.1', 5555))
print("Connection succeeded")

SIZE = sock.recv(50)
if SIZE == b'':
    print("Server closed")
    sock.close()
    sys.exit(0)
SIZE = int(SIZE)
print(f"Got size of {SIZE} from server")
sock.sendall(b"A") # acknowledge

print("Sending image...")

img = Image.open(img_path)
im_resize = img.resize((SIZE, SIZE))

buf = io.BytesIO()
im_resize.save(buf, format='PNG')
raw_image = pickle.dumps(buf)
n = BLK_SIZE
blocks = [raw_image[i:i+n] for i in range(0, len(raw_image), n)]
for n, blk in zip(range(len(blocks)), blocks):

    send_with_size(sock,b'BLK|' + blk)
    ack = sock.recv(1) # ack
    if ack == b'':
        print("Server closed")
        sock.close()
        sys.exit(0)
    print(f"Sending block no {n+1}/{len(blocks)}")
print("Finished sending image")
print(len(raw_image))
send_with_size(sock, b'STP|') # Stop server from receiving image
while True:
    ping = sock.recv(4)
    if ping == b'':
            print("Server closed")
            sock.close()
            sys.exit(0)
    sock.sendall(b"A")