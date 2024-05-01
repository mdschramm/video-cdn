import threading
import socketserver
import socket
import time
import cv2
import struct
import pickle
import numpy as np

address = ('localhost', 10001)


# client
def connect2server():
    s = socket.create_connection(address)
    # collects bytes from the server in chunks
    window = b""
    # size of data containing the frame size
    frame_size_header_len = struct.calcsize("Q")
    while True:
        # Obtain next frame's size
        while len(window) < frame_size_header_len:
            packet = s.recv(4 * 1024) 
            if not packet:
                break
            window += packet
        if not window:
            break

        # unpack the frame size
        frame_size_data = window[:frame_size_header_len]
        frame_size = struct.unpack("Q", frame_size_data)[0]

        # discard frame size data from window
        window = window[frame_size_header_len:]

        # obtain frame size worth of data
        while len(window) < frame_size:
            window += s.recv(4 * 1024)  # 4K buffer size

        # decode and render frame
        frame_data = window[:frame_size]
        image = cv2.imdecode(
            np.frombuffer(frame_data, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )
        cv2.imshow('Client', image)

        # Quit video with q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        # discard last frame's data and continue
        window = window[frame_size:]
    cv2.destroyAllWindows()


    s.close()



if __name__ == '__main__':
    connect2server()
    # threadlist = []
    # threadcount = 1

    # for i in range(threadcount):
    #     print('making client', i)
    #     client = threading.Thread(target=connect2server)
    #     threadlist.append(client)
    #     client.start()

    # for i in range(threadcount):
    #     threadlist[i].join()
