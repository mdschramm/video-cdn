# video-cdn

Python version: 3.11.5

Requires: opencv and numpy

```
pip install opencv-python && pip install numpy
```

To run (WIP)
1. Download a video into project folder (tested with .mp4)
2. Update `video =` in socket_server.py to your video name
3. Open 2 Terminals
4. Run `python socket_server.py` in the first and `python socket_client.py` in the second
5. Video should stream

