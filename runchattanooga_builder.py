from PIL import Image, ImageFont, ImageDraw, ImageFile
import os
import glob
import json
import sys

from runchattanooga_builder import settings, utils
from runchattanooga_builder.models import ParkImage

if sys.version_info[0] != 3:
    print("This script requires Python version 3.0 or later")
    sys.exit(1)

ImageFile.LOAD_TRUNCATED_IMAGES = True


def add_watermark_to_image(
        img, watermark_text, watermark_rgb, watermark_font_size):
    watermark_location = (watermark_font_size,
                          img.height - watermark_font_size * 2)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/arial.ttf", watermark_font_size)
    draw.text(watermark_location, watermark_text, watermark_rgb, font=font)

    return img


def get_park_image_models(src_filepaths, src_dirpath, dest_dirpath, img_output_instances):
    park_images = []

    for src_filepath in src_filepaths:
        park_image = ParkImage(
            src_filepath=src_filepath,
            src_dirpath=src_dirpath,
            dest_dirpath=dest_dirpath,
            img_output_instances=img_output_instances
        )
        park_images.append(park_image)

    return park_images


def process_and_save_images(park_image_models, src_master_dirpath, img_settings):
    for park_image_model in park_image_models:
        dest_instances = park_image_model.dest_instances
        src_filepath = park_image_model.src_filepath

        for dest_instance in dest_instances:
            dest_filepath = dest_instance.filepath

            dest_dirpath = os.path.dirname(dest_filepath)

            # Create result directory if it doesn't exist
            if not os.path.exists(dest_dirpath):
                os.makedirs(dest_dirpath)

            # Skip if dest_filepath already exists
            if os.path.isfile(dest_filepath):
                continue

            rel_src_filepath = os.path.relpath(src_filepath, src_master_dirpath)
            print()
            print('Converting ' + rel_src_filepath + '...')

            img = Image.open(src_filepath)

            # Process and save image instance (resize, apply enhancements, add watermark, etc.)
            instance_settings = img_settings.output_instances[
                dest_instance.img_name]
            output_image_width = instance_settings.img_width
            watermark_font_size = instance_settings.watermark_font_size

            result_img = utils.resize_image_using_ratio(
                img, output_image_width, Image.BICUBIC)

            result_img = instance_settings.enhancement_algorithm_list.enhance(result_img)

            result_img = add_watermark_to_image(
                result_img, img_settings.Watermark.text,
                img_settings.Watermark.rgb, watermark_font_size)

            result_img.save(dest_filepath, quality=img_settings.jpeg_quality)


def remove_extra_files_if_confirmed(dir_path, expected_filepaths):
    expected_filepaths_set = set(
        [os.path.abspath(filepath) for filepath in expected_filepaths])

    extra_filepaths = []

    actual_filepaths = glob.glob(os.path.join(dir_path, "*.*"))
    for actual_filepath in actual_filepaths:
        abs_actual_filepath = os.path.abspath(actual_filepath)
        if abs_actual_filepath not in expected_filepaths_set:
            extra_filepaths.append(abs_actual_filepath)

    if len(extra_filepaths) == 0:
        return

    print('The following extra images exist at the destination: ')
    for extra_filepath in extra_filepaths:
        print(extra_filepath)

    user_input = input('If you wish to remove them, type ''delete'': ')
    print('You entered ' + user_input)

    if user_input == 'delete':
        print('Removing extra files...')
        for extra_filepathp in extra_filepaths:
            os.remove(extra_filepath)


print("Getting list of source image paths...")
src_filepaths = utils.get_full_filepaths_in_tree(settings.DirPaths.src_images)

print("Building path transformations from "
      "source image path to destination image paths...")

park_image_models = get_park_image_models(
    src_filepaths=src_filepaths,
    src_dirpath=settings.DirPaths.src_images,
    dest_dirpath=settings.DirPaths.dest_images,
    img_output_instances=settings.ImageProcessing.output_instances)


print("Processing and saving images to respective output paths...")
process_and_save_images(
    park_image_models,
    src_master_dirpath=settings.DirPaths.src_images,
    img_settings=settings.ImageProcessing)

# Get destination filepaths from park_image_models
dest_filepaths = []
for park_image_model in park_image_models:
    for dest_instance in park_image_model.dest_instances:
        dest_filepaths.append(dest_instance.filepath)

print('Test: ' + dest_filepaths[0])
remove_extra_files_if_confirmed(settings.DirPaths.dest_images, dest_filepaths)

print('Loading park content JSON...')
with open(settings.FilePaths.park_content_json) as json_file:
    park_content = json.load(json_file)
    print('Test: ' + str(park_content['places'][0]['links']))
