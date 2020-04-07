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
pca_filename = "%s/%s_pca.p" % (destination, base)
umap_filename = "%s/%s_umap.p" % (destination, base)
output_filename = "%s/%s.txt" % (destination, base)

starttime = time.time()

url_df = pd.read_csv(file, index_col="access_pid")

count = len(url_df.filename)

print("Getting similarity for %s files." % count)

def skip_row(id, features, skipped):
  skipped.append(id)
  features.append(np.zeros(shape=(PREDICTION_LENGTH,)))
  return features, skipped

def load_predictions():
  skipped = []
  features = []
  for access_pid, row in tqdm.tqdm(url_df.iterrows(), total=count):
    id = row['id']
    predictions_file = "%s/%s.json.gz" % (predictions_folder, id)
    if (not os.path.exists(predictions_file)):
      # no predictions for this file
      features, skipped = skip_row(id, features, skipped)
    else:
      try:
        # TODO: this seems to be printing info even though it's in try/except
        predictions = np.loadtxt(predictions_file)
        if (len(predictions) == PREDICTION_LENGTH):
          features.append(predictions)
        else:
          # wrong file length
          features, skipped = skip_row(id, features, skipped)
      except OSError:
        # the zip was corrupt
        features, skipped = skip_row(id, features, skipped)
  if (len(skipped) > 0):
    print("Skipped %s files:" % len(skipped))
    print(skipped)
  return features

pca_exists = os.path.exists(pca_filename)
umap_exists = os.path.exists(umap_filename)
output_exists = os.path.exists(output_filename)

def do_pca(features):
  features = np.array(features)
  pca_features, pca = similarity.transform_features(features)
  if (not pca_exists or overwrite):
    pickle.dump([url_df, pca_features, pca], open(pca_filename, 'wb'))
  return pca_features, pca

def do_umap(pca_features):
  umap_features, tx, ty = similarity.umap_ify(pca_features)
  if (not umap_exists or overwrite):
    pickle.dump([umap_features, tx, ty], open(umap_filename, 'wb'))
  return umap_features, tx, ty

def do_similarity(features):
  # we don't ask if it exists because then what's the point of running this file?
  count = len(features)
  grid, nx, ny = similarity.rasterize_umap(features, count)
  # put the width/height info in the first row of the grid
  grid = np.insert(grid, 0, [nx, ny], axis=0)
  np.savetxt(output_filename, grid, fmt='%u')

if (overwrite or (not pca_exists and not umap_exists)):
  features = load_predictions()
  pca_features, pca = do_pca(features)
  umap_features, tx, ty = do_umap(pca_features)
else:
  # first do pca
  if (pca_exists):
    print("loaded pca %s" % pca_filename)
    url_df, pca_features, pca = pickle.load(open(pca_filename, 'rb'))
  else:
    features = load_predictions()
    pca_features, pca = do_pca(features)
  # now umap
  if (umap_exists):
    print("loaded umap %s" % umap_filename)
    umap_features, tx, ty = pickle.load(open(umap_filename, 'rb'))
  else:
    umap_features, tx, ty = do_umap(pca_features)
  # now rasterize
  do_similarity(umap_features)

print("Processed %s files in {} seconds".format(time.time() - starttime) % count)
