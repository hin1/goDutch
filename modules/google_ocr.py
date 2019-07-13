# Note: Google Cloud Vision API has a limit of 1000 uploads per month

import os
from google.cloud import vision
from google.cloud.vision import types

#Instantiate client
client = vision.ImageAnnotatorClient()

#Identifying image to annotate



