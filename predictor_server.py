import numpy as np
import keras
from keras.models import Model
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions, preprocess_input

# for the server
import socket
import sys
import traceback
from threading import Thread
from io import BytesIO

# load model and ignore model errors
np.seterr(divide='ignore', invalid='ignore')
model = keras.applications.VGG16(weights='imagenet', include_top=True)
feat_extractor = Model(inputs=model.input, outputs=model.get_layer("fc2").output)

def main():
  start_server()

def start_server():
  host = "127.0.0.1"
  port = 4000 # arbitrary non-privileged port

  soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
  print("Socket created")

  try:
    soc.bind((host, port))
  except:
    print("Bind failed. Error : " + str(sys.exc_info()))
    sys.exit()

  soc.listen(5)       # queue up to 5 requests
  print("Socket now listening")

  # infinite loop- do not reset for every requests
  while True:
    connection, address = soc.accept()
    ip, port = str(address[0]), str(address[1])
    print("Connected with " + ip + ":" + port)

    try:
      Thread(target=client_thread, args=(connection, ip, port)).start()
    except:
      print("Thread did not start.")
      traceback.print_exc()

  soc.close()

def load_image(path):
  try:
    img = image.load_img(path, target_size=model.input_shape[1:3])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return img, x
  except:
    return None, None

def predict_image(path):
  img, x = load_image(path)
  feat = feat_extractor.predict(x)[0]
  return feat

def client_thread(connection, ip, port, max_buffer_size = 4096):
  is_active = True

  while is_active:
    path = receive_input(connection, max_buffer_size)

    if "--quit--" in path:
      print("Client is requesting to quit")
      connection.close()
      print("Connection " + ip + ":" + port + " closed")
      is_active = False
    else:
      try:
        print("Processing path: {}".format(path))
        x = predict_image(path)
        f = BytesIO()
        np.savez_compressed(f, frame=x)
        f.seek(0)
        out = f.read()
        connection.sendall(out)
      except BrokenPipeError:
        print("Connection closed")
      except FileNotFoundError:
        print("[error] image does not exist: %s" % path)
        connection.sendall("-".encode("utf-8"))
      except IOError:
        print("[error] not an image: %s" % path)
        connection.sendall("-".encode("utf-8"))
      except ValueError:
        print("[error] could not be processed: %s" % path)
        connection.sendall("-".encode("utf-8"))
      except IndexError:
        print("[error] in keras preprocess_input")
        connection.sendall("-".encode("utf-8"))

def receive_input(connection, max_buffer_size):
  client_input = connection.recv(max_buffer_size)
  client_input_size = sys.getsizeof(client_input)

  if client_input_size > max_buffer_size:
    print("The input size is greater than expected {}".format(client_input_size))

  path = client_input.decode("utf8").rstrip()  # decode and strip end of line

  return path

if __name__ == "__main__":
  main()