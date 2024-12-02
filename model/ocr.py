import tensorflow as tf
import tensorflow.data as tfd
import pandas as pd
import numpy as np
import os
import json
import datetime
import keras
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model, load_model
from keras.src.layers import StringLookup
import sys, os, pathlib

prediction_model = None
num_to_char = None


def predict_text(BASE_DIR):
    global prediction_model

    def create_vocabulary():
        """
        This function creates a vocabulary of unique characters
        :return:
        """
        # Get the unique characters
        with open('unique_characters.json', 'r') as file:
            unique_characters = json.load(file)

        # Char to Num
        char_to_num = StringLookup(vocabulary=list(unique_characters), mask_token=None)
        num_to_char = StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)

        return char_to_num, num_to_char

    class CTCLayer(Layer):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

            # define the loss function
            self.loss_function = tf.keras.backend.ctc_batch_cost

        def call(self, y_true, y_hat):
            # Get the batch length
            batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")

            # get the input and label lengths
            input_len = tf.cast(tf.shape(y_hat)[1], dtype='int64') * tf.ones(shape=(batch_len, 1), dtype='int64')
            label_len = tf.cast(tf.shape(y_true)[1], dtype='int64') * tf.ones(shape=(batch_len, 1), dtype='int64')

            # calculate the loss
            loss = self.loss_function(y_true, y_hat, input_len, label_len)

            self.add_loss(loss)

            return y_hat

        def get_config(self):
            return super().get_config()

    def return_model_config(IMG_WIDTH, IMG_HEIGHT, char_to_num, load_image):

        input_images = Input(shape=(IMG_WIDTH, IMG_HEIGHT, 1), name="image")

        # Labels : These are added for the training purpose.
        input_labels = Input(shape=(None,), name="label")

        ### Convolutional layers
        # layer 1
        conv_1 = Conv2D(64, 3, strides=1, padding="same", kernel_initializer="he_normal", activation="relu",
                        name="conv_1")(
            input_images)
        # layer 2
        conv_2 = Conv2D(32, 3, strides=1, padding="same", kernel_initializer="he_normal", activation="relu",
                        name="conv_2")(
            conv_1)
        max_pool_1 = MaxPool2D(pool_size=(2, 2), strides=(2, 2))(conv_2)
        # layer 3
        conv_3 = Conv2D(64, 3, strides=1, padding='same', activation='relu', kernel_initializer='he_normal',
                        name="conv_3")(
            max_pool_1)
        conv_4 = Conv2D(32, 3, strides=1, padding='same', activation='relu', kernel_initializer='he_normal',
                        name="conv_4")(
            conv_3)
        max_pool_2 = MaxPool2D(pool_size=(2, 2), strides=(2, 2))(conv_4)

        ### Encoding
        reshape = Reshape(target_shape=((IMG_WIDTH // 4), (IMG_HEIGHT // 4) * 32), name="reshape_layer")(max_pool_2)
        dense_encoding = Dense(64, kernel_initializer="he_normal", activation="relu", name="enconding_dense")(reshape)
        dense_encoding_2 = Dense(64, kernel_initializer="he_normal", activation="relu", name="enconding_dense_2")(
            dense_encoding)
        dropout = Dropout(0.4)(dense_encoding_2)

        # Decoder
        lstm_1 = Bidirectional(LSTM(128, return_sequences=True, dropout=0.25), name="bidirectional_lstm_1")(dropout)
        lstm_2 = Bidirectional(LSTM(64, return_sequences=True, dropout=0.25), name="bidirectional_lstm_2")(lstm_1)

        # Final Output layer
        output = Dense(len(char_to_num.get_vocabulary()) + 1, activation="softmax", name="output_dense")(lstm_2)

        # Add the CTC loss
        ctc_loss_layer = CTCLayer()(input_labels, output)

        # Define the final model
        # model = Model(inputs=[input_images, input_labels], outputs=[ctc_loss_layer])
        prediction_model = Model(input_images, output)

        return prediction_model

    def make_prediction(model, image, decode_pred, load_image, num_to_char):
        """
        This function takes the model, image and decode_pred function as input and
        returns the prediction of the model.
        """
        # Load the image
        image = load_image(image)
        # Make prediction
        pred = model.predict(tf.expand_dims(image, axis=0))
        # Decode the prediction
        pred = decode_pred(pred, num_to_char)[0]

        return pred

    def load_image(image_path, IMG_WIDTH=200, IMG_HEIGHT=50):
        """
        This function gets the image path and
        reads the image using TensorFlow, Then the image will be decoded and
        will be converted to float data type. next resize and transpose will be applied to it.
        In the final step the image will be converted to a Numpy Array using tf.cast
        """
        # read the image
        image = tf.io.read_file(image_path)
        # decode the image
        decoded_image = tf.image.decode_jpeg(contents=image, channels=1)
        # convert image data type to float32
        convert_imgs = tf.image.convert_image_dtype(image=decoded_image, dtype=tf.float32)
        # resize and transpose
        resized_image = tf.image.resize(images=convert_imgs, size=(IMG_HEIGHT, IMG_WIDTH))
        image = tf.transpose(resized_image, perm=[1, 0, 2])

        # to numpy array (Tensor)
        image_array = tf.cast(image, dtype=tf.float32)

        return image_array

    def decoder_prediction(pred_label, num_to_char, MAX_LABEL_LENGTH=100):
        """
        This function has the job to decode the prediction that the model had.
        The model predicts each character and then this function makes it readable.
        """
        # Input length
        input_len = np.ones(shape=pred_label.shape[0]) * pred_label.shape[1]

        # CTC decode
        decode = tf.keras.backend.ctc_decode(pred_label, input_length=input_len, greedy=True)[0][0][:,
                 :MAX_LABEL_LENGTH]

        # Converting numerics back to their character values
        chars = num_to_char(decode)

        # Join all the characters
        texts = [tf.strings.reduce_join(inputs=char).numpy().decode('UTF-8') for char in chars]

        # Remove the unknown token

        filtered_texts = [text.replace('[UNK]', " ").strip() for text in texts]

        return filtered_texts

    os.chdir(os.path.join(BASE_DIR, "model"))

    if prediction_model is None:
        model = load_model('proc1_80.0_32_0.001' + ".keras", custom_objects={'CTCLayer': CTCLayer})
        model.summary()

        char_to_num, num_to_char = create_vocabulary()
        prediction_model = return_model_config(200, 50, char_to_num, load_image)
        prediction_model.set_weights(model.get_weights())

        prediction_model.summary()

    predicted_text = []

    img_path_ = os.path.join(os.getcwd(), 'temp')

    for img in os.listdir(img_path_):
        path = os.path.join(img_path_, img)
        if img.endswith('.jpg'):
            predicted_text.append(make_prediction(prediction_model, path, decoder_prediction, load_image, num_to_char))

    os.chdir(BASE_DIR)

    return predicted_text

