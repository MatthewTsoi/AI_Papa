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

#### A note of virtual environment, 
It is recommanded to run piece of code under separate python virtual environment. Learn more about this [documentation] (https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) 





