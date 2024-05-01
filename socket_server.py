import threading
import socketserver
import cv2
import socket
import time
import struct
import numpy as np
import pickle


class ThreadedEchoRequestHandler(
        socketserver.BaseRequestHandler,
):

    def handle(self):
        try:
            cur_thread = threading.current_thread()
            print('Server Thread: %s' % cur_thread.name)
            # video = '3698047-uhd_3840_2160_15fps.mp4'
            video = 'soccer_stadium.mp4'
            cap = cv2.VideoCapture(video)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                ret, jpeg = cv2.imencode('.jpg', frame, [480, 480])
                frame_data = jpeg.tobytes()
                self.request.sendall(struct.pack("Q", len(frame_data)))
                self.request.sendall(frame_data)
                if cv2.waitKey(1) == 13:
                    break
            cap.release()
        except Exception as e:
            print("Exception occurred:", e)
            # Close the connection with the client
            self.request.close()
            
       

class ThreadingServer(socketserver.ThreadingTCPServer):

    def __init__(self, server_address, RequestHandlerClass):
        socketserver.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)


if __name__ == '__main__':

    address = ('localhost', 10001)
    server = ThreadingServer(address,
                                ThreadedEchoRequestHandler)
    ip, port = server.server_address  # what port was assigned?

    try:
        print('Server loop running:')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.socket.close()

