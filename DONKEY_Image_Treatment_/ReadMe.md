treatment.py 
To test
select images from recording 
every 100 images from DONKEY_Image/['recording_directory']
to DONKEY_Image_Treatment/DONKEY_image_Treatment/SAMPLE_10img

It could be replaced to select all images recorded

Resize, convert and crop image extracted from race
from directory DONKEY_Image/SAMPLE_10img to DONKEY_image_Treatment/SAMPLE_treated

encodDecod.py
Create images from existing ones by basic transformations from 'SAMPLE_treated' to 'output'
autoencoding Images from 'output' to 'converted'