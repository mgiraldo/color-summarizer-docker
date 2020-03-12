import socket
import sys
from io import BytesIO
import numpy as np

def main():
  soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = "127.0.0.1"
  port = 4000
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