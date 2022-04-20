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
        return GridBox("1_1", self.box_id_list)

    def test_make_val_opt_list(self, test_box):
        assert test_box.make_val_opt_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]
