import os
import hashlib
from runchattanooga_builder import utils


class ParkImage:

    def __init__(self, src_filepath, src_dirpath, dest_dirpath, img_output_instances):
        self.src_filepath = src_filepath

        # Get filename for src_filepath
        src_filename = os.path.basename(self.src_filepath)

        # Get the image number contained in the file name
        src_img_number = utils.get_numeric_part_from_string(src_filename)

        # Get parent directory for src_filepath
        src_file_dir_path = os.path.dirname(self.src_filepath)

        # Get path relative to source root/start path (the part that comes
        # after the root path)
        start_rel_path = os.path.relpath(src_file_dir_path, src_dirpath)

        # Build destination paths
        # Use hash of source directory to maintain a small correlation
        # between source path and destination filename.
        # This should allow deleting individual destination images
        # and re-running the process quickly.
        # But still want to maintain order of files, so will use
        # actual src_img_number as next part.
        start_rel_path_hash = hashlib.md5(
            start_rel_path.encode('utf-8')).hexdigest()[:10]
        dest_file_base_name = 'img-' + \
            start_rel_path_hash + '-' + src_img_number

        # Add dest instance for each image destination
        self.dest_instances = []

        for img_output_name, img_output_props in img_output_instances.items():
            dest_filename = dest_file_base_name + \
                img_output_props.filename_add + ".jpg"
            dest_filepath = os.path.join(dest_dirpath, dest_filename)
            self.dest_instances.append(
                ParkImageDestinationInstance(img_output_name, dest_filepath))


class ParkImageDestinationInstance:

    def __init__(self, img_name, dest_filepath):
        self.img_name = img_name
        self.filepath = dest_filepath
