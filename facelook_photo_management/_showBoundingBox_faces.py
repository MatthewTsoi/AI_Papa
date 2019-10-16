
import boto3
import io
from argparse import ArgumentParser
from PIL import Image, ImageDraw, ExifTags, ImageColor

if __name__ == "__main__":

    #Parse input arguements
    parser = ArgumentParser(prog="show detected face",description="Using AWS Rekcognition service to identify face in a photo")
    ##Configure input arguements 
    parser.add_argument("--input_photo", type=str, help="Photo to identify face.")

    args = parser.parse_args()

    # Change photo to the path and filename of your image.
    photo = args.input_photo

    # Open image and get image data from stream.
    image = Image.open(open(photo,'rb'))
    stream = io.BytesIO()
    image.save(stream, format=image.format)
    image_binary = stream.getvalue()

    client = boto3.client('rekognition')
    response = client.detect_faces(Image={'Bytes': image_binary},
                                   Attributes=['ALL'])

    draw = ImageDraw.Draw(image)

    # Calculate and display a bounding box around each detected face
    print('Detected faces for ' + photo)
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' +
              str(faceDetail['AgeRange']['Low']) +
              ' and ' + str(faceDetail['AgeRange']['High']) +
              ' years old')

        box = faceDetail['BoundingBox']
        print(box)
        imgWidth, imgHeight = image.size
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
                
        print('Left: ' + '{0:.0f}'.format(left))
        print('Top: ' + '{0:.0f}'.format(top))
        print('Face Width: ' + "{0:.0f}".format(width))
        print('Face Height: ' + "{0:.0f}".format(height))

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)

        )
        draw.line(points, fill='#00d400', width=8)

        # Alternatively can draw rectangle. However you can't set line width.
        # draw.rectangle([left,top, left + (width * box['Width']), top +(height * box['Height'])], outline='yellow')

    image.show()

