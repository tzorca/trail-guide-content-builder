import PIL
from PIL import Image, ImageFont, ImageDraw, ImageFile
import os
import glob
import json
import hashlib
import settings
import utils
import sys

if sys.version_info[0] != 3:
    print("This script requires Python version 3.0 or later")
    sys.exit(1)

ImageFile.LOAD_TRUNCATED_IMAGES = True

def resize_image_using_ratio(img, new_image_width):
	img_width = img.size[0]
	img_height = img.size[1]

	img_width_to_height_ratio = img_width / img_height

	new_image_height = new_image_width / img_width_to_height_ratio
	new_image_size = (int(new_image_width), int(new_image_height))

	return img.resize(size=new_image_size, resample=Image.ANTIALIAS)

def add_watermark_to_image(img, watermark_text, watermark_rgb, watermark_font_size):
	watermark_location = (watermark_font_size, img.height - watermark_font_size*2)
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("fonts/arial.ttf", watermark_font_size)
	draw.text(watermark_location, watermark_text, watermark_rgb, font=font)

	return img

def build_src_to_dest_image_path_map(src_filepaths, dest_dirpath, img_output_instances):
	rel_path_to_img_count = {}
	src_path_to_dest_path = {}

	for src_filepath in src_filepaths:
		# Get filename for src_filepath
		src_filename = os.path.basename(src_filepath)

		# Get the image number contained in the file name
		src_img_number = utils.get_numeric_part_from_string(src_filename)

		# Get parent directory for src_filepath
		src_file_dir_path = os.path.dirname(src_filepath)

		# Get path relative to source root/start path (the part that comes after the root path)
		start_rel_path = os.path.relpath(src_file_dir_path, settings.DirPaths.src_images)

		# Increment rel_path_to_img_count for that start_rel_path
		rel_path_to_img_count[start_rel_path] = rel_path_to_img_count.get(start_rel_path, 0) + 1

		# Build destination paths
		# Use hash of source directory to maintain a small correlation between source path and destination filename
		# This should allow deleting individual destination images and re-running the process quickly
		# But still want to maintain order of files, so will use actual src_img_number as next part
		start_rel_path_hash = hashlib.md5(start_rel_path.encode('utf-8')).hexdigest()[:10]
		dest_file_base_name = 'img-' + start_rel_path_hash + '-' + src_img_number 

		# Add mapping for each image destination
		src_path_to_dest_path[src_filepath] = {}
		current_mappings = src_path_to_dest_path[src_filepath]
		for img_output_name, img_output_props in img_output_instances.items():
			file_name = dest_file_base_name + img_output_props['filename_addition'] + ".jpg"
			current_mappings[img_output_name] = os.path.join(dest_dirpath, file_name)

	return src_path_to_dest_path

def process_and_save_images(src_to_dest_instances, src_image_path, img_settings):
	for src_filepath in src_to_dest_instances:
		dest_instances = src_to_dest_instances[src_filepath]

		for instance_name, dest_filepath in dest_instances.items():
			dest_dirpath = os.path.dirname(dest_filepath)
			src_dirpath = os.path.dirname(src_filepath)

			src_rel_dirpath = os.path.relpath(src_dirpath, src_image_path)
			dest_filename = os.path.basename(dest_filepath)

			# Create result directory if it doesn't exist
			if not os.path.exists(dest_dirpath):
				os.makedirs(dest_dirpath)

			# Skip if dest_filepath already exists
			if os.path.isfile(dest_filepath):
				continue

			print('Converting image from ' + src_rel_dirpath + '...')
			
			img = Image.open(src_filepath)

			# Process and save image instance (resize, add watermark, etc.)
			img_output_instance_settings = img_settings.output_instances[instance_name]
			output_image_width = img_output_instance_settings['image_width']
			watermark_font_size = img_output_instance_settings['watermark_font_size']

			converted_img = resize_image_using_ratio(img, output_image_width)

			converted_img = add_watermark_to_image(converted_img, img_settings.Watermark.text, 
				img_settings.Watermark.rgb, watermark_font_size)

			converted_img.save(dest_filepath, quality=80)


def remove_extra_files_if_confirmed(dir_path, expected_filepaths):
	expected_filepaths_set = set([os.path.abspath(filepath) for filepath in expected_filepaths])

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
		for extra_filepath in extra_filepaths:
			os.remove(extra_filepath)


print("Getting list of source image paths...")
src_filepaths = utils.get_full_filepaths_in_tree(settings.DirPaths.src_images)

print("Building path transformations from source image path to destination image paths...")
src_to_dest_instances_map = build_src_to_dest_image_path_map(src_filepaths, settings.DirPaths.dest_images, 
	settings.ImageProcessing.output_instances)

print("Processing and saving images to respective output paths...")
process_and_save_images(src_to_dest_instances_map, src_image_path=settings.DirPaths.src_images, 
	img_settings=settings.ImageProcessing)

dest_instances = list(src_to_dest_instances_map.values())
print(dest_instances[0])
dest_filepaths = []
for dest_instance in dest_instances:
	dest_filepaths.extend(dest_instance.values())
print(dest_filepaths[0])
remove_extra_files_if_confirmed(settings.DirPaths.dest_images, dest_filepaths)


print('Loading park content JSON...')
with open(settings.FilePaths.park_content_json) as json_file:
	park_content = json.load(json_file)
	print('Test: ' + str(park_content['places'][0]['links']))

