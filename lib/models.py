class GridBox:
    """
    Class used to create and assign attributes to each individual box on a sudoku board

    Arguments:
    - box_id (str): The unique id assigned to each box based on their x and y coordinates in the game grid
    - box_id_list (list): A list including the box_ids for every one of the boxes that will be created for this game grid
    - grid_size (int): The length of each side the game grid. All game grids are assumed to be square.

    Upon initial creation the value_options_list attribute assumes that all potential value options are still active for a box
    """

    def __init__(self, box_id: str, box_id_list: list, grid_size: int = 9):
        # self.build_box_attributes(box_id, box_id_list, grid_size)
        self.box_id = box_id
        self.box_id_list = box_id_list
        self.grid_size = grid_size

        self.box_setup()

    def box_setup(self):
        self.confirmed_val = None
        self.val_opts_list = self.make_val_opt_list()

        self.box_y_coord = self.box_id[0]
        self.box_x_coord = self.box_id[2]

        self.square_id = self.get_square_id(self.box_id)

        self.assoc_box_ids = self.create_list_of_assoc_box_ids()
        self.assoc_row_boxes = self.get_assoc_row_boxes()
        self.assoc_col_boxes = self.get_assoc_col_boxes()
        self.assoc_square_boxes = self.get_assoc_square_boxes()

    def make_val_opt_list(self):
        return [n for n in range(1, self.grid_size + 1)]

    def get_row_id(self, id):
        return int(id[0])

    def get_col_id(self, id):
        return int(id[2])

    def get_square_index(self, id):
        if int(id) < (self.grid_size * 0.34):
            return "1"
        elif int(id) > (self.grid_size * 0.67):
            return "3"
        else:
            return "2"

    def get_square_id(self, id):
        square_y = self.get_square_index(id[0])
        square_x = self.get_square_index(id[2])

        return "_".join([square_y, square_x])

    def y_coord_match(self, id):
        return self.get_row_id(id) == int(self.box_y_coord)

    def x_coord_match(self, id):
        return self.get_col_id(id) == int(self.box_x_coord)

    def square_match(self, id):
        return self.get_square_id(id) == self.square_id

    def not_self(self, id):
        return id != self.box_id

    def any_valid_match(self, id):
        return (
            self.x_coord_match(id) or self.y_coord_match(id) or self.square_match(id)
        ) and self.not_self(id)

    def create_list_of_assoc_box_ids(self):
        return [b for b in self.box_id_list if self.any_valid_match(b)]

    def get_assoc_row_boxes(self):
        return [
            b for b in self.assoc_box_ids if self.get_row_id(b) == int(self.box_y_coord)
        ]

    def get_assoc_col_boxes(self):
        return [
            b for b in self.assoc_box_ids if self.get_col_id(b) == int(self.box_x_coord)
        ]

    def get_assoc_square_boxes(self):
        return [
            b
            for b in self.assoc_box_ids
            if self.get_square_id(b) == self.square_id
        ]
