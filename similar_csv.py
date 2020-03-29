#!/usr/bin/env python
import time
import tqdm
import argparse
import os
import numpy as np
import pandas as pd
import pickle

from image_utils import similarity

PREDICTION_LENGTH = 4096

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", default="/usr/src/app/files/files-urls.csv", type=str, help="path to CSV file (default: /usr/src/app/files/files-urls.csv)")
parser.add_argument("-p", "--predictions_folder", default="/usr/src/app/files/predictions", type=str, help="Folder where predictions are located (default: /usr/src/app/files/predictions)")
parser.add_argument("-d", "--destination", default="/usr/src/app/files/similarities", type=str, help="Folder where to save results. Multiple files for each process will be created. (default: /usr/src/app/files/similarities)")
parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files if they exist')

args = parser.parse_args()

file = args.file
predictions_folder = args.predictions_folder
destination = args.destination
overwrite = args.overwrite

if (not os.path.exists(file)):
  print("File %s does not exist." % file)
  exit()

if (not os.path.exists(predictions_folder)):
  print("Folder %s does not exist." % predictions_folder)
  exit()

if (not os.path.exists(destination)):
  print("Folder %s does not exist." % destination)
  exit()

# get the base name for output file creation
fullname = os.path.basename(file)
base = os.path.splitext(fullname)[0]

starttime = time.time()

url_df = pd.read_csv(file, index_col="access_pid")

count = len(url_df.filename)

print("Getting similarity for %s files." % count)

skipped = []
features = []

for access_pid, row in tqdm.tqdm(url_df.iterrows(), total=count):
  id = row['id']
  predictions_file = "%s/%s.json.gz" % (predictions_folder, id)
  if (not os.path.exists(predictions_file)):
    skipped.append(id)
    features.append(np.zeros(shape=(PREDICTION_LENGTH,))) # no predictions for this file so we add empty (all items must be present)
  else:
    predictions = np.loadtxt(predictions_file)
    features.append(predictions)

if (len(skipped) > 0):
  print("Skipped %s files." %  len(skipped))

pca_features, pca = similarity.transform_features(features)
pca_filename = "%s/%s_pca.p" % (destination, base)

if (not os.path.exists(pca_filename) or overwrite):
  pickle.dump([url_df, pca_features, pca], open(pca_filename, 'wb'))

tsne_features, tx, ty = similarity.tsne_ify(pca_features)
tsne_filename = "%s/%s_tsne.p" % (destination, base)

if (not os.path.exists(tsne_filename) or overwrite):
  pickle.dump([tsne_features, tx, ty], open(tsne_filename, 'wb'))

grid, nx, ny = similarity.rasterize_tsne(tsne_features, count)
output_filename = "%s/%s.txt" % (destination, base)

if (not os.path.exists(output_filename) or overwrite):
  # put the width/height info in the first row of the grid
  grid = np.insert(grid, 0, [nx, ny], axis=0)
  np.savetxt(output_filename, grid, fmt='%u')

print("Processed %s files in {} seconds".format(time.time() - starttime) % count)

if (len(skipped) > 0):
  print("Skipped %s files:" % len(skipped))
  print(skipped)