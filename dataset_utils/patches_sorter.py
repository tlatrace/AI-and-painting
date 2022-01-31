import tensorflow as tf
import numpy as np
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from dataset_utils.file_utils import (
    save_list_to_csv,
    load_saved_dict,
    save_dict_to_csv,
    timeit,
)
from dataset_utils.files_stats import count_mask_value_occurences_percent_of_2d_tensor
from dataset_utils.image_utils import (
    get_file_name_with_extension,
    get_image_patches_paths_with_limit,
    get_image_patch_masks_paths, decode_image,
)
from dataset_utils.masks_encoder import stack_image_patch_masks


def get_patch_coverage(
    image_patch_masks_paths: [Path],
    mapping_class_number: {str: int},
) -> float:
    mask_tensor = stack_image_patch_masks(
        image_patch_masks_paths=image_patch_masks_paths,
        mapping_class_number=mapping_class_number,
    )
    count_mask_value_occurrence = count_mask_value_occurences_percent_of_2d_tensor(
        mask_tensor
    )
    if 0 not in count_mask_value_occurrence.keys():
        return 100
    else:
        return 100 - count_mask_value_occurrence[0]


# deprecated
def create_generator_patches_coverage(
    patches_dir_path: Path, mapping_class_number: {str: int}
) -> [Path]:
    for image_dir_path in patches_dir_path.iterdir():
        for patch_dir_path in image_dir_path.iterdir():
            for image_patch_path in (patch_dir_path / "image").iterdir():
                image_patch_masks_paths = get_image_patch_masks_paths(image_patch_path)
                yield image_patch_path, get_patch_coverage(
                    image_patch_masks_paths=image_patch_masks_paths,
                    mapping_class_number=mapping_class_number,
                )


# deprecated
def save_all_patches_coverage(
    patches_dir_path: Path, output_path: Path, mapping_class_number: {str: int}
) -> dict:
    patches_coverage_dict = dict()
    generator = create_generator_patches_coverage(
        patches_dir_path, mapping_class_number
    )
    while True:
        try:
            image_patch_path, patch_coverage = next(generator)
            patches_coverage_dict[image_patch_path] = patch_coverage
            logger.info(
                f"\nImage patch {image_patch_path} has a labels coverage of {patch_coverage}."
            )
        except StopIteration:
            break
    save_dict_to_csv(dict_to_export=patches_coverage_dict, output_path=output_path)
    return patches_coverage_dict


# deprecated
def is_patch_only_background(image_patch_masks_paths: [Path], patch_size: int) -> bool:
    """
    Test if the labels of a patch is background only, i.e. a patch_size x patch_size array of zeros.
    """
    background_array = tf.zeros((patch_size, patch_size), dtype=tf.int32).numpy()
    patch_mask_array = stack_image_patch_masks(
        image_patch_masks_paths=image_patch_masks_paths,
    ).numpy()
    try:
        np.testing.assert_array_equal(patch_mask_array, background_array)
        return True
    except AssertionError:
        return False


# deprecated
def get_only_background_patches_dir_paths(
    image_dir_path: Path, patch_size: int, all_masks_overlap_indices_path: Path
) -> [Path]:
    only_background_patches_dir_paths = list()
    for image_patch_dir_path in image_dir_path.iterdir():
        for image_patch_path in (image_patch_dir_path / "image").iterdir():
            if is_patch_only_background(
                image_patch_path, patch_size, all_masks_overlap_indices_path
            ):
                only_background_patches_dir_paths.append(image_patch_dir_path)
    return only_background_patches_dir_paths


# deprecated
def create_generator_all_only_background_patches(
    patches_dir_path: Path, patch_size: int, all_masks_overlap_indices_path: Path
) -> [Path]:
    for image_dir_path in patches_dir_path.iterdir():
        only_background_patches_dir_paths = get_only_background_patches_dir_paths(
            image_dir_path, patch_size, all_masks_overlap_indices_path
        )
        yield image_dir_path, only_background_patches_dir_paths


# deprecated
def save_all_only_background_patches_dir_paths(
    patches_dir_path: Path,
    patch_size: int,
    output_path: Path,
    all_masks_overlap_indices_path: Path,
) -> [Path]:
    all_only_background_patches_dir_paths = list()
    generator = create_generator_all_only_background_patches(
        patches_dir_path, patch_size, all_masks_overlap_indices_path
    )
    while True:
        try:
            image_dir_path, only_background_patches_dir_paths = next(generator)
            all_only_background_patches_dir_paths += only_background_patches_dir_paths
            logger.info(
                f"\nImage {get_file_name_with_extension(image_dir_path)} has {len(only_background_patches_dir_paths)} patches with background only."
            )
        except StopIteration:
            break
    save_list_to_csv(
        list_to_export=all_only_background_patches_dir_paths,
        output_path=output_path,
    )
    return all_only_background_patches_dir_paths


def get_all_only_background_patches_dir_paths(
    saved_only_background_patches_dir_paths_path: Path,
) -> [Path]:
    all_only_background_patches_dir_paths = list()
    only_background_patches_dir_paths_list = load_saved_dict(
        saved_only_background_patches_dir_paths_path
    )
    for only_background_patches_dir_path in only_background_patches_dir_paths_list:
        all_only_background_patches_dir_paths.append(only_background_patches_dir_path)
    return all_only_background_patches_dir_paths
