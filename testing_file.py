from PIL import Image

"""
def get_image_size(image_file):
    image = Image.open(image_file)
    image_dimensions = image.size
    return image_dimensions
"""


def get_image_size(image_file):
    return Image.open(image_file).size


# print(get_image_size("image_files/test_images/sudoku_test_image.jpg"))

print(list(range(1, 9 + 1)))
