from PIL import Image, ImageFont, ImageDraw
import PIL
from os import walk
import os
import settings
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_full_filepaths_in_tree(root_dir_path):
	filepaths = []
	for (dirpath, dirnames, filenames) in walk(root_dir_path):
		for filename in filenames:
			full_path = os.path.join(dirpath, filename)
			filepaths.append(full_path)
	return filepaths

def resize_image_using_ratio(img, new_image_width):
	img_width = img.size[0]
	img_height = img.size[1]

	img_width_to_height_ratio = img_width / img_height

	new_image_height = new_image_width / img_width_to_height_ratio
	new_image_size = (int(new_image_width), int(new_image_height))

	return img.resize(size=new_image_size, resample=Image.ANTIALIAS)

def add_watermark_to_image(img, watermark_text):
	# TODO
	return img

def build_src_to_dest_image_path_map(src_filepaths, dest_dirpath):
	rel_path_to_img_count = {}
	src_path_to_dest_path = {}

	for src_filepath in src_filepaths:

		# Get parent directory for src_filepath
		src_file_dir_path = os.path.dirname(src_filepath)

		# Get path relative to source root/start path (the part that comes after the root path)
		start_rel_path = os.path.relpath(src_file_dir_path, settings.content_source_path)

		# Increment rel_path_to_img_count for that start_rel_path
		rel_path_to_img_count[start_rel_path] = rel_path_to_img_count.get(start_rel_path, 0) + 1

		# Get image number from rel_path_to_img_count
		img_number  = rel_path_to_img_count[start_rel_path]

		# Get folder number from number of entries in rel_path_to_img_count
		folder_number = len(rel_path_to_img_count)

		# Build destination path
		dest_file_name = 'img%(img_number)s_%(folder_number)s.jpg' % locals()
		dest_filepath = os.path.join(dest_dirpath, start_rel_path, dest_file_name)

		# Map source path to dest_path
		src_path_to_dest_path[src_filepath] = dest_filepath

	return src_path_to_dest_path

print("Getting list of source file paths...")
src_filepaths = get_full_filepaths_in_tree(settings.content_source_path)

print("Building path transformations from source image path to destination image path...")
src_to_dest_path_map = build_src_to_dest_image_path_map(src_filepaths, settings.content_dest_path)


print("Resizing and saving images to respective output paths...")
for src_filepath in src_to_dest_path_map:
	dest_filepath = src_to_dest_path_map[src_filepath]
	dest_dirpath = os.path.dirname(dest_filepath)

	# Create result directory
	if not os.path.exists(dest_dirpath):
		os.makedirs(dest_dirpath)

	print('Loading image from ' + src_filepath + '...')
	
	img = Image.open(src_filepath)
	
	print('Resizing image...')

	result_img = resize_image_using_ratio(img, settings.output_image_width)

	print('Adding watermark...')

	result_img = add_watermark_to_image(img, settings.watermark_text)

	print('Saving result image to ' + dest_filepath + '...')

	result_img.save(dest_filepath, quality=80)


