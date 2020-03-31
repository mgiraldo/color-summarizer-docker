#!/usr/bin/env python
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from PIL import Image
import rasterfairy
import math
import numpy as np

DEFAULT_COMPONENT_SIZE = 300

def transform_features(features):
  components = DEFAULT_COMPONENT_SIZE
  if (len(features) < components):
    components = len(features)
  print("one")
  features = np.array(features)
  print("two")
  pca = PCA(n_components=components)
  print("three")
  pca.fit(features)
  print("four")
  pca_features = pca.transform(features)
  print("five")
  return pca_features, pca

def tsne_ify(pca_features):
  print("six")
  X = np.array(pca_features)
  print("seven")
  tsne_features = TSNE(n_components=2, learning_rate=150, perplexity=30, angle=0.2, verbose=2).fit_transform(X)
  print("eight")
  tx, ty = get_tsne_xy(tsne_features)
  print("nine")
  return tsne_features, tx, ty

def get_tsne_xy(tsne):
  tx, ty = tsne[:,0], tsne[:,1]
  tx = (tx-np.min(tx)) / (np.max(tx) - np.min(tx))
  ty = (ty-np.min(ty)) / (np.max(ty) - np.min(ty))
  return tx, ty

def rasterize_tsne(tsne, count):
  side = math.sqrt(count)
  nx = math.ceil(side)
  ny = round(side)
  print("ten %s %s %s" % (side, nx, ny))
  grid_assignment = rasterfairy.transformPointCloud2D(tsne, target=(nx, ny))
  print("eleven")
  grid = grid_assignment[0]
  return grid, nx, ny

## HELPERS ##

def get_image_distances(query_image_idx, pca_features, reverse=False):
  distances = [ distance.cosine(pca_features[query_image_idx], feat) for feat in pca_features ]
  idx_closest = sorted(range(len(distances)), key=lambda k: distances[k], reverse=reverse)
  return idx_closest

def get_close_midway_far_images(query_image_idx, pca_features, num_results=5):
  midway = int(float(len(pca_features)) * 0.5)
  idx_all = get_image_distances(query_image_idx, pca_features)
  idx_closest = idx_all[1:num_results+1]
  idx_midway = idx_all[midway:num_results+midway]
  idx_farthest = idx_all[len(pca_features)-num_results:len(pca_features)]
  return idx_closest, idx_midway, idx_farthest

def get_closest_images(query_image_idx, pca_features, num_results=5):
  idx_closest = get_image_distances(query_image_idx, pca_features)[1:num_results+1]
  return idx_closest

def get_midway_images(query_image_idx, pca_features, num_results=5):
  midway = int(float(len(pca_features)) * 0.5)
  idx_midway = get_image_distances(query_image_idx, pca_features)[midway:num_results+midway]
  return idx_midway

def get_farthest_images(query_image_idx, pca_features, num_results=5):
  idx_farthest = get_image_distances(query_image_idx, pca_features, reverse=True)[0:num_results]
  return idx_farthest

def get_concatenated_images(indexes, thumb_height, image_names):
  thumbs = []
  for idx in indexes:
    filename = path_for_filename(image_names[idx])
    img = image.load_img(filename)
    img = img.resize((int(img.width * thumb_height / img.height), thumb_height))
    thumbs.append(img)
  concat_image = np.concatenate([np.asarray(t) for t in thumbs], axis=1)
  return concat_image
