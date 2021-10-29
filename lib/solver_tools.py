from grid_box import GridBox
import copy

# TODO: Add type hints to all functions
# TODO: update dict iteration to in dict.items()


class GridSolver:
    def __init__(self, game_grid):
        self.game_grid = game_grid
        self.grid_size = len(game_grid)
        self.box_id_list = self.generate_box_id_list(self.grid_size)
        self.boxes = self.create_defined_boxes(self.box_id_list, self.grid_size)

        self.completed_game_grid = self.run_solver_attempt(
            game_grid, self.boxes, self.grid_size
        )

    def generate_box_id_list(self):
        return [
            "_".join(str(row), str(col))
            for col in range(1, self.grid_size + 1)
            for row in range(1, self.grid_size + 1)
        ]

    def create_defined_boxes(self):
        boxes = {}
        for box in self.box_id_list:
            boxes[box] = GridBox(box, self.box_id_list, self.grid_size)

        return boxes

    def return_grid_value(self, box_attr):
        return self.game_grid[box_attr["row_id"] - 1][box_attr["col_id"] - 1]

    # TODO: Break up this function and anything else this big
    def lock_initial_values(self):
        for box, box_attr in self.boxes.items():
            grid_value = self.return_grid_value(box_attr)
            if grid_value != 0:
                box_attr["confirmed_value"] = grid_value
                box_attr["value_options_list"] = [grid_value]

        return self.boxes

    def remove_invalid_options(self, boxes):
        for box in boxes:
            if boxes[box].confirmed_value is not None:
                # primary_box_id = boxes[box].box_id
                primary_box_value = boxes[box].confirmed_value
                associated_boxes = boxes[box].associated_box_ids

                for comp_box in associated_boxes:
                    temp_options_list = boxes[comp_box].value_options_list
                    if primary_box_value in temp_options_list:
                        temp_options_list.remove(primary_box_value)
                    boxes[comp_box].value_options_list = temp_options_list
            else:
                pass

        return boxes

    def remove_invalid_options_infered(self, boxes):
        for box in boxes:
            box_options = boxes[box].value_options_list
            box_option_count = len(box_options)
            associated_row_boxes = boxes[box].associated_row_boxes
            associated_col_boxes = boxes[box].associated_col_boxes
            associated_square_boxes = boxes[box].associated_square_boxes
            associations_list = [
                associated_row_boxes,
                associated_col_boxes,
                associated_square_boxes,
            ]
            for association in associations_list:
                non_matching_associated_boxes = []
                value_option_matches = 1
                for comp_box in association:
                    if boxes[comp_box].value_options_list == box_options:
                        value_option_matches += 1
                    else:
                        non_matching_associated_boxes.append(comp_box)
                if value_option_matches == box_option_count and box_option_count > 1:
                    for associated_box in non_matching_associated_boxes:
                        temp_options_list = boxes[associated_box].value_options_list
                        for value in box_options:
                            if value in boxes[associated_box].value_options_list:
                                temp_options_list.remove(value)
                        boxes[associated_box].value_options_list = temp_options_list
                else:
                    pass

        return boxes

    def lock_infered_values_by_elimination(self, boxes):
        for box in boxes:
            box_options = boxes[box].value_options_list
            associated_row_boxes = boxes[box].associated_row_boxes
            associated_col_boxes = boxes[box].associated_col_boxes
            associated_square_boxes = boxes[box].associated_square_boxes
            associations_list = [
                associated_row_boxes,
                associated_col_boxes,
                associated_square_boxes,
            ]

            for value in box_options:
                for association in associations_list:
                    option_presence_count = 0
                    for comp_box in association:
                        if value in boxes[comp_box].value_options_list:
                            option_presence_count += 1
                    if option_presence_count == 0:
                        boxes[box].confirmed_value = value
                        boxes[box].value_options_list = [value]
        return boxes

    def lock_new_values(self, boxes):
        for box in boxes:
            if (
                len(boxes[box].value_options_list) == 1
                and boxes[box].confirmed_value is None
            ):
                boxes[box].confirmed_value = boxes[box].value_options_list[0]

        return boxes

    def count_confirmed_boxes(self, boxes):
        confirmed_boxes = 0
        for box in boxes:
            if boxes[box].confirmed_value is not None:
                confirmed_boxes += 1
        return confirmed_boxes

    def write_to_grid(self, game_grid, boxes):
        for box in boxes:
            row = boxes[box].row_id - 1
            col = boxes[box].col_id - 1
            value = boxes[box].confirmed_value

            game_grid[row][col] = value

        return game_grid

    def all_values_unique(self, boxes):
        for box in boxes:
            box_value = boxes[box].confirmed_value
            if box_value is not None:
                for comp_box in boxes[box].associated_box_ids:
                    if boxes[comp_box].confirmed_value == box_value:
                        return False
        return True

    def attempt_grid_completion(
        self, boxes, confirmed_boxes, total_box_count, end_loop, loop_count
    ):
        while confirmed_boxes < total_box_count and not end_loop:
            previous_confirmed_boxes = self.count_confirmed_boxes(boxes)

            boxes = self.remove_invalid_options(boxes)
            boxes = self.lock_new_values(boxes)
            boxes = self.lock_infered_values_by_elimination(boxes)
            boxes = self.remove_invalid_options_infered(boxes)
            boxes = self.lock_new_values(boxes)
            boxes = self.lock_infered_values_by_elimination(boxes)
            confirmed_boxes = self.count_confirmed_boxes(boxes)
            if previous_confirmed_boxes == confirmed_boxes:
                end_loop = True
            loop_count += 1

        attempt_results = {
            "attempt_boxes": boxes,
            "confirmed_boxes": confirmed_boxes,
            "loop_ended": end_loop,
        }

        return attempt_results

    def revert_simulated_value(self, boxes, simulation_box):
        boxes[simulation_box].confirmed_value = None
        boxes[simulation_box].value_options_list = boxes[
            "simulation_box"
        ].value_options_list

        return boxes

    def get_max_potential_value(self, potential_values):
        max_improvement = 0
        best_potential_value = None
        for value in potential_values:
            if potential_values[value]["count_improvement"] > max_improvement:
                max_improvement = potential_values[value]["count_improvement"]
                best_potential_value = potential_values[value]

        return best_potential_value

    def complete_game_grid(self, game_grid, boxes, grid_size):
        total_box_count = grid_size * grid_size

        boxes = self.lock_initial_values(game_grid, boxes)

        confirmed_boxes = self.count_confirmed_boxes(boxes)
        loop_count = 1
        end_loop = False

        attempt_results = self.attempt_grid_completion(
            boxes, confirmed_boxes, total_box_count, end_loop, loop_count
        )
        boxes = attempt_results["attempt_boxes"]
        original_confirmed_count = attempt_results["confirmed_boxes"]

        simulation_attempts = []  # TODO: simulation_attempts dict
        simulation_box_omit_list = []
        original_boxes = copy.deepcopy(boxes)

        while original_confirmed_count < (total_box_count):
            simulation = SimulationAttempt(
                game_grid,
                grid_size,
                simulation_attempts,
                original_boxes,
                simulation_box_omit_list,
                original_confirmed_count,
                total_box_count,
            )

            if not simulation.simulation_outcome["sucesful_simulation"]:
                simulation_attempts.append(simulation)
                original_boxes = copy.deepcopy(boxes)
                if (
                    simulation.simulation_box_max_index
                    == simulation.simulation_box_index
                ):
                    simulation_box_omit_list.append(simulation.simulation_box)
            elif simulation.simulation_outcome["sucesful_simulation"]:
                boxes = simulation.simulation_outcome["simulation_attempt_boxes"]
                original_confirmed_count = total_box_count

        completed_game_grid = self.write_to_grid(game_grid, boxes)

        return completed_game_grid

    def run_solver_attempt(self, test_grid, boxes, grid_size):
        boxes = self.lock_initial_values(test_grid, boxes)

        boxes = self.remove_invalid_options(boxes)
        boxes = self.remove_invalid_options_infered(boxes)
        boxes = self.lock_new_values(boxes)

        completed_game_grid = self.complete_game_grid(test_grid, boxes, grid_size)

        for row in completed_game_grid:
            print(row)

        return completed_game_grid


class SimulationAttempt(GridSolver):
    def __init__(
        self,
        game_grid,
        grid_size,
        simulation_attempts,
        original_boxes,
        simulation_box_omit_list,
        original_confirmed_count,
        total_box_count,
    ):
        self.game_grid = game_grid
        self.grid_size = grid_size

        self.simulation_id = self.get_next_simulation_id(simulation_attempts)
        self.simulation_box = self.find_shortest_options_list(
            original_boxes, simulation_box_omit_list
        )
        self.simulation_box_index = self.get_next_simulation_box_index(
            simulation_attempts, self.simulation_box
        )
        self.simulation_box_max_index = (
            len(original_boxes[self.simulation_box].value_options_list) - 1
        )
        self.simulation_value = original_boxes[self.simulation_box].value_options_list[
            self.simulation_box_index
        ]
        self.simulation_outcome = None
        self.simulation_boxes = self.apply_simulated_value(
            original_boxes, self.simulation_box, self.simulation_value
        )
        self.original_confirmed_count = original_confirmed_count
        self.total_box_count = total_box_count

        simulation_results = self.simulate_grid_completion(
            self.simulation_boxes, self.original_confirmed_count, self.total_box_count
        )
        self.simulation_outcome = simulation_results

    def simulate_grid_completion(
        self,
        simulation_boxes,
        original_confirmed_count,
        total_box_count,
        end_loop=False,
    ):
        confirmed_boxes = original_confirmed_count
        loop_count = 1
        while confirmed_boxes < total_box_count and not end_loop:
            previous_confirmed_boxes = confirmed_boxes
            simulation_boxes = self.remove_invalid_options(simulation_boxes)
            simulation_boxes = self.lock_new_values(simulation_boxes)
            simulation_boxes = self.lock_infered_values_by_elimination(simulation_boxes)
            simulation_boxes = self.remove_invalid_options_infered(simulation_boxes)
            simulation_boxes = self.lock_new_values(simulation_boxes)
            simulation_boxes = self.lock_infered_values_by_elimination(simulation_boxes)
            confirmed_boxes = self.count_confirmed_boxes(simulation_boxes)
            sucesful_simulation = False
            if (previous_confirmed_boxes == confirmed_boxes - 1) or (
                previous_confirmed_boxes == confirmed_boxes
            ):
                end_loop = True

            if confirmed_boxes == total_box_count and self.all_values_unique(
                simulation_boxes
            ):
                sucesful_simulation = True
            loop_count += 1

        attempt_results = {
            "simulation_attempt_boxes": simulation_boxes,
            "simulation_confirmed_boxes": confirmed_boxes,
            "loop_ended": end_loop,
            "sucesful_simulation": sucesful_simulation,
        }

        return attempt_results

    def find_shortest_options_list(self, boxes, test_box_omit_list):
        shortest_list_length = 9
        shotest_list_id = None
        for box in boxes:
            box_options_count = len(boxes[box].value_options_list)
            if (
                box_options_count < shortest_list_length
                and boxes[box].confirmed_value is None
                and boxes[box].box_id not in test_box_omit_list
            ):
                shortest_list_length = box_options_count
                shotest_list_id = boxes[box].box_id

        return shotest_list_id

    def get_next_simulation_id(self, simulation_attempts):
        simulation_count = len(simulation_attempts)
        if simulation_count == 0:
            next_simulation_id = 1
        else:
            latest_simulation_index = len(simulation_attempts) - 1
            latest_simulation_id = simulation_attempts[
                latest_simulation_index
            ].simulation_id
            next_simulation_id = latest_simulation_id + 1

        return next_simulation_id

    def get_next_simulation_box_index(self, simulation_attempts, simulation_box):
        if len(simulation_attempts) == 0:
            next_simulation_box_index = 0
        else:
            latest_simulation_index = len(simulation_attempts) - 1
            latest_simulation_box = simulation_attempts[
                latest_simulation_index
            ].simulation_box
            latest_simulation_box_index = simulation_attempts[
                latest_simulation_index
            ].simulation_box_index

            if simulation_box == latest_simulation_box:
                next_simulation_box_index = latest_simulation_box_index + 1
            else:
                next_simulation_box_index = 0
        return next_simulation_box_index

    def apply_simulated_value(self, boxes, simulation_box, simulation_value):
        boxes[simulation_box].confirmed_value = simulation_value
        return boxes
