# Image Analysis Utils

Python and Ruby convenience files to do color and object analysis in a set of images:

- Color Summarizer based on [Martin Krzywinski's project](http://mkweb.bcgsc.ca/colorsummarizer/)
- Keras/TensorFlow Object Predictor
- Scikit-Learn PCA/t-SNE image similarity based on [Gene Kogan's work](https://ml4a.github.io/)

## Color Summarizer Web API

Runs the [color summarizer](http://mkweb.bcgsc.ca/color-summarizer/) as a web application that can be queried.

## To build and use

> NOTE: **Placeholder**. `docker-compose` tasks not finalised. In the meantime use normal `docker` commands.

```
docker pull mgamga/color-summarizer
docker-compose build
```
Run `docker-compose up predictor` to run the object detection/prediction server.

Run `docker-compose up colors` to run the color summarizer server.

This will run the app in port `5000`. Test it visiting:

`http://localhost:5000/?path=/path/to/file.jpg`

~~`http://localhost:5000/pretty?url=https://c2.staticflickr.com/8/7411/11187582405_2befbdca1e.jpg`~~

You should see something like this:

````
{
  "imgdata": {
    "@file": "/path/to/file.jpg",
    "@width_original": "150",
    "@width": "50",
    "@height_original": "150",
    "@height": "50",
    "clusters": {
      "cluster": [
        ...
      ]
    },
    "stats": {
      ...
    },
    "histogram": {
      ...
    }
  }
}
````

## Parameters

### Summarizer

~~The app expects a `/:type?url=IMAGE_URL` request where `type` can be `text`, `json`, `xml`, or `pretty` and `url` has to be a valid URL to an image file. If no `type` is specified `json` will be assumed.~~

See (legacy Ruby code is still there in case you're interested):

- `/image_utils/similarity.py`
- `/summarize_file.py`
- `/summarize_csv.py`
- `/app.py` 

### Predictor

See:

- `/predictor_server.py`
- `/predictor_client.py`
- `/predictor_csv.py`

### Similarity

See:

- `/image_utils/similarity.py`
- `/similar_csv.py`

## Source code

Get the source code in https://github.com/mgiraldo/image-utils

Get the Docker container in https://hub.docker.com/r/mgamga/image-utils/

## Credits

[Color summarizer](http://mkweb.bcgsc.ca/colorsummarizer/) by Martin Krzywinski

[Matt Miller](https://twitter.com/thisismmiller) did the [Docker summarizer](https://github.com/thisismattmiller/color-summarizer-docker) on which this project is based.

James Higginbotham's [tutorial on Docker and Sinatra APIs](https://dzone.com/articles/deploying-rest-apis-to-docker-using-ruby-and-sinat).

Sample image via [The Finnish Museum of Photography](https://www.flickr.com/photos/valokuvataiteenmuseo/11187582405/).
