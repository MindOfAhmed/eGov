from PIL import Image
import io
import os
import boto3
import numpy as np
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# retrieve the key and endpoint from the os environment
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')

''' 
This function will validate the uploaded images like the passport image by detecting faces 
and checking if the image meets the requirements of a gov document. it will 
return a boolean indicating whether the image is valid or not, and a message.
'''
def validate_uploaded_photo(picture):
    try:
        # convert the uploaded image to a byte array
        image_stream = io.BytesIO(picture.read())

        # initialize the Rekognition client
        rekognition = boto3.client('rekognition', region_name='eu-west-2',
                                   aws_access_key_id=AWS_ACCESS_KEY,
                                   aws_secret_access_key=AWS_SECRET_KEY)

        # call rekognition to detect faces in the image
        response = rekognition.detect_faces(
            Image={'Bytes': image_stream.getvalue()},
            Attributes=['ALL']
        )
    except (NoCredentialsError, PartialCredentialsError) as e:
        return False, f"Error with AWS credentials: {str(e)}"
    except Exception as e:
        return False, f"Error detecting faces: {str(e)}"
    
    ''' check if faces are detected '''
    detected_faces = response.get('FaceDetails', [])
    if not detected_faces:
        return False, "No faces detected in the image."

    ''' check image has one face only '''
    if len(detected_faces) > 1:
        return False, "Multiple faces detected in the image."

    # extract face rectangle and quality attributes
    face_details = detected_faces[0]
    face_rect = face_details['BoundingBox']
    # the width and height are notmalized values (ratios) and not pixels
    face_width = face_rect['Width'] 
    face_height = face_rect['Height']

    # open the image using PIL
    img = Image.open(picture)
    img_width, img_height = img.size

    # convert Left, Top, Width & Height from normalized values to pixel coordinates
    left_pixels = face_rect['Left'] * img_width
    top_pixels = face_rect['Top'] * img_height
    face_width_pixels = face_width * img_width
    face_height_pixels = face_height * img_height

    # get the center of the face rectangle
    face_center_x = left_pixels + (face_width_pixels / 2)
    face_center_y = top_pixels + (face_height_pixels / 2)


    '''check if the face size is appropriate'''
    if face_width_pixels < 0.3 * img_width or face_width_pixels > 0.7 * img_width:
        return False, "Face size is not within the required range. It should be between 30% and 70% of the image width."

    '''check if the face is centered'''
    if abs(face_center_x - img_width / 2) > 0.1 * img_width or abs(face_center_y - img_height / 2) > 0.1 * img_height:
        return False, "Face must be centered in the image."

    '''check if the head is straight (head pose roll) '''
    head_pose = face_details['Pose']
    if head_pose['Roll'] > 10 or head_pose['Roll'] < -10:
        return False, "Head is tilted in the image."

    '''check if the background of the image is white'''
    # convert the image to numpy array for efficient processing 
    img_array = np.array(img) 
    # define the number of pixels to consider from each corner
    corner_margin = 50  

    # define corner areas (top-left, top-right, bottom-left, bottom-right)
    corners = [
        (range(corner_margin), range(corner_margin)),  # top-left
        (range(img_width - corner_margin, img_width), range(corner_margin)),  # top-right
        (range(corner_margin), range(img_height - corner_margin, img_height)),  # bottom-left
        (range(img_width - corner_margin, img_width), range(img_height - corner_margin, img_height))  # bottom-right
    ]

    # check each corner
    for x_range, y_range in corners:
        for x in x_range:
            for y in y_range:
                r, g, b = img_array[y, x][:3]  # get the pixel color, ignoring alpha channel
                # check if the pixel is not (almost) white
                if not (r > 180 and g > 180 and b > 180):
                    return False, "The background of the image is not white in the corners."

    '''check the image quality - resolution '''
    if img_width < 600 or img_height < 600:
        return False, "Image resolution is too low."

    return True, "Image is valid."