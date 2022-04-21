import cv2
import pytesseract
import os
import os.path

from PIL import Image
from shutil import copyfile


"""
convert_to_bw is a function that converts the photograph of a sudoku grid
to black and white for improved OCR and then saves the new copy with a
unique filename.
"""


class ImageProcessor:
    def __init__(self, input_image_path, grid_size=9) -> list:
        self.input_image_path = input_image_path
        self.grid_size = grid_size
        self.box_image_file_path = "image_files/box_images/"
        self.temp_image_path = "image_files/temp_image_files/temp_image.jpg"

        self.processed_grid = self.run_processor()

    def process(self):
        self.convert_to_bw()
        self.bw_image_dimensions = self.return_image_size(
            self.input_image_path.replace(".jpg", "_bw.jpg")
        )
        self.box_size_x = self.bw_image_dimensions[0] / self.grid_size
        self.box_size_y = self.bw_image_dimensions[1] / self.grid_size

        self.generate_crop_coordinates(self.input_image_path.replace(".jpg", "_bw.jpg"))

        self.build_composite_images()

        return self.read_box_images_to_grid()

    def image_cleanup(self):
        for root, dirs, files in os.walk(self.box_image_file_path):
            for file in files:
                os.remove(os.path.join(root, file))

    def run_processor(self):
        game_grid = self.process()
        self.image_cleanup()

        return game_grid

    def return_image_size(self, image_file):
        return Image.open(image_file).size

    def crop_image(self, image_file, left, upper, right, lower):
        return Image.open(image_file).crop((left, upper, right, lower))

    def generate_box_name(self, row_id, box_id, suffix=""):
        return str(row_id) + "_" + str(box_id) + suffix

    def save_cropped_image(self, cropped_image, box_name):
        cropped_image.save(self.box_image_file_path + box_name + ".jpg")

    def prepare_bw_filename(self):
        return self.input_image_path[0: len(self.input_image_path) - 4] + "_bw.jpg"

    def convert_to_bw(self, threshold=75):
        gray_image = Image.open(self.input_image_path).convert("L")
        bw_image = gray_image.point(lambda x: 0 if x < threshold else 255, "1")

        bw_image.save(self.prepare_bw_filename())

    def refine_cropped_image(self, cropped_image):
        # TODO: confirm why this is being saved at the start of this function and not elsewhere
        cropped_image.save(self.temp_image_path)

        image_size = self.return_image_size(self.temp_image_path)
        trim_size = image_size[0] * 0.1

        return self.crop_image(
            self.temp_image_path,
            trim_size,
            trim_size,
            (image_size[0] - trim_size),
            (image_size[1] - trim_size),
        )

    def process_box_image(
        self,
        image_file,
        current_left,
        current_upper,
        current_right,
        current_lower,
        row_pos,
        box_pos,
    ):
        cropped_image = self.crop_image(
            image_file,
            current_left,
            current_upper,
            current_right,
            current_lower,
        )

        self.save_cropped_image(
            self.refine_cropped_image(cropped_image),
            self.generate_box_name(row_pos, box_pos),
        )

    # TODO: Need to break up into smaller functions
    # TODO: Convert these into objects with their own attributes?
    def generate_crop_coordinates(self, image_file):
        position_list = list(range(1, self.grid_size + 1))
        current_upper = 0
        current_lower = current_upper + self.box_size_y

        for row_pos in position_list:
            current_left = 0
            current_right = current_left + self.box_size_x

            for box_pos in position_list:
                self.process_box_image(
                    image_file,
                    current_left,
                    current_upper,
                    current_right,
                    current_lower,
                    row_pos,
                    box_pos,
                )

                current_left += self.box_size_x
                current_right += self.box_size_x

            current_upper += self.box_size_y
            current_lower += self.box_size_y

    def get_list_of_box_names(self):
        return set(
            [
                fn[0:3]
                for fn in os.listdir(self.box_image_file_path)
                if fn.endswith(".jpg") and "composite" not in fn
            ]
        )

    def get_list_of_file_copy_names(self, box_name):
        return [
            fn
            for fn in os.listdir(self.box_image_file_path)
            if (box_name in fn and "composite" not in fn)
        ]

    def list_valid_filenames(self):
        return [
            fn
            for fn in os.listdir(self.box_image_file_path)
            if fn.endswith(".jpg") and len(fn) == 7
        ]

    def perform_duplication(self, fn):
        for n in range(1, 6):
            src = self.box_image_file_path + fn
            dst = f"{self.box_image_file_path}{fn[0 : len(fn) - 4]}_copy{str(n)}.jpg"
            copyfile(src, dst)

    def duplicate_cropped_image(self):
        for fn in self.list_valid_filenames():
            self.perform_duplication(fn)

    def return_dims(self, images):
        return zip(*(i.size for i in images))

    def produce_composite_images(self):
        for box_name in self.get_list_of_box_names():
            images = [
                Image.open(self.box_image_file_path + x)
                for x in self.get_list_of_file_copy_names(box_name)
            ]
            widths, heights = self.return_dims(images)

            total_width = sum(widths)
            max_height = max(heights)

            new_im = Image.new("RGB", (total_width, max_height))

            x_offset = 0
            for im in images:
                new_im.paste(im, (x_offset, 0))
                x_offset += im.size[0]

            new_im.save(self.box_image_file_path + box_name + "_composite.jpg")

    def build_composite_images(self):
        self.duplicate_cropped_image()
        self.produce_composite_images()

    # Read Grid From Images

    def apply_threshold_change(self, box_name):
        ret, img = cv2.threshold(
            cv2.imread(self.box_image_file_path + box_name + ".jpg"),
            127,
            255,
            cv2.THRESH_BINARY,
        )
        return img

    # TODO: determine if this step is redundant
    def adjust_box_threshold(self, box_name):
        cv2.imwrite(
            self.box_image_file_path + box_name + ".jpg",
            self.apply_threshold_change(box_name),
        )

    def read_box_image(self, box_name):
        return pytesseract.image_to_string(
            self.apply_threshold_change(box_name),
            config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789",
        )

    def blanks_as_zeros(self, box_value):
        return "0" if len(box_value) == 0 or box_value == "\x0c" else box_value

    # TODO: Need to figure out what this function actually does
    def collapse_value_text(self, box_value):
        expanded_box_value_dict = {}
        for char in box_value:
            if char not in expanded_box_value_dict.keys():
                expanded_box_value_dict[char] = 1
            else:
                expanded_box_value_dict[char] += 1

        return max(expanded_box_value_dict, key=expanded_box_value_dict.get)

    def establish_box_value(self, box_name):
        return int(
            self.collapse_value_text(
                self.blanks_as_zeros(self.read_box_image(box_name))
            )
        )

    def read_box_images_to_grid(self, file_path="image_files/box_images/"):
        starting_grid = [[], [], [], [], [], [], [], [], []]
        position_list = list(range(1, self.grid_size + 1))

        for row_num in position_list:
            for col_num in position_list:
                box_name = self.generate_box_name(row_num, col_num, suffix="_composite")

                self.adjust_box_threshold(box_name)

                box_value = self.establish_box_value(box_name)

                starting_grid[row_num - 1].append(box_value)

        return starting_grid
