##Main program 
## Before running this program, you need to have functional aws cli and boto3 installed.
##^^^^^^
##Author: matthew.tsoi@gmail.com

import boto3
from botocore.exceptions import ClientError
import logging,time, io
from PIL import Image, ImageDraw, ExifTags, ImageColor

def init_logger():
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='facelook_photo_management.log',
                    filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.info('Logger started!') 

def createCollection(collectionId=''):

    logging.info('Creating face index collection ['+collectionId+']')
    # Replace collectionID with the name of the collection that you want to create.
    maxResults = 2

    # Create a collection
    logging.info('Creating collection:' + collectionId)

    client=boto3.client('rekognition')
    response = client.create_collection(CollectionId=collectionId)

    logging.info('Collection ARN: ' + response['CollectionArn'])
    logging.info('Status code: ' + str(response['StatusCode']))
    logging.info('Done...')

    if response['StatusCode']==200:
        logging.info('Collection created successfully!')
        return  response['CollectionArn']
    else:
        return 0 

def removeCollection(collectionId=''):
    
    logging.info('Attempting to delete collection ' + collectionId)
    client=boto3.client('rekognition')
    statusCode=''

    try:
        response=client.delete_collection(CollectionId=collectionId)
        statusCode=response['StatusCode']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info ('The collection ' + collectionId + ' was not found ')
        else:
            logging.error ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        statusCode=e.response['ResponseMetadata']['HTTPStatusCode']
    logging.info('Operation returned Status Code: ' + str(statusCode))


def addFaces(filename='',collectionId=''):

    faceIds = []

    image = Image.open(open(filename,'rb'))
    stream = io.BytesIO()
    image.save(stream, format=image.format)
    image_binary = stream.getvalue()

    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collectionId,
                                #Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                Image={'Bytes': image_binary},
                                ExternalImageId=filename,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    logging.info ('Results for ' + photo) 	
    logging.debug ('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         logging.debug('  Face ID: ' + faceRecord['Face']['FaceId'])
         logging.debug('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

         faceIds.append(faceRecord['Face']['FaceId'])

    return faceIds

    #print('Faces not indexed:')
    #for unindexedFace in response['UnindexedFaces']:
    #    print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
    #    print(' Reasons:')
    #    for reason in unindexedFace['Reasons']:
    #        print('   ' + reason)




##Main routine
if __name__ == "__main__":

    ##init logger 
    init_logger() 

    removeCollection('faceCollection')

    ##Create a face index collection
    createCollection('faceCollection')

    ##Add face index into collection from face index folder 
    #addFaces('/Users/Matthew/Desktop/test_2.jpg','faceCollection')