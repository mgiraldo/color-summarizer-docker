#!/usr/bin/env python

from flask import Flask, jsonify, render_template, request, send_from_directory
from image_utils import summary
import json

app = Flask(__name__, template_folder="./views", static_url_path="")

@app.route("/", defaults={"render_type": "json"})
@app.route("/<string:render_type>")
def index(render_type):
  if "path" in request.args:
    image_path = request.args.get("path")
    json_str = summary.summarize(image_path)
    output = json.loads(json_str)
    hexes = []
    for cluster in output['imgdata']['clusters']['cluster']:
      hex = cluster['hex']['@hex']
      hexes.append(hex)
    if render_type == "pretty":
      return render_template("pretty.html", output=output, hexes = hexes, path=image_path)
    else:
      return jsonify(output)
  else:
    return "Provide a path to summarize."

@app.route("/assets/<path:filename>")
def send_asset(filename):
  return send_from_directory("./assets", filename)

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0")