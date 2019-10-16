# Facelook Photo Management tool
Face lookup tool for photo management using simple implementation of AWS Rekcognition services 

> ## How can I sort out **thousands** photos and place them into different folders for individual faces? 

## Problem statement 
One day, you and your family joined a birthday party. Everyone really enjoy it, and you even feel better as you used your new camera to take more than `two thousands(!!)` photos and tried out all the new (cool) features. 
At the end of the event, parents suggest that "Hey Matt, please send me those photo I am on it, thx!"


## The solution
Use **`AI`** to recognize your friends' face (signature) and let the program to sort them out for you :+1: 
Face recogition nowadays is a relatively mature technology, we are going to use/demo [AWS rekognition](
https://docs.aws.amazon.com/rekognition/latest/dg/faces.html) services to achieve this without the complexity to train and manage the NN/CNN behind.

### Prepartion 

- [x] Get AWS account (there are free tiers for photo recognition)
- [x] Setup your [AWS client](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) in your desktop
- [x] Setup your python 3.6+ environment including AWS boto3 [link](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) and Pillow modules. Refer to requirements.txt for python modules used. 

Alternatively, you can install these with below 2 command 

```
pip install Pillow
pip install boto3
```
- [x] Last, you need to prepare faces of your friends in a fold (named input_face_folder as parameter) 


#### Prepare for the "faces"
Before we can create copies for individuals. We need to prepare a photo of that person with name as file name. 

For example, if you want to index your friend "Donald", you need to have his photo (the one and only one face on the photo!) as donanld.jpg. You can directly crop from existing photo with minimum resultion of 40x40 pixels.  
Detail can be find on AWS [limitation page](https://en.wikipedia.org/wiki/File:Donald_Trump_official_portrait.jpg) 


There is a sample script (_showBoundingBox_faces.py) to verify if the face photo is ok or not. And it display the identified faces as below. 

```
Matthew$ python3 _showBoundingBox_faces.py --input_photo donald.jpg 
Detected faces for donald.jpg
The detected face is between 50 and 68 years old
{'Width': 0.33377254009246826, 'Height': 0.3336979150772095, 'Left': 0.31624940037727356, 'Top': 0.23058736324310303}
Left: 712
Top: 657
Face Width: 751
Face Height: 951
```

<img width="731" alt="donald_boundingbox" src="https://user-images.githubusercontent.com/49335272/66935750-238d2700-f06f-11e9-87d7-bd3fb948e60e.png">



## Usage
```
usage: Use face recongnition to management photos

Using AWS Rekcognition service to sort photo by invidial matched face (person)

optional arguments:
  -h, --help            show this help message and exit
  --input_folder INPUT_FOLDER
                        Folder path for photos to be process.
  --input_face_folder INPUT_FACE_FOLDER
                        Folder path face photo. Filename will be used as face
                        reference ID
  --output_folder OUTPUT_FOLDER
                        Output folder
  --threshold THRESHOLD
                        Threshold face similarity match
```
## Sample execution
I have included a detail logging during execution. And you will find even all AWS API response in the log file (facelook_photo_management.log)! 

```bash
(facelook_photo_management) Matthew$ python facelook_photo_management.py 
root        : INFO     Logger started!
root        : INFO     Attempting to delete collection faceCollection
botocore.credentials: INFO     Found credentials in shared credentials file: ~/.aws/credentials
root        : INFO     Operation returned Status Code: 200
root        : INFO     Creating face index collection [faceCollection]
root        : INFO     Collection ARN: aws:rekognition:us-east-1:275835853639:collection/faceCollection
root        : INFO     Status code: 200
root        : INFO     Collection created successfully!
root        : INFO     [./in_face//boris.jpg] Reading image file: ./in_face//boris.jpg
root        : INFO     [./in_face//donald.jpg] Reading image file: ./in_face//donald.jpg
root        : INFO     2 threads started for face index processing.
root        : INFO     [./in_face//boris.jpg] Add face completed. Processing time: 2.75 sec.
root        : INFO     [./in_face//boris.jpg]  Face signature: 0bbbb829-a8b0-43cc-a308-d027e7dadffd
root        : INFO     [./in_face//boris.jpg]  Face ID: boris
root        : INFO     [./in_face//boris.jpg]  Confidence: 99.99998474121094
root        : INFO     [./in_face//donald.jpg] Add face completed. Processing time: 3.56 sec.
root        : INFO     [./in_face//donald.jpg]  Face signature: ec242bb4-7641-4fac-8fef-438610ea1c1c
root        : INFO     [./in_face//donald.jpg]  Face ID: donald
root        : INFO     [./in_face//donald.jpg]  Confidence: 100.0
root        : INFO     All faces added to collect in 3.5661sec.
root        : INFO     [./in_photo//gathering_00003.jpg] Face detection completed. 2 faces detected in 3.2268sec.
root        : INFO     [./in_photo//gathering_00001.jpg] Face detection completed. 8 faces detected in 3.6266sec.
root        : INFO     [./in_photo//gathering_00002.jpg] Face detection completed. 12 faces detected in 4.1662sec.
root        : INFO     [./in_photo//gathering_00004.jpg] Face detection completed. 15 faces detected in 4.2519sec.
root        : INFO     [gathering_00003.jpg] Matched person [donald] with similarity 96.44%
root        : INFO     [gathering_00003.jpg] Matched person [boris] with similarity 99.84%
root        : INFO     [gathering_00003.jpg] Face matched completed in 5.0502sec.
root        : INFO     [gathering_00001.jpg] Matched person [donald] with similarity 99.22%
root        : INFO     [gathering_00002.jpg] Matched person [donald] with similarity 97.63%
root        : INFO     [gathering_00001.jpg] Face matched completed in 6.0155sec.
root        : INFO     [gathering_00004.jpg] Face matched completed in 6.449sec.
root        : INFO     [gathering_00002.jpg] Face matched completed in 6.7134sec.
root        : INFO     Process completed in 12.85 sec.

```
## Project folder 
```bash
.
.
|_____decribeCollection.py
|____facelook_photo_management.py
|____in_photo
| |____gathering_00004.jpg
| |____gathering_00002.jpg
| |____gathering_00003.jpg
| |____gathering_00001.jpg
|____in_face
| |____boris.jpg
| |____donald.jpg
|_____showBoundingBox_faces.py
|____out_photo
| |____donald
| | |____gathering_00002.jpg
| | |____gathering_00003.jpg
| | |____gathering_00001.jpg
| |____boris
| | |____gathering_00003.jpg
|____README.md
|____.gitignore
|____facelook_photo_management.log

```



