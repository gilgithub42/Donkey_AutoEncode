# -*- coding: utf-8 -*-
"""07_autoencoder.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1n68Pzk8rvDLW5qOBdjzHN5_zteVLeofp
"""

#default_exp autoencoder

#hide
# from nbdev.showdoc import *
# all_flag

"""# Autoencoders

> Summary: Encoder, Decoder, Latent vector, Variational Autoencoder, VAE, Latent Space

## What are Autoencoders?

Autoencoders are neural networks that learn to efficiently compress and encode data then learn to reconstruct the data back from the reduced encoded representation to a representation that is as close to the original input as possible. Therefore, autoencoders reduce the dimentsionality of the input data i.e. reducing the number of features that describe input data.

Since autoencoders encode the input data and reconstruct the original input from encoded representation, they learn the **identity** function in an unspervised manner.

![](images/autoen_architecture.png)
*Autoencoder architecture. [[Image Source](https://lilianweng.github.io/lil-log/2018/08/12/from-autoencoder-to-beta-vae.html)]*

An autoencoder consists of two primary components:
1. Encoder: Learns to compress (reduce) the input data into an encoded representation.
2. Decoder: Learns to reconstruct the  original data from the encoded representation to be as close to the original input as possible.
3. Bottleneck: The layer that contains the compressed representation of the input data.
4. Reconstruction loss: The method to that measures how well the decoder is performing, i.e. measures the difference between the encoded and decoded vectors.

The model involves encoded function $g$ parameterized by $\phi$ and a decoder function $f$ parameterized by $\theta$. The bottleneck layer is $\mathbf{z}=g_{\phi}(\mathbf{x})$, and the reconstructed input $\mathbf{x'}=f_{\theta}(g_{\phi}(\mathbf{x}))$.

For measuring the reconstruction loss, we can use the cross entropy (when activation function is sigmoid) or basic Mean Squared Error (MSE):

$$L_{AE}(\theta,\phi)=\frac{1}{n}\sum_{i=1}^n (\mathbf{x}^{(i)}-f_{\theta}(g_{\phi}(\mathbf{x}^{(i)})))^2$$

## Autoencoder Applications

Autoencoders have several different applications including:

- Dimensionality Reductiions

- Image Compression

- Image Denoising

- Image colorization

### Image Denoising

Image denoising is the process of removing noise from the image. We can train an autoencoder to remove noise from the images. 

![](images/autoen_denoising_architecture.png)
*Denoising autoencoder architecture. [[Image Source](https://lilianweng.github.io/lil-log/2018/08/12/from-autoencoder-to-beta-vae.html)]*

We start by adding some noise (usually Gaussian noise) to the input images and then train the autoencoder to map noisy digits images to clean digits images. In order to see a complete example of image denoising, see [here](https://blog.keras.io/building-autoencoders-in-keras.html).

## Autoencoder Implementation
"""

# pip install augmentor

#export
import Augmentor
import os
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

#export
def get_pixel(image, i, j):
    """ Returns a pixel at coordinate (`i`, `j`). """
    return image.getpixel((i,j))

def change_image_background(orig_dir_path, converted_path):
    """ Changes the image background from white to black and foreground from black to white,
     for all the images at folder `orig_dir_path` and place them into folder `converted_path`."""
    files = os.listdir(dir_path)
    num_files = len(files)
    data = []
    counter = 1
    for f in tqdm(files, total=num_files):
        img = Image.open(os.path.join(dir_path,f))
        out_img = Image.new('RGB',img.size,color=1)
        width, height = img.size
        for w in range(width):
            for h in range(height):
                r, g, b = get_pixel(img, w,h)
                if r > 128 or g > 128 or b > 128:
                    r = g = b = 0
                else:
                    r = g = b = 255
                out_img.putpixel((w,h),(r,g,b))
        file_name = os.path.join(converted_path, str(counter) + '.png')
        out_img.save(file_name)
        counter += 1
    return data


def create_augmentor_pipeline(dir_path):
    """ Creates a pipeline for generating extra images from images at folder `dir_path`."""
    p = Augmentor.Pipeline(dir_path)
    p.resize(probability=1,width=64,height=64)
    p.rotate90(probability=0.1)
    p.rotate(probability=0.2, max_left_rotation=5, max_right_rotation=10)
    p.skew_left_right(probability=0.1)
    p.greyscale(probability=1)
    return p


def load_data(dir_path):
    """ Loads all the images from directory `dir_path`, converts them to matrices and return a list."""
    files = os.listdir(dir_path)
    num_files = len(files)
    data = []
    for f in tqdm(files, total=num_files):
        img = Image.open(os.path.join(dir_path,f))
        img_array = np.array(img)
        data.append(img_array)
    return data

"""> Note: The dataset contains several Farsi (Persian) characters written in `Moallah` font. It can replaced with any dataset of your interest."""

# Change the background to black and foreground to white
# Please note that you have to execute this once. If your dataset is already correctly
# formatted, then skip this step.
# path_data = r"./ml_tutorial-master/data/"
path_data = r"./"
# path_data=path_data.encode('unicode_escape').decode()
dir_path = path_data + 'SAMPLE_treated'
# dir_path = os.path.join(path_data,'moalla-dataset')
converted_path = os.path.join(path_data,'converted')
converted_path = path_data + 'converted'
print(converted_path)
# change_image_background(dir_path, converted_path)

p = create_augmentor_pipeline(converted_path)

# Generate  10000 images of (64 x 64) according to the pipeline and put them in `data/converted/output` folder
num_samples = 10000
p.sample(num_samples)

# Load all the images and return a list having array representation of each image
dir_path = os.path.join(converted_path,'output')
data = load_data(dir_path)

# Split the dataset into 80% train and 20% test sets.
train_data,test_data,_,_ = train_test_split(data,data,test_size=0.2)
train_data = np.array(train_data)
test_data = np.array(test_data)

# select a random image and display it
sample = 1190
img = Image.fromarray(train_data[sample])
plt.imshow(img)

# Normalizing train and test data
normalized_train_data = train_data.astype('float32')/255.0
normalized_test_data = test_data.astype('float32')/255.0

# Reshaping train and test sets, i.e. changing from (64, 64) to (64, 64, 1)
normalized_train_data = np.expand_dims(normalized_train_data,axis=-1)
normalized_test_data = np.expand_dims(normalized_test_data,axis=-1)
print('Normalization and reshaping is done.')
print('Input shape = {}'.format(normalized_train_data.shape[1:]))

"""### Defining the Encoder

"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Conv2DTranspose, Flatten
from tensorflow.keras.layers import Reshape, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import TensorBoard

image_width  = 64
image_height = 64
n_epochs     = 15
batch_size   = 128

input_img = Input(shape=(image_width, image_height, 1))  

# You can experiment with the encoder layers, i.e. add or change them
x = Conv2D(32, (3, 3), activation='relu', strides=2, padding='same')(input_img)
x = Conv2D(64, (3, 3), activation='relu', strides=2, padding='same')(x)

# We need this shape later in the decoder, so we save it into a variable.
encoded_shape = K.int_shape(x)

x = Flatten()(x)
encoded = Dense(128)(x)

# Builing the encoder
encoder = Model(input_img,encoded,name='encoder')

# at this point the representation is 128-dimensional
encoder.summary()

"""### Defining the Decoder"""

# Input shape for decoder
encoded_input = Input(shape=(128,))
x = Dense(np.prod(encoded_shape[1:]))(encoded_input)
x = Reshape((encoded_shape[1], encoded_shape[2], encoded_shape[3]))(x)
x = Conv2DTranspose(64,(3, 3), activation='relu',strides=2, padding='same')(x)
x = Conv2DTranspose(32,(3, 3), activation='relu', strides=2, padding='same')(x)
x = Conv2DTranspose(1,(3, 3), activation='sigmoid', padding='same')(x)

decoder = Model(encoded_input,x,name='decoder')
decoder.summary()

"""### Defining the Autoencoder"""

autoencoder = Model(input_img, decoder(encoder(input_img)),name="autoencoder")
autoencoder.summary()

# Compile and train the model. Log and visualize using tensorboard
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

h = autoencoder.fit(normalized_train_data, normalized_train_data,
                epochs=n_epochs,
                batch_size=batch_size,
                shuffle=True,
                validation_data=(normalized_test_data, normalized_test_data),
                callbacks=[TensorBoard(log_dir='/tmp/autoencoder')])

#hide
# Plot the training history using altair

import altair as alt
import pandas as pd

train_source = pd.DataFrame({'x':np.arange(0,n_epochs), 'y':h.history['loss'], 'orig_label': 15 * ['train_loss']})
val_source = pd.DataFrame({'x':np.arange(0,n_epochs), 'y':h.history['val_loss'], 'val_label': 15 * ['val_loss']})
legends = ['train loss', 'val loss']

train_chart = alt.Chart(train_source).mark_line().encode(
    alt.X('x', title='Epochs'),
    alt.Y('y', title='Loss/Accuracy'),
    color=alt.Color('orig_label:O', legend=alt.Legend(title=None))
)
val_chart = alt.Chart(val_source).mark_line().encode(
    alt.X('x', title='Epochs'),
    alt.Y('y', title='Loss/Accuracy'),
    color=alt.Color('val_label:O', scale=alt.Scale(range=['red']), legend=alt.Legend(title=None))

    
)
# alt.layer(train_chart, val_chart).resolve_scale(color='independent')

# plot the train and validation losses
N = np.arange(0, n_epochs)
plt.figure()
plt.plot(N, h.history['loss'], label='train_loss')
plt.plot(N, h.history['val_loss'], label='val_loss')
plt.title('Training Loss and Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Loss/Accuracy')
plt.legend(loc='upper right')

"""TensorBoard also provides plenty of useful information including measurements and visualizations during and after training. The snippet below shows the training loss in TensorBoard:

![](images/autoen_tensorboard.png)

"""

# Make predictions on the test set
decoded_imgs = autoencoder.predict(normalized_test_data)

def visualize(model, X_test, n_samples): 
    """ Visualizes the original images and the reconstructed ones for `n_samples` examples 
    on the test set `X_test`."""
      
    # Reconstructing the encoded images 
    reconstructed_images = model.predict(X_test) 
      
    plt.figure(figsize =(20, 4)) 
    for i in range(1, n_samples): 
          
        # Generating a random to get random results 
        rand_num = np.random.randint(0, 2000) 
      
        # To display the original image 
        ax = plt.subplot(2, 10, i) 
        plt.imshow(X_test[rand_num].reshape(image_width, image_width)) 
        plt.gray() 
        ax.get_xaxis().set_visible(False) 
        ax.get_yaxis().set_visible(False) 
  
        # To display the reconstructed image 
        ax = plt.subplot(2, 10, i + 10) 
        plt.imshow(reconstructed_images[rand_num].reshape(image_width, image_width)) 
        plt.gray() 
        ax.get_xaxis().set_visible(False) 
        ax.get_yaxis().set_visible(False) 
          
    # Displaying the plot 
    plt.show()

# Plots `n_samples` images. Top row is the original images and the lower row is the reconstructed ones.
n_samples = 10
visualize(autoencoder,normalized_test_data, n_samples)

"""## Variational Autoencoders (VAE)

### Limitations of Autoencoders for Content Generation

After we train an autoencoder, we might think whether we can use the model to create new content. Particularly, we may ask *can we take a point randomly from that latent space and decode it to get a new content?*

The answer is "yes", but but quality and relevance of generated data depend on the regularity of the latent space. The latent space regularity depends on the *distribution of the initial data*, the *dimension of the latent space* and the *architecture of the encoder*. It is quite difficult to ensure, a priori, that the encoder will organize the latent space in a smart way compatible with the generative process I mentioned. No regularization means overfitting, which leads to meaningless content once decoded for some point. For more information, see [this nice blog](https://towardsdatascience.com/understanding-variational-autoencoders-vaes-f70510919f73). 

How can we make sure the latent space is regularized enough? We can explicitly introduce regularization during the training process. Therefore, we introduce **Variational Autoencoders**.

### Variational Autoencoder (VAE)

It's an autoencoder whose training is regularized to avoid overfitting and ensure that the latent space has good properties that enable generative process. The idea is instead of mapping the input into a fixed vector, we want to map it into a distribution. In other words, the encoder outputs two vectors of size $n$, a vector of means $\mathbf{\mu}$, and another vector of standard variations $\mathbf{\sigma}$.

![](images/autoen_vae1.png)
*Difference between autoencoder (deterministic) and variational autoencoder (probabilistic). [[Image Source](https://towardsdatascience.com/understanding-variational-autoencoders-vaes-f70510919f73)]*

The encoded distributions are often normal so that the encoder can be trained to return the mean and the covariance matrix that describe these Gaussians. We force the encoder to return the distributions that are close to a standard normal distribution.

![](images/autoen_vae-gaussian.png)
*Variational autoencoder model with the multivariate Gaussian assumption.[[]Image Source](https://lilianweng.github.io/lil-log/2018/08/12/from-autoencoder-to-beta-vae.html)*

### VAE Loss Function

The loss function that we need to minimize for VAE consists of two components: (a) reconstruction term, which is similar to the loss function of regular autoencoders; and (b) regularization term, which regularizes the latent space by making the distributions returned by the encoder close to a standard normal distribution. We use the Kullback-Leibler divergence to quantify the difference between the returned distribution and a standard Gaussian. KL divergence $D_{KL}(X\|Y)$ measures how much information is lost if the distribution $Y$ is used to represent $X$. I am not willing to go deeply into the mathmatical details of VAE, however, all the math details have been nicely described [here](https://lilianweng.github.io/lil-log/2018/08/12/from-autoencoder-to-beta-vae.html) and [here](https://towardsdatascience.com/understanding-variational-autoencoders-vaes-f70510919f73) among other places.

$$L_{VAE}=\|\mathbf{x}-\mathbf{x'}\|^2 - D_{KL}[N(\mu_{\mathbf{x}},\sigma_{\mathbf{x}})\|N(0,1)]$$

$$D_{KL}[N(\mu_{\mathbf{x}},\sigma_{\mathbf{x}})\|N(0,1)]=\frac{1}{2}\sum_{k} (\sigma_{\mathbf{x}} + \mu_{\mathbf{x}}^2 -1 - \log(\sigma_{\mathbf{x}}))$$

where $k$ is the dimension of the Gaussian. In practice, however, it’s better to model $\sigma_{\mathbf{x}}$ rather than $\log(\sigma_{\mathbf{x}})$ as it is more numerically stable to take exponent compared to computing log. Hence, our final KL divergence term is:

$$D_{KL}[N(\mu_{\mathbf{x}},\sigma_{\mathbf{x}})\|N(0,1)]=\frac{1}{2}\sum_{k} (\exp(\sigma_{\mathbf{x}}) + \mu_{\mathbf{x}}^2 -1 - \sigma_{\mathbf{x}})$$

What is important is that the VAE loss function involves generating samples from $\mathbf{z}\sim N(\mathbf{\mu},\mathbf{\sigma})$. Since Sampling is a stochastic process, we cannot backpropagate the gradient while training the model. To make it trainable, a simple trick, called reparametrization trick, is used to make the gradient descent possible despite the random sampling that occurs halfway of the architecture. In this trick, random variable $\mathbf{z}$ is expressed as a deterministic variable $\mathbf{z}=\mathcal{T}_{\phi}(\mathbf{x},\mathbf{\epsilon})$, where $\mathbf{\epsilon}$ is an auxiliary independent random variable, and the transformation function $\mathcal{T}_{\phi}$ parameterized by ϕ converts $\mathbf{\epsilon}$ to $\mathbf{z}$.

If $\mathbf{z}$ is a random variable following a Gaussian distribution with mean $\mathbf{\mu}$ and with covariance $\mathbf{\sigma}$ then it can be expressed as:

$$\mathbf{z}=\mathbf{\mu}+\mathbf{\sigma}\odot \mathbf{\epsilon}$$

where $\odot$ is the element-wise multiplication.

![](images/autoen_vae_backprop.png)
*Illustration of the reparametrisation trick. [[Image Source](https://towardsdatascience.com/understanding-variational-autoencoders-vaes-f70510919f73)]*

### VAE Implementation
"""