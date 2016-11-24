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

    return os.path.join(dirpath, filename_without_ext +
                        addition + filename_ext)


def resize_image_using_ratio(img, new_image_width, resample_mode):
    img_width = img.size[0]
    img_height = img.size[1]

    img_width_to_height_ratio = img_width / img_height

    new_image_height = new_image_width / img_width_to_height_ratio
    new_image_size = (int(new_image_width), int(new_image_height))

    return img.resize(size=new_image_size, resample=resample_mode)


# Sourced from http://stackoverflow.com/a/7716358
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)
