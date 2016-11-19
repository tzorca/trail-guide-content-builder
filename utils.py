import re
import os


def get_full_filepaths_in_tree(root_dir_path):
	filepaths = []
	for (dirpath, dirnames, filenames) in os.walk(root_dir_path):
		for filename in filenames:
			full_path = os.path.join(dirpath, filename)
			filepaths.append(full_path)
	return filepaths

def get_numeric_part_from_string(text):
	found_numbers = re.findall(r'\d+', text)
	return (''.join(found_numbers))

def add_to_filename_without_extension(filepath, addition):
	filename_without_ext = os.path.splitext(filepath)[0]
	filename_ext = os.path.splitext(filepath)[1]

	dirpath = os.path.dirname(filepath)

	return os.path.join(dirpath, filename_without_ext + addition + filename_ext)
