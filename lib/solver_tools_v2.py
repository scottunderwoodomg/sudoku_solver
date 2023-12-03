# from lib.models import GridBox
from models import GridBox


class GridSolver2:
    def __init__(self, game_grid):
        self.game_grid = game_grid
        self.grid_size = len(game_grid)
        self.total_box_count = self.grid_size**2
        self.box_id_list = self.generate_box_id_list()
        self.boxes = self.create_defined_boxes()
        # TODO: begin building out logic_application_loops record once I have ability to count locks
        # self.logic_application_loops = {}

        # TODO: this should be removed from the init to avoid the dependency issue
        # self.completed_game_grid = self.run_solver_attempt()

    def run_solver(self):
        """
        1. lock provided values
        2. remove provided values from all associated box option lists
        3. looks for boxes with only one viable option -> lock those
        4. remove locked values from all associated box option lists

        TODO: figure out how to loop reconcile_and_lock_associated_options until it stops prodicing more valid results

        5. find naked singles
        6. find hidden singles (for value in opt list, if value not in opt list of any associated boxes, lock value)
        7. find naked pairs (for opt list, if opt list for any associated boxes is 1:1, remove both opts from all other in set.  likely need to run this for rows,cols,boxes in order)
        8. find hidden pairs
        8. find locked candidates
        9. find pointing tuples
        10. find naked tripples
        11. find x-wings
        12. find y-wings

        """
        self.debug_output()

        self.apply_initial_vals()

        self.debug_output()

        self.reconcile_and_lock_associated_options()
        self.reconcile_and_lock_associated_options()
        self.reconcile_and_lock_associated_options()

        self.debug_output()

        self.reconcile_hidden_singles()

        self.debug_output()

        pass

    # Produces a list of all the possible box_id's based on grid size
    # TODO: Potentially does not need to be run on its own in the init?
    def generate_box_id_list(self) -> list:
        return [
            "_".join([str(row), str(col)])
            for col in range(1, self.grid_size + 1)
            for row in range(1, self.grid_size + 1)
        ]

    # Instantiates a box object for all of the necessary boxes defined in box_id_list
    def create_defined_boxes(self) -> dict:
        boxes = {}
        for box in self.box_id_list:
            boxes[box] = GridBox(box, self.box_id_list, self.grid_size)

        return boxes

    # Reads the provided game board and returns the value of a specific box based on provided y and x coordinates
    def return_grid_val(self, box_attr):
        return self.game_grid[int(box_attr.box_y_coord) - 1][
            int(box_attr.box_x_coord) - 1
        ]

    # TODO: Break up this function and anything else this big
    def apply_initial_vals(self):
        for box, box_attr in self.boxes.items():
            grid_val = self.return_grid_val(box_attr)
            if grid_val != 0:
                box_attr.confirmed_val = grid_val
                # TODO: figure out how to make it so that we don't need to also set the opts list here?
                box_attr.val_opts_list = [grid_val]

        return self.boxes

    def remove_confirmed_val_options(self):
        for box, box_attr in self.boxes.items():
            if box_attr.confirmed_val is not None:
                for associated_id in box_attr.assoc_box_ids:
                    try:
                        self.boxes[associated_id].val_opts_list.remove(
                            box_attr.confirmed_val
                        )
                    except:
                        pass

        return self.boxes

    def lock_sole_options(self):
        for box, box_attr in self.boxes.items():
            if len(box_attr.val_opts_list) == 1:
                box_attr.confirmed_val = box_attr.val_opts_list[0]

        return self.boxes

    def reconcile_and_lock_associated_options(self):
        self.remove_confirmed_val_options()
        self.lock_sole_options()

    # TODO: create and tear down objects as a way to pare down the multi-loop functions

    def reconcile_hidden_singles(self):
        # TODO: Define these reused loop definitions as a wrapper or decorator something?
        for box, box_attr in self.boxes.items():
            for option in box_attr.val_opts_list:
                for associated_set in [
                    box_attr.assoc_row_boxes,
                    box_attr.assoc_col_boxes,
                    box_attr.assoc_square_boxes,
                ]:
                    associated_value_pool = set(
                        [
                            value
                            for associated_box in associated_set
                            for value in self.boxes[associated_box].val_opts_list
                        ]
                    )
                    if option not in associated_value_pool:
                        box_attr.confirmed_val = option
                        # TODO: figure out how to make it so that we don't need to also set the opts list here?
                        box_attr.val_opts_list = [option]

        self.lock_sole_options()
        return self.boxes

    def count_locked_values(self):
        locked_val_cnt = 0
        for box, box_attr in self.boxes.items():
            if box_attr.confirmed_val is not None:
                locked_val_cnt += 1

        return locked_val_cnt

    def debug_output(self, type="partial"):
        print("Count of locked values: ", self.count_locked_values())

        if type == "full":
            for box, box_attr in self.boxes.items():
                print(box, box_attr.confirmed_val, box_attr.val_opts_list)

        print("########################")

    """
    def reconcile_hidden_singles(self):
        for box, box_attr in self.boxes.items():
            for associated_set in [box_attr.assoc_row_boxes,box_attr.assoc_col_boxes, box_attr.assoc_square_boxes]:
                for associated_box in associated_set:
                    if len(box_attr.val_opts_list) == 2 and box_attr.val_opts_list == self.boxes[associated_box].val_opts_list:
                        


    self.lock_sole_options()
    """


####################
# Misc. Testing
####################

test_board_1 = [
    [0, 6, 0, 2, 0, 0, 3, 1, 9],
    [0, 0, 0, 0, 9, 0, 0, 8, 0],
    [7, 0, 0, 8, 6, 0, 4, 0, 0],
    [0, 0, 0, 6, 7, 0, 0, 0, 5],
    [4, 0, 7, 0, 5, 8, 0, 0, 0],
    [0, 0, 0, 3, 0, 2, 0, 0, 0],
    [6, 2, 0, 7, 0, 1, 0, 0, 0],
    [0, 5, 0, 0, 0, 0, 6, 2, 0],
    [0, 0, 0, 5, 0, 0, 1, 9, 0],
]

test_board = [
    [0, 3, 0, 4, 0, 0, 0, 5, 0],
    [0, 0, 9, 0, 0, 3, 6, 0, 4],
    [0, 0, 0, 0, 0, 9, 7, 0, 0],
    [0, 0, 0, 0, 0, 6, 9, 0, 0],
    [0, 9, 5, 0, 0, 0, 0, 4, 3],
    [0, 0, 3, 2, 0, 0, 0, 0, 0],
    [0, 0, 6, 0, 0, 0, 0, 0, 0],
    [8, 0, 2, 1, 0, 0, 4, 0, 0],
    [0, 1, 0, 0, 0, 2, 0, 0, 0],
]


# GridSolver2(test_board).run_solver()
GridSolver2(test_board_1).run_solver()
