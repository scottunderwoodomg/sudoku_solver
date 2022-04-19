#from PIL import Image

#from lib.Image_processing import imageProcessor
from lib.solver_tools import GridSolver

"""
def get_image_size(image_file):
    image = Image.open(image_file)
    image_dimensions = image.size
    return image_dimensions
"""


#def get_image_size(image_file):
#    return Image.open(image_file).size


# print(get_image_size("image_files/test_images/sudoku_test_image.jpg"))

# print(list(range(1, 9 + 1)))

#processor = imageProcessor("image_files/test_images/sudoku_test_image.jpg")
#result = processor.process()

#for r in result:
#    print(r)


med = [
    [0, 6, 0, 2, 0, 0, 3, 1, 9],
    [0, 0, 0, 0, 9, 0, 0, 8, 0],
    [7, 0, 0, 8, 6, 0, 4, 0, 0],
    [0, 0, 0, 6, 7, 0, 0, 0, 5],
    [4, 0, 7, 0, 5, 8, 0, 0, 0],
    [0, 0, 0, 3, 0, 2, 0, 0, 0],
    [6, 2, 0, 7, 0, 1, 0, 0, 0],
    [0, 5, 0, 0, 0, 0, 6, 2, 0],
    [0, 0, 0, 5, 0, 0, 1, 9, 0]
]

easy = [
    [2, 0, 0, 5, 1, 0, 0, 0, 4],
    [4, 0, 9, 0, 6, 8, 0, 0, 0],
    [0, 0, 8, 0, 0, 0, 0, 7, 0],
    [0, 0, 0, 8, 9, 0, 7, 2, 0],
    [1, 0, 0, 0, 0, 5, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 5, 0, 8],
    [0, 6, 1, 0, 0, 0, 0, 9, 0],
    [0, 2, 4, 1, 3, 9, 8, 0, 6],
    [0, 5, 3, 0, 8, 2, 4, 1, 7]
]

evil_board = [
    [7, 0, 0, 8, 0, 0, 1, 2, 0],
    [0, 9, 0, 0, 4, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 3],
    [1, 0, 0, 2, 0, 0, 5, 7, 0],
    [0, 0, 0, 0, 0, 0, 0, 6, 0],
    [0, 0, 2, 0, 0, 8, 0, 0, 0],
    [0, 7, 0, 0, 0, 9, 3, 5, 0],
    [0, 0, 0, 5, 0, 0, 0, 0, 6],
    [3, 0, 0, 0, 0, 0, 0, 0, 8],
]

result = GridSolver(evil_board)

for r in result.completed_game_grid:
    print(r)
