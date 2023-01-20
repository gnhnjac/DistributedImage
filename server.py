import socket
import threading
import pygame
from pygame.locals import *
import time
import pickle
from PIL import Image
from tcp_by_size import *

BLK_SIZE = 10000
SIZE = 600
RECT_SIZE = SIZE//4
RECT_X = SIZE//2 - RECT_SIZE//2
RECT_Y = SIZE//2 - RECT_SIZE//2
CONNS = 0
LOCK = threading.Lock()

sock = socket.socket()

sock.bind(('127.0.0.1', 5555))

sock.listen()

image_buffer = []
full_image = pygame.Surface((SIZE, SIZE))
full_image.fill(0)

def construct_full_image():

    global full_image

    coords = {0:(0,0), 1:(SIZE//2, 0), 2:(0, SIZE//2), 3:(SIZE//2,SIZE//2)}
    full_image.fill(0)
    for i, image in zip(range(4), image_buffer):
        full_image.blit(image[0], coords[i])
    print("Reconstructed image successfully")


def remove_client_image(cli):

    LOCK.acquire()

    for i in range(len(image_buffer)):
    
        if image_buffer[i][1] == cli:
            del image_buffer[i]
            construct_full_image()
            LOCK.release()
            print("Image removed successfully")
            return
    print("Could not find image")
    LOCK.release()

def handle_client(cli, addr):
    global CONNS
    global image_buffer
    LOCK.acquire()
    CONNS += 1
    LOCK.release()

    print(f"New connection from {addr[0]}:{addr[1]}")

    try:
        cli.sendall(f'{SIZE//2}'.encode())
        ack = cli.recv(1)
        if ack == b'':
            print(f"{addr[0]}:{addr[1]} disconnected")
            LOCK.acquire()
            CONNS -= 1
            LOCK.release()
            cli.close()
            return
        raw_image = b''
        blk = recv_by_size(cli)
        if blk == b'':
            print(f"{addr[0]}:{addr[1]} disconnected")
            LOCK.acquire()
            CONNS -= 1
            LOCK.release()
            cli.close()
            return
        i = 0
        while blk[:4] != b"STP|":

            cli.sendall(b"A") # acknowledge


            blk = blk[4:]

            raw_image += blk

            blk = recv_by_size(cli)
            if blk == b'':
                print(f"{addr[0]}:{addr[1]} disconnected")
                LOCK.acquire()
                CONNS -= 1
                LOCK.release()
                cli.close()
                return
            i+=1
            print(f"Receiving block no. {i} from {addr[0]}:{addr[1]}")
        print(len(raw_image))
        bytesio = pickle.loads(raw_image)
        bytesio.seek(0)
        print(f"Got Image from client {addr[0]}:{addr[1]}")
        LOCK.acquire()
        image_buffer.append((pygame.image.load(bytesio),cli))
        construct_full_image()
        LOCK.release()

        while True:
            cli.send(b'PING')
            ack = cli.recv(1)
            if ack == b'':
                print(f"{addr[0]}:{addr[1]} disconnected")
                LOCK.acquire()
                CONNS -= 1
                LOCK.release()
                cli.close()
                remove_client_image(cli)
                return
            time.sleep(1)
    except Exception as e:
        print(f"{addr[0]}:{addr[1]} disconnected, Exception: {e}")
        LOCK.acquire()
        CONNS -= 1
        LOCK.release()
        cli.close()
        remove_client_image(cli)
        return


def handle_conns():
    while True:

        if CONNS < 4:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=[conn,addr])
            t.start()

t = threading.Thread(target=handle_conns)
t.start()

pygame.init()
screen = pygame.display.set_mode((SIZE, SIZE))
clock = pygame.time.Clock()
running = 1

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0
    
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        RECT_X-=2
    elif keys[K_RIGHT]:
        RECT_X+=2
    elif keys[K_DOWN]:
        RECT_Y += 2
    elif keys[K_UP]:
        RECT_Y -= 2

    screen.fill(0)
    screen.blit(full_image, (RECT_X,RECT_Y), (RECT_X,RECT_Y,RECT_SIZE,RECT_SIZE))
    pygame.draw.rect(screen, 255, (RECT_X,RECT_Y, RECT_SIZE,RECT_SIZE), 3)
    pygame.draw.rect(screen,(255,255,255), (0,0,SIZE//2,SIZE//2),1)
    pygame.draw.rect(screen,(255,255,255), (0,SIZE//2,SIZE//2,SIZE//2),1)
    pygame.draw.rect(screen,(255,255,255), (SIZE//2,0,SIZE//2,SIZE//2),1)
    pygame.draw.rect(screen,(255,255,255), (SIZE//2,SIZE//2,SIZE//2,SIZE//2),1)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()