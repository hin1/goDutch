#Google Cloud Vision allows 1000 scans per month
#Reference: https://medium.com/searce/tips-tricks-for-using-google-vision-api-for-text-detection-2d6d1e0c6361

import os

# Remember to transfer the key to server
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/seanchan/Documents/Orbital/goDutch/GoDutch-641ac56fc8a1.json"
#Image file to process
#file_name = "/Users/seanchan/goDutch/test/testpic3.jpg"

import argparse #Purely for testing
from PIL import Image, ImageDraw
from enum import Enum
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
import pprint

#Enumerations to denote type of information being detected
class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

def save_dict(file, dictionary):
    
    split_file = os.path.splitext(file)
    new_name = split_file[0] + "-full_response.txt"
    
    new_file = open(new_name,'w+')
    new_file.write(str(dictionary))
    new_file.close()
    print("File saved: " + new_name)

def get_full_response_dict(file_name):
    #Instantiate client
    client = vision.ImageAnnotatorClient()

    with open(file_name, "rb") as f:
        img_content = f.read()

    img = types.Image(content=img_content)

    #Label detection
    response = client.text_detection(image=img)
    dict_response = MessageToDict(response,preserving_proto_field_name = True)
    
    texts = dict_response["text_annotations"]
    full_text = dict_response["full_text_annotation"]
    #texts = response.text_annotations
    #full_text = response.full_text_annotation

    save_dict(file_name,dict_response)
    
    #print("Text_annotation:")
    #print(texts)
    #print("\n")
    #print("Full_text_annotation:")
    #print(full_text)

    return texts
    

def get_basic_text(file_name):
    
    #Instantiate client
    client = vision.ImageAnnotatorClient()

    with open(file_name, "rb") as f:
        img_content = f.read()

    img = types.Image(content=img_content)

    #Label detection
    response = client.text_detection(image=img)
    texts = response.text_annotations

    txt = []
    
    for text in texts:
        print('{} '.format(text.description), end = ' ')
        txt.append(text)
        #vertices = (['({},{})'.format(vertex.x, vertex.y)
        #            for vertex in text.bounding_poly.vertices])
        #print('bounds: {}'.format(','.join(vertices)))

    return txt

'''TESTING FUNCTIONS'''

#Draws a border around the bounding box
# image: The path to the image to draw boxes in
# boundaries: Either a list of 2-tuples [(x1,y1),(x2,y2)...] or a list of consecutive x and y coordinates [x1,y1,x2,y2...]
#             Lines drawn in between every 2 consecutive points, and between first and last point
# colour: Either common HTML colours (case insensitive) or Hexadecimal colour specifiers (e.g. #rgb or #rrggbb)
def draw_boxes(image, boundaries, colour):
    draw = ImageDraw.Draw(image)

    for bound in boundaries:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, colour)
        #None refers to the fill of the polygon
    return image

#Returns bounds of a document
# image_file: the file path of the image to detect text from
# feature: FeatureType.BLOCK/PARA/WORD/SYMBOL
def get_document_bounds(image_file, feature):

    client = vision.ImageAnnotatorClient()
    bounds = []

    with open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    # bounding_box order is: top left, top right, bottom right, bottom left
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)

                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)

                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)

        if (feature == FeatureType.PAGE):
            bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.PAGE)
    draw_boxes(image, bounds, 'blue')
    bounds = get_document_bounds(filein, FeatureType.PARA)
    draw_boxes(image, bounds, 'red')
    bounds = get_document_bounds(filein, FeatureType.WORD)
    draw_boxes(image, bounds, 'yellow')

    if fileout is not 0:
        image.save(fileout)
    else:
        #This method saves the image to a temporary PNG file, and opens it with the native Preview application.
        image.show()

'''
def main():
    get_raw_txt(file_name)

# Type into terminal: python3 google_ocr.py <image_file> [-out_file <save_file>]
if __name__ == '__main__':
    main()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('detect_file', help='The image for text detection.')
    parser.add_argument('-out_file', help='Optional output file', default=0)
    args = parser.parse_args()

    render_doc_text(args.detect_file, args.out_file)
'''









