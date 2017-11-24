from PIL import ImageStat, ImageEnhance, ImageOps
import operator
import functools
import math
from ctg_builder import utils


class FactorDeterminer:

    def __init__(self, max_val=None, min_val=None, target_val=None, avg_count=0, cutoff=0):
        self.max_val = max_val
        self.min_val = min_val
        self.target_val = target_val
        self.avg_count = avg_count
        self.cutoff = cutoff

    def determine(self, orig_val):
        if self.max_val is not None and orig_val > self.max_val:
            factors = [self.max_val / orig_val]
        elif self.min_val is not None and orig_val < self.min_val:
            factors = [self.min_val / orig_val]
        elif self.target_val is not None:
            factors = [self.target_val / orig_val]
        else:
            return 1

        factors.extend([1] * self.avg_count)
        factor = utils.mean(factors)
        return factor


class EnhancementType:
    Brightness = 0
    Saturation = 1
    AutoContrast = 2


class EnhancementAlgorithm:

    def __init__(self, enhancement_type, factor_determiner):
        self.enhancement_type = enhancement_type
        self.factor_determiner = factor_determiner

    def enhance(self, img):
        enhancer = None
        if self.enhancement_type is EnhancementType.Brightness:
            orig_val = get_brightness(img)
            enhancer = ImageEnhance.Brightness(img)
            print('orig_brightness = ' + str(orig_val))

        elif self.enhancement_type is EnhancementType.Saturation:
            orig_val = get_saturation(img)
            enhancer = ImageEnhance.Color(img)
            print('orig_saturation = ' + str(orig_val))

        if enhancer:
            factor = self.factor_determiner.determine(orig_val)
            return enhancer.enhance(factor)
        else:
            if self.enhancement_type is EnhancementType.AutoContrast:
                # Autocontrast once before applying cutoff
                result_img = ImageOps.autocontrast(img)

                if self.factor_determiner.cutoff != 0:
                    result_img = ImageOps.autocontrast(
                        result_img, cutoff=self.factor_determiner.cutoff)

                return result_img

        print('Invalid algorithm')
        return img


class EnhancementAlgorithmList:

    def __init__(self, name, enhancement_algorithms):
        self.name = name
        self.enhancement_algorithms = enhancement_algorithms

    def enhance(self, img):
        result_img = img
        for enhancement_algorithm in self.enhancement_algorithms:
            result_img = enhancement_algorithm.enhance(result_img)

        return result_img


# Sourced from http://stackoverflow.com/a/7170023
def equalize(img):
    h = img.convert("L").histogram()
    lut = []
    for b in range(0, len(h), 256):
        # step size
        step = functools.reduce(operator.add, h[b:b + 256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + h[i + b]
    # map image through lookup table
    return img.point(lut * 3)


# Sourced from http://stackoverflow.com/a/3498247
def get_brightness(img):
    stat = ImageStat.Stat(img)
    r, g, b = stat.mean
    return math.sqrt(0.241 * (r ** 2) + 0.691 * (g ** 2) + 0.068 * (b ** 2))


def get_saturation(img):
    hsv_img = img.convert('HSV')
    stat = ImageStat.Stat(hsv_img)
    h, s, v = stat.mean
    return s
