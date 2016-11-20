from PIL import Image, ImageDraw, ImageFile
import os
import utils
import settings


OUTPUT_IMAGE_WIDTH = 1280


resample_modes = [
    {
        'name': 'Nearest',
        'mode': Image.NEAREST
    },
    {
        'name': 'BILINEAR',
        'mode': Image.BILINEAR
    },
    {
        'name': 'BICUBIC',
        'mode': Image.BICUBIC
    },
    {
        'name': 'LANCZOS',
        'mode': Image.LANCZOS
    }
]


def test_resize_resample_modes(img, base_image_name):
    for resample_mode in resample_modes:
        mode = resample_mode['mode']
        mode_name = resample_mode['name']

        converted_img = utils.resize_image_using_ratio(
            img, OUTPUT_IMAGE_WIDTH, mode)

        output_filename = base_image_name + '-' + mode_name + '.jpg'
        output_path = os.path.join(
            settings.DirPaths.test_dest_images, output_filename)

        converted_img.save(output_path, settings.ImageProcessing.jpeg_quality)


for filepath in settings.FilePaths.test_images:
    img = Image.open(filepath)

    base_image_name = os.path.basename(filepath)

    test_resize_resample_modes(img, base_image_name)
