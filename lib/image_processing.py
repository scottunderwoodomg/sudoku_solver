import cv2
import pytesseract

from PIL import Image


"""
convert_to_bw is a function that converts the photograph of a sudoku grid 
to black and white for improved OCR and then saves the new copy with a 
unique filename.
"""


def convert_to_bw(image_file, threshold):
    image_filename = image_file[0 : len(image_file) - 4]

    column = Image.open(image_file)
    gray = column.convert("L")
    blackwhite = gray.point(lambda x: 0 if x < threshold else 255, "1")

    new_filename = image_filename + "_bw.jpg"
    blackwhite.save(new_filename)


def get_image_size(image_file):
    image = Image.open(image_file)
    image_dimensions = image.size
    return image_dimensions


def crop_image(image_file, left, upper, right, lower):
    im = Image.open(image_file)
    im_crop = im.crop((left, upper, right, lower))
    return im_crop


def generate_box_name(row_id, box_id):
    box_name = str(row_id) + "_" + str(box_id)
    return box_name


def save_cropped_image(cropped_image, box_name, file_path="image_files/box_images/"):
    composite_file_path = file_path + box_name + ".jpg"
    cropped_image.save(composite_file_path)


def refine_cropped_image(
    cropped_image, temp_image_path="image_files/temp_image_files/temp_image.jpg"
):
    cropped_image.save(temp_image_path)
    image_size = get_image_size(temp_image_path)
    trim_size = image_size[0] * 0.1
    trimmed_image = crop_image(
        temp_image_path,
        trim_size,
        trim_size,
        (image_size[0] - trim_size),
        (image_size[1] - trim_size),
    )

    return trimmed_image


# TODO: Need to break up into smaller functions
def generate_crop_coordinates(image_file, grid_size=9):
    image_dimensions = get_image_size(image_file)
    image_width = image_dimensions[0]
    image_height = image_dimensions[1]

    box_size_x = image_width / grid_size
    box_size_y = image_height / grid_size

    row_id = 1
    current_upper = 0
    current_lower = current_upper + box_size_y

    while row_id <= 9:
        box_id = 1
        current_left = 0
        current_right = current_left + box_size_x

        while box_id <= 9:
            cropped_image = crop_image(
                image_file, current_left, current_upper, current_right, current_lower
            )
            cropped_image = refine_cropped_image(cropped_image)

            box_name = generate_box_name(row_id, box_id)

            save_cropped_image(cropped_image, box_name)

            current_left += box_size_x
            current_right += box_size_x
            box_id += 1

        current_upper += box_size_y
        current_lower += box_size_y
        row_id += 1


convert_to_bw("image_files/test_images/sudoku_test_image.jpg", 75)

generate_crop_coordinates("image_files/test_images/sudoku_test_image_bw.jpg")


import os
from shutil import copyfile


def duplicate_cropped_image(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") and len(filename) == 7:
            base_filename = filename[0 : len(filename) - 4]
            for n in range(1, 6):
                copy_filename = base_filename + "_copy" + str(n) + ".jpg"
                src = directory + filename
                dst = directory + copy_filename
                copyfile(src, dst)


def get_list_of_box_names(directory):
    box_name_list = []
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") and "composite" not in filename:
            box_name = filename[0:3]
            box_name_list.append(box_name)
    box_name_list = set(box_name_list)
    return box_name_list


def get_list_of_file_copy_names(box_name, directory):
    file_name_list = []
    for filename in os.listdir(directory):
        if box_name in filename and "composite" not in filename:
            file_name_list.append(filename)

    return file_name_list


def produce_composite_images(box_name_list, directory):
    for box_name in box_name_list:
        file_name_list = get_list_of_file_copy_names(box_name, directory)

        images = [Image.open(directory + x) for x in file_name_list]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new("RGB", (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        composite_image_name = box_name + "_composite.jpg"
        new_im.save(directory + composite_image_name)


def build_composite_images(directory):
    box_id_list = get_list_of_box_names(directory)

    duplicate_cropped_image(directory)

    box_name_list = get_list_of_box_names(directory)

    produce_composite_images(box_name_list, directory)


active_ditectory = "image_files/box_images/"

build_composite_images(active_ditectory)


# Read Grid From Images


def adjust_box_threshold(file_path, box_name):
    composite_file_path = file_path + box_name + ".jpg"
    img = cv2.imread(composite_file_path)
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(composite_file_path, img)


def read_box_image(
    file_path, box_name, temp_image_path="image_files/temp_image_files/temp_image.jpg"
):
    composite_file_path = file_path + box_name + ".jpg"

    # image_size = get_image_size(composite_file_path)
    # cropped_image = crop_image(composite_file_path, 30, 30, (image_size[0]-30), (image_size[1]-30))

    # cropped_image.save(temp_image_path)

    # img = cv2.imread(temp_image_path)
    img = cv2.imread(composite_file_path)
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(
        img, config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789"
    )
    return text


def collapse_value_text(box_value):
    expanded_box_value_dict = {}
    for char in box_value:
        if char not in expanded_box_value_dict.keys():
            expanded_box_value_dict[char] = 1
        else:
            expanded_box_value_dict[char] += 1

    assumed_box_value = max(expanded_box_value_dict, key=expanded_box_value_dict.get)
    return assumed_box_value


def blanks_as_zeros(box_value):
    if len(box_value) == 0:
        return "0"
    else:
        return box_value


def read_box_images_to_grid(file_path="image_files/box_images/"):
    starting_grid = [[], [], [], [], [], [], [], [], []]

    starting_row_number = 1

    while starting_row_number <= 9:
        starting_box_number = 1

        while starting_box_number <= 9:
            box_name = generate_box_name(starting_row_number, starting_box_number)
            box_name = box_name + "_composite"

            adjust_box_threshold(file_path, box_name)

            box_value = read_box_image(file_path, box_name)

            box_value = blanks_as_zeros(box_value)

            box_value = collapse_value_text(box_value)

            box_value = int(box_value)

            starting_grid[starting_row_number - 1].append(box_value)

            starting_box_number += 1

        starting_row_number += 1

    return starting_grid


starting_grid = read_box_images_to_grid()

for row in starting_grid:
    print(row)