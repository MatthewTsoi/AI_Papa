##Main program 
## Before running this program, you need to have functional aws cli and boto3 installed.
##^^^^^^
##Author: matthew.tsoi@gmail.com

import boto3
from botocore.exceptions import ClientError
import logging,time, io, os
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

    client=boto3.client('rekognition')
    response = client.create_collection(CollectionId=collectionId)

    logging.info('Collection ARN: ' + response['CollectionArn'])
    logging.info('Status code: ' + str(response['StatusCode']))

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

    tic=time.time()

    logging.info('Reading image file: '+filename)
    image = Image.open(open(filename,'rb'))
    stream = io.BytesIO()
    image.save(stream, format=image.format)
    image_binary = stream.getvalue()

    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collectionId,
                                #Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                Image={'Bytes': image_binary},
                                ExternalImageId=os.path.splitext(os.path.basename(filename))[0],
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    toc = time.time()

    logging.info ('Results for image file' + filename+'. Processing time: '+str(round((toc-tic),2))+' sec.')	
    logging.debug ('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
        logging.info('  Face signature: ' + faceRecord['Face']['FaceId'])
        logging.info('  Face ID: ' + faceRecord['Face']['ExternalImageId']) 
        logging.info('  Confidence: {}'.format(faceRecord['Face']['Confidence']))
        logging.debug('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
        
        faceIds.append([faceRecord['Face']['ExternalImageId'],faceRecord['Face']['FaceId']])
   
    return faceIds

    #print('Faces not indexed:')
    #for unindexedFace in response['UnindexedFaces']:
    #    print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
    #    print(' Reasons:')
    #    for reason in unindexedFace['Reasons']:
    #        print('   ' + reason)

def detectFaces(img='',debug=False):
    #Get a list of face IDs from an image 

    faces=[]
    photo= img
    # Open image and get image data from stream.
    image = Image.open(open(photo,'rb'))
    stream = io.BytesIO()
    image.save(stream, format=image.format)
    image_binary = stream.getvalue()

    client = boto3.client('rekognition')

    tic = time.time() 
    response = client.detect_faces(Image={'Bytes': image_binary},Attributes=['ALL'])

    toc = time.time() 

    logging.info('['+img+'] Face detection completed. '+str(len(response['FaceDetails']))+' faces detected in '+str(round(toc-tic,4))+'sec.')

    for faceDetail in response['FaceDetails']:
        #print('The detected face is between ' +
        #      str(faceDetail['AgeRange']['Low']) +
        #      ' and ' + str(faceDetail['AgeRange']['High']) +
        #      ' years old')
        #print('The gender of detected face is'+str(faceDetail['Gender']))

        box = faceDetail['BoundingBox']
        #print(box)
        imgWidth, imgHeight = image.size
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']

        face=image.crop((left,top,left+width,top+height))
        faces.append(face)

        #ImageDraw.Draw(face)
        if debug:
            face.show()
                
    if debug:
        image.show()

    return faces

def matchFaces(collecitonId='',img_file='',debug=False):
    ##Match detected faces with existing collection


    tic = time.time()
    ##Get a list of faces from photo 
    faces=detectFaces(img_file)

    matched_faces=[]

    client = boto3.client('rekognition')
    for face in faces:
        stream = io.BytesIO()
        face.save(stream, format='PNG')
        image_binary = stream.getvalue()

        response = client.search_faces_by_image(CollectionId=collecitonId,Image={
        'Bytes': image_binary},MaxFaces=123)
    
        if debug:
            print (response['FaceMatches'])
            face.show()

        if response['FaceMatches']:
            #face.show()
            #logging.info(response['FaceMatches']['ExternalImageId'])
            logging.info('['+img_file+'] Matched person ['+response['FaceMatches'][0]['Face']['ExternalImageId']+'] with similarity '+str(round(response['FaceMatches'][0]['Similarity'],2))+'%')

            matched_faces.append(response['FaceMatches'][0]['Face']['ExternalImageId'])

    toc = time.time()

    logging.info('['+img_file+'] Face matched completed and found ['+str(len(matched_faces))+'] faces in '+str(round(toc-tic,4))+'sec.')

    return matched_faces

##Main routine
if __name__ == "__main__":
    
    ##parameters defaults
    input_folder='./in_photo/'
    input_face_folder = './in_face/'
    output_folder='./out_photo'
    

    ##init logger 
    init_logger() 

    removeCollection('faceCollection')

    ##Create a face index collection
    createCollection('faceCollection')

    ##Add face index into collection from face index folder 
    #logging.info(addFaces('./in_face/donald.jpg','faceCollection'))
    directory = os.fsencode(input_face_folder)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)   
        if filename.endswith(".jpeg") or filename.endswith(".jpg"): 
            #print(input_folder+filename)
            #print(filename)
            logging.info(addFaces(input_face_folder+'/'+filename,'faceCollection'))
            continue
        else:
            continue
    




    directory = os.fsencode(input_folder)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)   
        if filename.endswith(".jpeg") or filename.endswith(".jpg"): 
            #print(input_folder+filename)
            #print(filename)
            matchFaces('faceCollection',input_folder+'/'+filename)
            continue
        else:
            continue
    
    ##Detech faces for an imag
    #print(matchFaces('faceCollection','./in_photo/gathering_0001.jpeg'))