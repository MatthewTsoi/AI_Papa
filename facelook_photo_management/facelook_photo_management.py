##Main program 
## Before running this program, you need to have functional aws cli and boto3 installed.
##^^^^^^
##Author: AI_Papa  (matthew.tsoi@gmail.com) 

##Import AWS client modules
import boto3
from botocore.exceptions import ClientError

##Import modules for multi-thread and general OS utilities
import logging,time, io, os, shutil
from threading import Thread
from argparse import ArgumentParser

##Import mode for image processing, **Need additional PIP install 
from PIL import Image#, ImageDraw, ExifTags, ImageColor

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
    #maxResults = 2

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

    logging.info('['+filename+'] Reading image file: '+filename)
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

    logging.info ('['+filename+'] Add face completed. Processing time: '+str(round((toc-tic),2))+' sec.')	
    logging.debug ('['+filename+'] Faces indexed:')						
    for faceRecord in response['FaceRecords']:
        logging.info('['+filename+']  Face signature: ' + faceRecord['Face']['FaceId'])
        logging.info('['+filename+']  Face ID: ' + faceRecord['Face']['ExternalImageId']) 
        logging.info('['+filename+']  Confidence: {}'.format(faceRecord['Face']['Confidence']))
        logging.debug('['+filename+']  Location: {}'.format(faceRecord['Face']['BoundingBox']))
        
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

def matchFace(collectionId='',face='',input_folder='',path_sep='',img_file='',output_folder='',threshold=70,debug=False):
    stream = io.BytesIO()
    face.save(stream, format='PNG')
    image_binary = stream.getvalue()

    client = boto3.client('rekognition')

    try:
        response = client.search_faces_by_image(CollectionId=collectionId,FaceMatchThreshold=threshold,Image={'Bytes': image_binary},MaxFaces=123)
    except:
        if debug:
            face.show() 
        return 

    if debug:
        print (response['FaceMatches'])
        face.show()

    if response['FaceMatches']:
        #face.show()
        logging.info('['+img_file+'] Matched person ['+response['FaceMatches'][0]['Face']['ExternalImageId']+'] with similarity '+str(round(response['FaceMatches'][0]['Similarity'],2))+'%')

        matched_person = response['FaceMatches'][0]['Face']['ExternalImageId']
        
        ##creaete person folder if it does not exists yet
        if os.path.exists(output_folder+path_sep+matched_person):
            pass
        else:
            os.mkdir(output_folder+path_sep+matched_person)

        shutil.copyfile(input_folder+path_sep+img_file,output_folder+path_sep+matched_person+path_sep+img_file)
        

    
def matchFaces(collectionId='',input_folder='',path_sep="\\",img_file='',output_folder='',threshold=70,debug=False):
    ##Match detected faces with existing collection


    tic = time.time()
    ##Get a list of faces from photo 
    faces=detectFaces(input_folder+path_sep+img_file,debug=debug)

    threads=[]

    #client = boto3.client('rekognition')
    for face in faces:

        t=Thread(target=matchFace,args=(collectionId,face,input_folder,path_sep,img_file,output_folder,threshold,debug))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join(180)

    toc = time.time()  


    #logging.info('['+img_file+'] Face matched completed and found ['+str(len(matched_faces))+'] faces in '+str(round(toc-tic,4))+'sec.')
    logging.info('['+img_file+'] Face matched completed in '+str(round(toc-tic,4))+'sec.')

#    return matched_faces

def isWindows():
    if os.name=='nt':
        return True
    else:
        return False

##Main routine
if __name__ == "__main__":
    
    overall_tic=time.time() 

    ##input arguements defaults
    #input_folder='./in_photo/'
    #input_face_folder = './in_face/'
    #output_folder='./out_photo'
    #threshold=70

    #Parse input arguements
    parser = ArgumentParser(prog="facelook",description="Using AWS Rekcognition service to sort photo by invidial matched face (person)",usage="Use face recongnition to management photos")

    ##Configure input arguements 
    parser.add_argument("--input_folder", default='./in_photo/', type=str, help="Folder path for photos to be process.")
    parser.add_argument("--input_face_folder", default='./in_face/', type=str, help="Folder path face photo. Filename will be used as face reference ID")
    parser.add_argument("--output_folder", default='./out_photo/', type=str, help="Output folder")
    parser.add_argument("--threshold", default=85, type=int, help="Threshold face similarity match") 
   
    args = parser.parse_args()

    if args.input_folder is not None:
        input_folder=args.input_folder
    if args.input_face_folder is not None:
        input_face_folder=args.input_face_folder
    if args.output_folder is not None:
        output_folder=args.output_folder
    if args.threshold is not None:
        threshold=args.threshold
        


    
    ##determine OS platform to define path separator 
    if isWindows():
        path_sep='\\'
    else:
        path_sep='/'

    ##init logger 
    init_logger() 

    try:
        removeCollection('faceCollection')
    except:
        logging.warning('Collection does not exists!')

    ##Create a face index collection
    createCollection('faceCollection')

    ##Add face index into collection from face index folder 
    #logging.info(addFaces('./in_face/donald.jpg','faceCollection'))
    directory = os.fsencode(input_face_folder)
    threads=[]

    tic=time.time()

    for file in os.listdir(directory):
        filename = os.fsdecode(file)   
        if filename.endswith(".jpeg") or filename.endswith(".jpg"): 
            #addFaces(input_face_folder+path_sep+filename,'faceCollection')
            t=Thread(target=addFaces,args=(input_face_folder+path_sep+filename,'faceCollection'))
            t.start()
            threads.append(t)
    logging.info(str(len(threads))+' threads started for face index processing.')
    ##Wait for all face index threads completed
    for t in threads:
        t.join(180)

    toc=time.time()
    logging.info('All faces added to collect in '+str(round(toc-tic,4))+'sec.')
    
    #time.sleep(3)

    ##Now detect faces from photo collection and put them into identified person folder(s)
    directory = os.fsencode(input_folder)
    threads=[]
    for file in os.listdir(directory):
        filename = os.fsdecode(file)  
        if filename.endswith(".jpeg") or filename.endswith(".jpg"): 
            
            #matchFaces('faceCollection',input_folder,path_sep,filename,output_folder)
            t=Thread(target=matchFaces,args=('faceCollection',input_folder,path_sep,filename,output_folder,threshold))
            t.start()
            threads.append(t)
    
    for t in threads:
        t.join(60)


    overall_toc=time.time()
    logging.info('Process completed in '+str(round(overall_toc-overall_tic,2))+' sec.')
    ##Remove the face collection 
    #removeCollection('faceCollection')