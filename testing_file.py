from PIL import Image

from lib.image_processing import imageProcessor

"""
def get_image_size(image_file):
    image = Image.open(image_file)
    image_dimensions = image.size
    return image_dimensions
"""


def get_image_size(image_file):
    return Image.open(image_file).size


# print(get_image_size("image_files/test_images/sudoku_test_image.jpg"))

# print(list(range(1, 9 + 1)))

processor = imageProcessor("image_files/test_images/sudoku_test_image.jpg")
result = processor.process()

for r in result:
    print(r)