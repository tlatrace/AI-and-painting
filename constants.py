import numpy as np
from tensorflow.keras.optimizers import Adam
from pathlib import Path
from tensorflow import keras
from scipy.signal import gaussian

# local_machine = False
local_machine = True

# Paths variables
if local_machine:
    DATA_DIR_ROOT = Path(
        r"C:\Users\thiba\OneDrive - CentraleSupelec\Mission_JCS_IA_peinture\files"
    )
    MASKS_DIR_PATH = DATA_DIR_ROOT / "labels_masks/all"
    REPORT_DIR_PATH = DATA_DIR_ROOT / r"reports/report_2022_01_06__17_43_17"
    CHECKPOINT_DIR_PATH = (
        DATA_DIR_ROOT / r"reports/report_2022_01_06__17_43_17/2_model_report"
    )
    IMAGES_DIR_PATH = Path(
        r"C:\Users\thiba\OneDrive - CentraleSupelec\Mission_JCS_IA_peinture\images\sorted_images\kept\all"
    )
    TEST_IMAGES_DIR_PATH = DATA_DIR_ROOT / "test_images"
    DOWNSCALED_TEST_IMAGES_DIR_PATH = TEST_IMAGES_DIR_PATH / "downscaled_images" / "max"
    TEST_IMAGE_PATH = IMAGES_DIR_PATH / "_DSC0246.JPG"
    N_EPOCHS = 2
    N_PATCHES_LIMIT = 50
else:  # aws instance
    DATA_DIR_ROOT = Path(r"/home/data")
    MASKS_DIR_PATH = DATA_DIR_ROOT / "labels_masks"
    REPORT_DIR_PATH = DATA_DIR_ROOT / r"reports/report_2022_01_06__17_43_17"
    CHECKPOINT_DIR_PATH = (
        DATA_DIR_ROOT / r"reports/report_2022_01_06__17_43_17/2_model_report"
    )
    IMAGES_DIR_PATH = DATA_DIR_ROOT / "images"
    TEST_IMAGES_DIR_PATH = DATA_DIR_ROOT / "test_images"
    DOWNSCALED_TEST_IMAGES_DIR_PATH = TEST_IMAGES_DIR_PATH / "downscaled_images" / "max"
    TEST_IMAGE_PATH = IMAGES_DIR_PATH / "_DSC0246/_DSC0246.jpg"
    N_EPOCHS = 10
    N_PATCHES_LIMIT = None

TEST_IMAGES_NAMES = [
    "3.jpg",
    "4.jpg",
    "DSC_0097.jpg",
    "IMG_3083.jpg",
    "IMG_4698_2.jpg",
    "IMG_4724_2.jpg",
    "IMG_4831.jpg",
    "IMG_4939.jpg",
    "P1000724.jpg",
    "_DSC0036.jpg",
    "_DSC0064.jpg",
    "_DSC0103.jpg",
    "_DSC0177.jpg",
    "_DSC0201.jpg",
    "_DSC0231.jpg",
    "_DSC0235.jpg",
    "_DSC0241.jpg",
    "_DSC0245.jpg",
    "_DSC0257.jpg",
    "_DSC0300.jpg",
]
TEST_IMAGES_PATHS_LIST = [
    TEST_IMAGES_DIR_PATH / image_name for image_name in TEST_IMAGES_NAMES
]
DOWNSCALED_TEST_IMAGES_PATHS_LIST = [
    DOWNSCALED_TEST_IMAGES_DIR_PATH / ("downscaled_max_" + image_name)
    for image_name in TEST_IMAGES_NAMES
]
PATCHES_DIR_PATH = DATA_DIR_ROOT / "patches/256x256"
PREDICTIONS_DIR_PATH = DATA_DIR_ROOT / "predictions"
REPORTS_ROOT_DIR_PATH = DATA_DIR_ROOT / "reports"
IMAGE_PATCH_PATH = DATA_DIR_ROOT / "patches/256x256/1/1/image/1_patch_1.jpg"
IMAGE_PATH = DATA_DIR_ROOT / "images/_DSC0246/_DSC0246.jpg"
MASK_PATH = (
    DATA_DIR_ROOT
    / "labels_masks/all/1/feuilles-vertes/mask_1_feuilles-vertes__090f44ab03ee43d7aaabe92aa58b06c1.png"
)

# Palette & mapping related variables
MAPPING_CLASS_NUMBER = {
    "background": 0,
    "poils-cheveux": 1,
    "vetements": 2,
    "peau": 3,
    "bois-tronc": 4,
    "ciel": 5,
    "feuilles-vertes": 6,
    "herbe": 7,
    "eau": 8,
    "roche": 9,
}  # maps each labelling class to a number

PALETTE_HEXA = {
    0: "#DCDCDC",  # gainsboro
    1: "#8B6914",  # goldenrod4
    2: "#BF3EFF",  # darkorchid1
    3: "#FF7D40",  # flesh
    4: "#E3CF57",  # banana
    5: "#6495ED",  # cornerflowblue
    6: "#458B00",  # chartreuse4
    7: "#7FFF00",  # chartreuse1
    8: "#00FFFF",  # aqua
    9: "#FF0000",  # red
}


def turn_hexadecimal_color_into_nomalized_rgb_list(hexadecimal_color: str) -> [int]:
    hexadecimal_color = hexadecimal_color.lstrip("#")
    return tuple(int(hexadecimal_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def turn_hexadecimal_color_into_rgb_list(hexadecimal_color: str) -> [int]:
    hexadecimal_color = hexadecimal_color.lstrip("#")
    return tuple(int(hexadecimal_color[i : i + 2], 16) for i in (0, 2, 4))


PALETTE_RGB_NORMALIZED = {
    key: turn_hexadecimal_color_into_nomalized_rgb_list(value)
    for key, value in PALETTE_HEXA.items()
}
PALETTE_RGB = {
    key: turn_hexadecimal_color_into_rgb_list(value)
    for key, value in PALETTE_HEXA.items()
}

# LabelBox related variables
JSON_PATH = Path(
    "C:/Users/thiba/OneDrive - CentraleSupelec/Mission_JCS_IA_peinture/labelbox_export_json/export-2021-07-26T14_40_28.059Z.json"
)
# Values in a binary LabelBox mask
MASK_TRUE_VALUE = 255
MASK_FALSE_VALUE = 0

# Model parameters & hyperparameters

PATCH_SIZE = 256
BATCH_SIZE = 8  # 32 is a frequently used value
N_CLASSES = 9
VALIDATION_PROPORTION = 0.2
TEST_PROPORTION = 0.1
PATCH_OVERLAP = 40  # 20 not enough, 40 great
PATCH_COVERAGE_PERCENT_LIMIT = 75
ENCODER_KERNEL_SIZE = 3
LINEARIZER_KERNEL_SIZE = 3
N_CPUS = 4
TARGET_HEIGHT = 2176
TARGET_WIDTH = 3264
PADDING_TYPE = "same"
LEARNING_RATE = 1e-4
OPTIMIZER = Adam(
    lr=LEARNING_RATE
)  # try to put tf.Variable instead of float to shut the warnings
LOSS_FUNCTION = keras.losses.categorical_crossentropy
METRICS = [keras.metrics.categorical_accuracy, keras.metrics.MeanIoU(N_CLASSES)]
DOWNSCALE_FACTORS = (6, 6, 1)
DATA_AUGMENTATION = False
IMAGE_DATA_GENERATOR_CONFIG_DICT = dict(
    brightness_range=[0.8, 1.2],
    horizontal_flip=True,
    zoom_range=[1.0, 1.2],
    # rotation_range=5,
    # channel_shift_range=50,
    # samplewise_std_normalization=True,
)
EARLY_STOPPING_LOSS_MIN_DELTA = 0.02
EARLY_STOPPING_ACCURACY_MIN_DELTA = 0.01
CORRELATE_PREDICTIONS_BOOL = False


def generate_gaussian_kernel(sigma, neigh):
    """
    Gaussian kernel generator.

    Inputs:
        sigma:     Std of Gaussian
        neigh:     Size of window
    """

    kernel_1d = gaussian(M=neigh, std=sigma)
    kernel = np.outer(kernel_1d, kernel_1d)

    return kernel / np.sum(kernel)


# CORRELATION_FILTER = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
CORRELATION_FILTER = 10 * generate_gaussian_kernel(sigma=1, neigh=5)

# Physical parameters (in mm)
MAX_WIDTH_PIXELS = 800
MAX_HEIGHT_PIXELS = 700
MIN_WIDTH_PIXELS = 160
MIN_HEIGHT_PIXELS = 140
