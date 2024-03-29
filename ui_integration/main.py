import tensorflow as tf
from pathlib import Path

from ui_integration.predictions_maker import make_predictions
from ui_integration.utils import (
    get_formatted_time,
    get_image_name_without_extension,
    turn_2d_tensor_to_3d_tensor,
)


# Constants
PATCH_SIZE = 256
PATCH_OVERLAP = 40
N_CLASSES = 9
BATCH_SIZE = 8
ENCODER_KERNEL_SIZE = 3
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
}  # Maps each labelling class to a number
# Values in a binary LabelBox mask
MASK_TRUE_VALUE = 255
MASK_FALSE_VALUE = 0


def main(
    image_path: Path,
    model_checkpoint_dir_path: Path,
    workspace_dir_path: Path,
) -> {str: Path}:
    """
    Generate and save binary predictions masks in the specified workspace folder.

    :param image_path: The image on which to make predictions on.
    :param model_checkpoint_dir_path: The path to the model checkpoint.
    :param workspace_dir_path: Folder where to save the binary predictions.
      It will create a subfolder named "<image_name>/predictions__<run_date>",
      with binary masks "<image_name>__<class_name>.png" in it.

    :returns A dictionnary with key <class_name> and value <class_mask_path>.

    Example : main(Path(".../image.jpg", Path(".../final_models/1_model_2022_01_06__17_43_17"), Path(".../my_workspace/")
    """
    # Make predictions
    predictions_tensor = make_predictions(
        target_image_path=image_path,
        checkpoint_dir_path=model_checkpoint_dir_path,
        patch_size=PATCH_SIZE,
        patch_overlap=PATCH_OVERLAP,
        n_classes=N_CLASSES,
        batch_size=BATCH_SIZE,
        encoder_kernel_size=ENCODER_KERNEL_SIZE,
    )

    # Create a subfolder for the predictions
    predictions_root_path = (
        workspace_dir_path
        / get_image_name_without_extension(image_path)
        / ("predictions__" + get_formatted_time())
    )
    predictions_root_path.mkdir(parents=True)

    # Create and save binary tensors
    class_masks_paths_dict = dict()
    for idx, class_number in enumerate(MAPPING_CLASS_NUMBER.values()):
        binary_tensor = tf.where(
            condition=tf.equal(predictions_tensor, class_number),
            x=MASK_TRUE_VALUE,
            y=MASK_FALSE_VALUE,
        )

        binary_tensor_3d = turn_2d_tensor_to_3d_tensor(tensor_2d=binary_tensor)
        mapping_number_class = {
            class_number: class_name
            for class_name, class_number in MAPPING_CLASS_NUMBER.items()
        }

        output_path = (
            predictions_root_path
            / f"{get_image_name_without_extension(image_path)}__{mapping_number_class[idx]}.png"
        )
        tf.keras.preprocessing.image.save_img(output_path, binary_tensor_3d)
        class_masks_paths_dict[mapping_number_class[idx]] = output_path
    print(
        f"\nBinary predictions plot successfully saved in folder : {predictions_root_path}"
    )

    return class_masks_paths_dict


# -----
# DEBUG

# class_masks_path_dict = main(
#     model_checkpoint_dir_path=Path(
#         r"C:\Users\thiba\OneDrive - CentraleSupelec\Mission_JCS_IA_peinture\files\final_models\1_model_2022_01_06__17_43_17"
#     ),
#     image_path=Path(
#         r"C:\Users\thiba\OneDrive - CentraleSupelec\Mission_JCS_IA_peinture\files\test_images\downscaled_images\max\downscaled_max_4.jpg"
#     ),
#     workspace_dir_path=Path(
#         r"C:\Users\thiba\OneDrive - CentraleSupelec\Mission_JCS_IA_peinture\files"
#     ),
# )
