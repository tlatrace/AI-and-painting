import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path

from constants import PADDING_TYPE


def build_unet(
    n_classes: int, batch_size: int, encoder_kernel_size: int
) -> keras.Model:
    inputs = keras.Input(shape=(None, None, 3), batch_size=batch_size)

    encoder_block_1, skip_features1 = encoder_block(inputs, 32, encoder_kernel_size)
    encoder_block_2, skip_features2 = encoder_block(
        encoder_block_1, 64, encoder_kernel_size
    )
    encoder_block_3, skip_features3 = encoder_block(
        encoder_block_2, 128, encoder_kernel_size
    )
    encoder_block_4, skip_features4 = encoder_block(
        encoder_block_3, 256, encoder_kernel_size
    )

    conv_block1 = conv_block(encoder_block_4, 512, encoder_kernel_size)

    decoder_block1 = decoder_block(
        conv_block1, skip_features4, 256, encoder_kernel_size
    )
    decoder_block2 = decoder_block(
        decoder_block1, skip_features3, 128, encoder_kernel_size
    )
    decoder_block3 = decoder_block(
        decoder_block2, skip_features2, 64, encoder_kernel_size
    )
    decoder_block4 = decoder_block(
        decoder_block3, skip_features1, 32, encoder_kernel_size
    )

    outputs = layers.Conv2D(
        filters=n_classes, kernel_size=1, padding=PADDING_TYPE, activation="sigmoid"
    )(decoder_block4)

    model = keras.Model(inputs=inputs, outputs=outputs, name="U-Net")
    return model


def build_small_unet(
    n_classes: int, input_shape: int, batch_size: int, encoder_kernel_size: int
) -> keras.Model:
    """One encoder-decoder level less. Divides by a factor 4 the number of total paramaters of the model."""
    inputs = keras.Input(shape=(input_shape, input_shape, 3), batch_size=batch_size)

    encoder_block_1, skip_features1 = encoder_block(inputs, 32, encoder_kernel_size)
    encoder_block_2, skip_features2 = encoder_block(
        encoder_block_1, 64, encoder_kernel_size
    )
    encoder_block_3, skip_feature3 = encoder_block(
        encoder_block_2, 128, encoder_kernel_size
    )

    conv_block1 = conv_block(encoder_block_3, 256, encoder_kernel_size)

    decoder_block1 = decoder_block(conv_block1, skip_feature3, 128, encoder_kernel_size)
    decoder_block2 = decoder_block(
        decoder_block1, skip_features2, 64, encoder_kernel_size
    )
    decoder_block3 = decoder_block(
        decoder_block2, skip_features1, 32, encoder_kernel_size
    )

    outputs = layers.Conv2D(
        filters=n_classes + 1, kernel_size=1, padding=PADDING_TYPE, activation="sigmoid"
    )(decoder_block3)

    model = keras.Model(inputs=inputs, outputs=outputs, name="U-Net")
    return model


def build_small_unet_arbitrary_input(
    n_classes: int, batch_size: int, encoder_kernel_size: int
) -> keras.Model:
    """One encoder-decoder level less -> divides by a factor 4 the number of total paramaters of the model."""
    inputs = keras.Input(shape=(None, None, 3), batch_size=batch_size)

    encoder_block_1, skip_features1 = encoder_block(inputs, 32, encoder_kernel_size)
    encoder_block_2, skip_features2 = encoder_block(
        encoder_block_1, 64, encoder_kernel_size
    )
    encoder_block_3, skip_feature3 = encoder_block(
        encoder_block_2, 128, encoder_kernel_size
    )

    conv_block1 = conv_block(encoder_block_3, 256, encoder_kernel_size)

    decoder_block1 = decoder_block_test(
        conv_block1, skip_feature3, 128, encoder_kernel_size
    )
    decoder_block2 = decoder_block_test(
        decoder_block1, skip_features2, 64, encoder_kernel_size
    )
    decoder_block3 = decoder_block_test(
        decoder_block2, skip_features1, 32, encoder_kernel_size
    )

    outputs = layers.Conv2D(
        filters=n_classes + 1, kernel_size=1, padding=PADDING_TYPE, activation="sigmoid"
    )(decoder_block3)

    model = keras.Model(inputs=inputs, outputs=outputs, name="U-Net")
    return model


def conv_block(inputs: tf.Tensor, n_filters: int, kernel_size: int) -> tf.Tensor:
    x = layers.Conv2D(filters=n_filters, kernel_size=kernel_size, padding=PADDING_TYPE)(
        inputs
    )
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    x = layers.Conv2D(filters=n_filters, kernel_size=kernel_size, padding=PADDING_TYPE)(
        x
    )
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    return x


def encoder_block(
    inputs: tf.Tensor, n_filters: int, encoder_kernel_size: int
) -> (tf.Tensor, tf.Tensor):
    x = conv_block(inputs, n_filters, encoder_kernel_size)
    p = layers.MaxPooling2D(pool_size=2, strides=2)(x)
    return p, x


def decoder_block(
    inputs: tf.Tensor, skip_features: tf.Tensor, n_filters: int, kernel_size: int
) -> tf.Tensor:
    x = layers.Conv2DTranspose(
        filters=n_filters, kernel_size=2, strides=2, padding=PADDING_TYPE
    )(inputs)
    crop_shapes = get_crop_shape(x, skip_features)
    cropped_skip_features = layers.Cropping2D(
        cropping=crop_shapes, data_format="channels_last"
    )(skip_features)
    x = layers.concatenate([x, cropped_skip_features])
    x = conv_block(x, n_filters, kernel_size)
    return x


def decoder_block_test(
    inputs: tf.Tensor, skip_features: tf.Tensor, n_filters: int, kernel_size: int
) -> tf.Tensor:
    x = layers.Conv2DTranspose(
        filters=n_filters, kernel_size=2, strides=2, padding=PADDING_TYPE
    )(inputs)
    x = layers.concatenate([x, skip_features])
    x = conv_block(x, n_filters, kernel_size)
    return x


def get_crop_shape(reference_tensor: tf.Tensor, target_tensor: tf.Tensor) -> tuple:
    # height crop shape
    height_difference = target_tensor.get_shape()[1] - reference_tensor.get_shape()[1]
    assert height_difference >= 0
    if height_difference % 2 != 0:
        height_crop_shape = height_difference // 2, height_difference // 2 + 1
    else:
        height_crop_shape = height_difference // 2, height_difference // 2

    # width crop shape
    width_difference = target_tensor.get_shape()[2] - reference_tensor.get_shape()[2]
    assert width_difference >= 0
    if width_difference % 2 != 0:
        width_crop_shape = width_difference // 2, width_difference // 2 + 1
    else:
        width_crop_shape = width_difference // 2, width_difference // 2
    return height_crop_shape, width_crop_shape


def save_plotted_model(model: keras.Model, model_plot_path: Path) -> None:
    keras.utils.plot_model(
        model=model,
        to_file=model_plot_path,
        show_shapes=True,
    )
