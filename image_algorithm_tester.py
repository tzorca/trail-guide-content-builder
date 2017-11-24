from PIL import Image
import os
from ctg_builder import utils, settings
from ctg_builder.image_algorithm import FactorDeterminer, EnhancementType, EnhancementAlgorithm, EnhancementAlgorithmList

OUTPUT_IMAGE_WIDTH = 1280
OUTPUT_IMAGE_HEIGHT = 960

#
# Set up algorithms
brightness_min_100 = EnhancementAlgorithm(
    enhancement_type=EnhancementType.Brightness,
    factor_determiner=FactorDeterminer(min_val=100, avg_count=0))
saturation_min_30_max_130 = EnhancementAlgorithm(
    enhancement_type=EnhancementType.Saturation,
    factor_determiner=FactorDeterminer(min_val=30, max_val=130, avg_count=0))
saturation_min_30_max_130 = EnhancementAlgorithm(
    enhancement_type=EnhancementType.Saturation,
    factor_determiner=FactorDeterminer(min_val=30, max_val=130, avg_count=0))
autocontrast_normal = EnhancementAlgorithm(
    enhancement_type=EnhancementType.AutoContrast,
    factor_determiner=FactorDeterminer())
autocontrast_cutoff_1percent = EnhancementAlgorithm(
    enhancement_type=EnhancementType.AutoContrast,
    factor_determiner=FactorDeterminer(cutoff=0.01))

# Set up algorithm lists
enhancement_algorithm_lists = [
    EnhancementAlgorithmList(
        'Brightness-Min-100',
        [brightness_min_100]
    ),
    EnhancementAlgorithmList(
        'Saturation-30-to-130_BrightFix',
        [saturation_min_30_max_130, brightness_min_100]
    ),
    EnhancementAlgorithmList(
        'Saturation-30-to-130_BrightFix-AutoContrast',
        [saturation_min_30_max_130, brightness_min_100, autocontrast_normal]
    ),
    EnhancementAlgorithmList(
        'Saturation-30-to-130_BrightFix-AutoContrast-Cutoff-1percent',
        [saturation_min_30_max_130, brightness_min_100, autocontrast_cutoff_1percent]
    )
]
#
#

resample_modes = [
    {'name': 'Nearest', 'mode': Image.NEAREST},
    {'name': 'BILINEAR', 'mode': Image.BILINEAR},
    {'name': 'BICUBIC', 'mode': Image.BICUBIC},
    {'name': 'LANCZOS', 'mode': Image.LANCZOS}
]


def test_resize_resample_modes(img, base_image_name):
    for resample_mode in resample_modes:
        mode = resample_mode['mode']
        mode_name = resample_mode['name']

        result_img = utils.resize_fill_image(
            img, OUTPUT_IMAGE_WIDTH, OUTPUT_IMAGE_HEIGHT, mode)

        output_filename = base_image_name + '-' + mode_name + '.jpg'
        output_path = os.path.join(
            settings.DirPaths.test_dest_images, 'resample', output_filename)

        result_img.save(output_path, quality=settings.ImageProcessing.jpeg_quality,optimize=true)


def test_enhancement_algorithms(img, base_image_name):
    enhancement_dir = os.path.join(
        settings.DirPaths.test_dest_images, 'enhancement')
    print(base_image_name)

    # Save original image
    output_path = os.path.join(enhancement_dir, base_image_name + '-original.jpg')
    img.save(output_path, quality=settings.ImageProcessing.jpeg_quality)

    for enhancement_algorithm_list in enhancement_algorithm_lists:
        # Enhance and save each enhanced image
        enhanced_img = enhancement_algorithm_list.enhance(img)

        output_filename = base_image_name + '-' + enhancement_algorithm_list.name + '.jpg'
        output_path = os.path.join(enhancement_dir, output_filename)

        enhanced_img.save(output_path, quality=settings.ImageProcessing.jpeg_quality)


# Program starts here
for filepath in settings.FilePaths.test_images:
    img = Image.open(filepath)

    base_image_name = os.path.basename(filepath)

    # test_resize_resample_modes(img, base_image_name)

    resized_img = utils.resize_fill_image(img, OUTPUT_IMAGE_WIDTH, OUTPUT_IMAGE_HEIGHT, Image.BILINEAR)

    test_enhancement_algorithms(resized_img, base_image_name)
