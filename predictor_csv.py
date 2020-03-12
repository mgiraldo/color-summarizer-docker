#!/usr/bin/env python
import time
import pandas as pd
import tqdm
import os
from pathlib import Path
import argparse
import socket
import sys
from io import BytesIO
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", default="/usr/src/app/files/files-urls.csv", type=str, help="path to CSV file (default: /usr/src/app/files/files-urls.csv)")
parser.add_argument("-o", "--origin_folder", default="/usr/src/app/files", type=str, help="Folder where images are located (default: /usr/src/app/files)")
parser.add_argument("-d", "--destination", default="/usr/src/app/files/predictions", type=str, help="Folder where to save results (default: /usr/src/app/files/predictions)")
parser.add_argument("--host", default="127.0.0.1", type=str, help="Prediction server host (default: 127.0.0.1)")
parser.add_argument("--port", default=4000, type=str, help="Prediction server socket port (default: 4000)")

args = parser.parse_args()

file = args.file
origin_folder = args.origin_folder
destination = args.destination
host = args.host
port = args.port

count=0
starttime = time.time()

if (os.path.exists(file) == False):
  print("File %s does not exist." % file)
  exit()

if (os.path.exists(origin_folder) == False):
  print("Folder %s does not exist." % origin_folder)
  exit()

if (os.path.exists(destination) == False):
  print("Folder %s does not exist." % destination)
  exit()

url_df = pd.read_csv(file, index_col="id")

count = len(url_df.filename)

skipped = []

print("Predicting %s files using %s:%s" % (count, host, port))

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
packet_size = 4096

try:
  soc.connect((host, port))
except:
  print("Connection error")
  exit()

def predict_file(id, row):
  filename = row.filename
  # filename comes 0000XXXXXX.jpg and destination is 0000/0000XXXXXX.jpg
  path = "%s/%s/%s" % (origin_folder, filename[0:4], filename)
  if (Path(path).exists() == False):
    # no image
    skipped.append(row)
    return
  json = "%s/%s.json.gz" % (destination, id)
  if (Path(json).exists() == False):
    try:
      soc.sendall(path.encode("utf8"))
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
        np.savetxt(json, final_array)
    except:
      skipped.append(row)
      return

for id, row in tqdm.tqdm(url_df.iterrows(), total=count):
  predict_file(id, row)

soc.send(b'--quit--')

print("Processed %s files in {} seconds".format(time.time() - starttime) % count)

if (len(skipped) > 0):
  print("Skipped %s files:", len(skipped))
  print(skipped)