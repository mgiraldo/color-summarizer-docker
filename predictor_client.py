import socket
import sys
import os
from io import BytesIO
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--host", default="127.0.0.1", type=str, help="Prediction server host")
parser.add_argument("--port", default=4000, type=str, help="Prediction server socket port")

args = parser.parse_args()

host = args.host
port = args.port

def main():
  soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  packet_size = 4096

  try:
    soc.connect((host, port))
  except:
    print("Connection error")
    sys.exit()

  print("Enter 'quit' to exit")
  message = input(" -> ")

  while message != 'quit':
    soc.sendall(message.encode("utf8"))
    data = b''
    while True:
      receiving_buffer = soc.recv(packet_size)
      if not receiving_buffer: break
      if receiving_buffer == b'-': break
      else:
        data += receiving_buffer
        if len(receiving_buffer) < packet_size: break
    if data != b'':
      final_array=np.load(BytesIO(data))['frame']
      print(final_array)
    
    message = input(" -> ")

  soc.send(b'--quit--')

if __name__ == "__main__":
  main()