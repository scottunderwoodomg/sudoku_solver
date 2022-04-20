import pytest
from lib.models import GridBox
from lib.solver_tools import GridSolver


class TestGridBox:
    test_board = [
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

    box_id_list = GridSolver(test_board).generate_box_id_list()
    boxes = GridSolver(test_board).create_defined_boxes()

    @pytest.fixture(scope="module")
    def test_box(self):
        return GridBox("3_6", self.box_id_list)

    @pytest.fixture(scope="module")
    def comp_box_id(self):
        return "1_6"

    def test_make_val_opt_list(self, test_box):
        assert test_box.make_val_opt_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_square_match(self, test_box, comp_box_id):
        assert test_box.square_match(comp_box_id)

    def test_y_coord_match(self, test_box, comp_box_id):
        assert not test_box.y_coord_match(comp_box_id)

    def test_x_coord_match(self, test_box, comp_box_id):
        assert test_box.x_coord_match(comp_box_id)

    def test_not_self(self, test_box, comp_box_id):
        assert test_box.not_self(comp_box_id)

    def test_create_list_of_assoc_box_ids(self, test_box):
        assert test_box.create_list_of_assoc_box_ids() == [
            '3_1',
            '3_2',
            '3_3',
            '1_4',
            '2_4',
            '3_4',
            '1_5',
            '2_5',
            '3_5',
            '1_6',
            '2_6',
            '4_6',
            '5_6',
            '6_6',
            '7_6',
            '8_6',
            '9_6',
            '3_7',
            '3_8',
            '3_9'
        ]

    def test_get_assoc_row_boxes(self, test_box):
        test_box.create_list_of_assoc_box_ids()
        assert test_box.get_assoc_row_boxes() == [
            '3_1',
            '3_2',
            '3_3',
            '3_4',
            '3_5',
            '3_7',
            '3_8',
            '3_9'
        ]

    def test_get_assoc_col_boxes(self, test_box):
        test_box.create_list_of_assoc_box_ids()
        assert test_box.get_assoc_col_boxes() == [
            '1_6',
            '2_6',
            '4_6',
            '5_6',
            '6_6',
            '7_6',
            '8_6',
            '9_6',
        ]

    def test_get_assoc_square_boxes(self, test_box):
        test_box.create_list_of_assoc_box_ids()
        assert test_box.get_assoc_square_boxes() == [
            '1_4',
            '2_4',
            '3_4',
            '1_5',
            '2_5',
            '3_5',
            '1_6',
            '2_6'
        ]
