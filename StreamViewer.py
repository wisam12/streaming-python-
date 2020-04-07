import argparse

import cv2
import numpy as np
import zmq
import time
import threading

from constants import PORT
from utils import string_to_image

oldpoch = 0
current_frames = []


def display():
    global current_frames
    while True:
        while len(current_frames) >= 25:
            cv2.imshow("Stream", current_frames.pop())
            cv2.waitKey(1)


class StreamViewer:
    def __init__(self, port=PORT):
        """
        Binds the computer to a ip address and starts listening for incoming streams.

        :param port: Port which is used for streaming
        """
        context = zmq.Context()
        self.footage_socket = context.socket(zmq.SUB)
        self.footage_socket.bind('tcp://*:' + port)
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        self.keep_running = True

    def receive_stream(self):
        """
        Displays displayed stream in a window if no arguments are passed.
        Keeps updating the 'current_frame' attribute with the most recent frame, this can be accessed using 'self.current_frame'
        :param display: boolean, If False no stream output will be displayed.
        :return: None
        """
        global oldpoch, current_frames
        self.keep_running = True
        size = 0
        count_frame = 0
        while self.footage_socket and self.keep_running:
            try:
                frame = self.footage_socket.recv_string()
                count_frame = count_frame + 1
                size += self.utf8len(frame)
                if self.second_passed(oldpoch):
                    oldpoch = time.time()
                    print(str(size) + " " + str(count_frame))
                    size = 0
                    count_frame = 0
                current_frames.append(string_to_image(frame))

                # if display and len(self.current_frames) >= 30:
                #     for img in range(len(self.current_frames)):
                #         cv2.imshow("Stream", self.current_frames.pop())
                #         cv2.waitKey(1)

            except KeyboardInterrupt:
                cv2.destroyAllWindows()
                break
        print("Streaming Stopped!")

    def stop(self):
        """
        Sets 'keep_running' to False to stop the running loop if running.
        :return: None
        """
        self.keep_running = False

    @staticmethod
    def utf8len(s):
        return len(s.encode('utf-8'))

    @staticmethod
    def second_passed(oldepoch):
        return time.time() - oldepoch >= 1


def main():
    port = PORT

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port',
                        help='The port which you want the Streaming Viewer to use, default'
                             ' is ' + PORT, required=False)

    args = parser.parse_args()
    if args.port:
        port = args.port
    x = threading.Thread(name='displayer', target=display)
    x.start()
    stream_viewer = StreamViewer(port)
    stream_viewer.receive_stream()


if __name__ == '__main__':
    main()



import pyaudio, sys, socket

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
timer = 0

p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,channels = CHANNELS,rate = RATE,input = True,output = True,frames_per_buffer = chunk)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(),5000))
server_socket.listen(5)

print("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
print("Server Waiting for client on port 5000")

while 1:

    client_socket, address = server_socket.accept()
    client_socket.sendall(stream.read(chunk))