from lib.models import GridBox
import copy

# TODO: Add type hints to all functions
# TODO: update dict iteration to in dict.items()
# TODO: step through logic and add summary of what each function does before refactoring them


class GridSolver:
    def __init__(self, game_grid):
        self.game_grid = game_grid
        self.grid_size = len(game_grid)
        self.total_box_count = self.grid_size**2
        self.box_id_list = self.generate_box_id_list()
        self.boxes = self.create_defined_boxes()

        # TODO: this should be removed from the init to avoid the dependency issue
        # self.completed_game_grid = self.run_solver_attempt()

    def generate_box_id_list(self):
        return [
            "_".join([str(row), str(col)])
            for col in range(1, self.grid_size + 1)
            for row in range(1, self.grid_size + 1)
        ]

    def create_defined_boxes(self):
        boxes = {}
        for box in self.box_id_list:
            boxes[box] = GridBox(box, self.box_id_list, self.grid_size)

        return boxes

    def return_grid_val(self, box_attr):
        return self.game_grid[int(box_attr.box_y_coord) - 1][
            int(box_attr.box_x_coord) - 1
        ]

    # TODO: Break up this function and anything else this big
    def lock_initial_vals(self):
        for box, box_attr in self.boxes.items():
            grid_val = self.return_grid_val(box_attr)
            if grid_val != 0:
                box_attr.confirmed_val = grid_val
                box_attr.val_opts_list = [grid_val]

        return self.boxes

    def remove_assoc_box_confirmed_vals(self, boxes, box, comp_box):
        return [
            v for v in boxes[comp_box].val_opts_list if v != boxes[box].confirmed_val
        ]

    def check_assoc_box_vals(self, box, boxes):
        for comp_box in boxes[box].assoc_box_ids:
            boxes[comp_box].val_opts_list = self.remove_assoc_box_confirmed_vals(
                boxes, box, comp_box
            )

        return boxes

    # TODO: check if this is redundant with logic in the inferred+associated branch
    def remove_invalid_opts(self, boxes):
        for box in boxes:
            if boxes[box].confirmed_val is not None:
                boxes = self.check_assoc_box_vals(box, boxes)
            # else:
            #    pass

        return boxes

    def generate_assoc_box_type_lists(self, box, boxes):
        return [
            boxes[box].assoc_row_boxes,
            boxes[box].assoc_col_boxes,
            boxes[box].assoc_square_boxes,
        ]

    def check_assoc_opt_list_matches(
        self, box, boxes, comp_box, opt_match_cnt, non_match_assoc_boxes
    ):
        if boxes[comp_box].val_opts_list == boxes[box].val_opts_list:
            opt_match_cnt += 1
        else:
            non_match_assoc_boxes.append(comp_box)

        return opt_match_cnt, non_match_assoc_boxes

    def assoc_boxes_with_common_opts(self, box, boxes, opt_match_cnt):
        return (
            opt_match_cnt == len(boxes[box].val_opts_list)
            and len(boxes[box].val_opts_list) > 1
        )

    def remove_opts_assoc_boxes_without_common_opts(self, box, boxes, assoc_box):
        return [
            v
            for v in boxes[assoc_box].val_opts_list
            if v not in boxes[box].val_opts_list
        ]

    def remove_invalid_opts_infered(self, boxes):
        for box in boxes:
            for association in self.generate_assoc_box_type_lists(box, boxes):
                non_match_assoc_boxes = []
                opt_match_cnt = 1
                for comp_box in association:
                    (
                        opt_match_cnt,
                        non_match_assoc_boxes,
                    ) = self.check_assoc_opt_list_matches(
                        box,
                        boxes,
                        comp_box,
                        opt_match_cnt,
                        non_match_assoc_boxes,
                    )
                if self.assoc_boxes_with_common_opts(box, boxes, opt_match_cnt):
                    for assoc_box in non_match_assoc_boxes:
                        boxes[
                            assoc_box
                        ].val_opts_list = self.remove_opts_assoc_boxes_without_common_opts(
                            box, boxes, assoc_box
                        )
                else:
                    pass

        return boxes

    def lock_infered_vals_by_elimination(self, boxes):
        for box in boxes:
            for val in boxes[box].val_opts_list:
                for association in self.generate_assoc_box_type_lists(box, boxes):
                    opt_presence_cnt = 0
                    for comp_box in association:
                        if val in boxes[comp_box].val_opts_list:
                            opt_presence_cnt += 1
                    if opt_presence_cnt == 0:
                        boxes[box].confirmed_val = val
                        boxes[box].val_opts_list = [val]
        return boxes

    def no_confirmed_val(self, box, boxes):
        return boxes[box].confirmed_val is None

    def single_unconfirmed_opt(self, box, boxes):
        return len(boxes[box].val_opts_list) == 1 and self.no_confirmed_val(box, boxes)

    def lock_new_vals(self, boxes):
        for box in boxes:
            if self.single_unconfirmed_opt(box, boxes):
                boxes[box].confirmed_val = boxes[box].val_opts_list[0]

        return boxes

    def count_confirmed_boxes(self, boxes):
        confirmed_boxes = 0
        for box in boxes:
            if not self.no_confirmed_val(box, boxes):
                confirmed_boxes += 1
        return confirmed_boxes

    def write_to_grid(self, game_grid, boxes):
        for box in boxes:
            game_grid[int(boxes[box].box_y_coord) - 1][
                int(boxes[box].box_x_coord) - 1
            ] = boxes[box].confirmed_val

        return game_grid

    def box_values_unique(self, box_1, box_2, boxes):
        return boxes[box_2].confirmed_val != boxes[box_1].confirmed_val

    def all_vals_unique(self, boxes):
        for box in boxes:
            if not self.no_confirmed_val(box, boxes):
                for comp_box in boxes[box].assoc_box_ids:
                    if not self.box_values_unique(box, comp_box, boxes):
                        return False
        return True

    def lock_new_and_infered_vals(self, boxes):
        return self.lock_infered_vals_by_elimination(self.lock_new_vals(boxes))

    def process_invalid_opts(self, boxes):
        return self.lock_new_and_infered_vals(self.remove_invalid_opts(boxes))

    def process_invalid_opts_infered(self, boxes):
        return self.lock_new_and_infered_vals(self.remove_invalid_opts_infered(boxes))

    def prepare_attempt_results(
        self, boxes, confirmed_boxes, end_loop, sucesful_simulation=None
    ):
        return {
            "attempt_boxes": boxes,
            "confirmed_boxes": confirmed_boxes,
            "loop_ended": end_loop,
            "sucesful_simulation": sucesful_simulation,
        }

    def attempt_grid_completion(self, boxes, confirmed_boxes, end_loop):
        while confirmed_boxes < self.total_box_count and not end_loop:
            previous_confirmed_boxes = self.count_confirmed_boxes(boxes)
            boxes = self.process_invalid_opts_infered(self.process_invalid_opts(boxes))
            confirmed_boxes = self.count_confirmed_boxes(boxes)
            if previous_confirmed_boxes == confirmed_boxes:
                end_loop = True

        return self.prepare_attempt_results(boxes, confirmed_boxes, end_loop)

    # TODO: Likely remove, appears to not be used
    # def revert_simulated_val(self, boxes, simulation_box):
    #    boxes[simulation_box].confirmed_val = None
    #    boxes[simulation_box].val_opts_list = boxes["simulation_box"].val_opts_list
    #    return boxes

    # TODO: Likely remove, appears to not be used
    # def get_max_potential_val(self, potential_vals):
    #    max_improvement = 0
    #    best_potential_val = None
    #    for val in potential_vals:
    #        if potential_vals[val]["count_improvement"] > max_improvement:
    #            max_improvement = potential_vals[val]["count_improvement"]
    #            best_potential_val = potential_vals[val]
    #    return best_potential_val

    # TODO: Break this up once I confirm how the simulation attempts are intended to work
    def complete_game_grid(self):
        boxes = self.lock_initial_vals()
        confirmed_boxes = self.count_confirmed_boxes(boxes)
        end_loop = False

        attempt_results = self.attempt_grid_completion(boxes, confirmed_boxes, end_loop)
        boxes = attempt_results["attempt_boxes"]
        original_confirmed_count = attempt_results["confirmed_boxes"]

        simulation_attempts = []  # TODO: simulation_attempts dict
        simulation_box_omit_list = []
        original_boxes = copy.deepcopy(boxes)

        while original_confirmed_count < (self.total_box_count):
            sim = SimulationAttempt(
                self.game_grid,
                self.grid_size,
                simulation_attempts,
                original_boxes,
                simulation_box_omit_list,
                original_confirmed_count,
                self.total_box_count,
            )

            if not sim.simulation_outcome["sucesful_simulation"]:
                simulation_attempts.append(sim)
                original_boxes = copy.deepcopy(boxes)
                if sim.simulation_box_max_index == sim.simulation_box_index:
                    simulation_box_omit_list.append(sim.simulation_box)
            elif sim.simulation_outcome["sucesful_simulation"]:
                boxes = sim.simulation_outcome["attempt_boxes"]
                original_confirmed_count = self.total_box_count

        completed_game_grid = self.write_to_grid(self.game_grid, boxes)

        return completed_game_grid

    def run_solver_attempt(self):
        # boxes = self.process_invalid_opts(self.lock_initial_vals())

        return self.complete_game_grid()


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
        self.simulation_box = self.find_shortest_opts_list(
            original_boxes, simulation_box_omit_list
        )
        self.simulation_box_index = self.get_next_simulation_box_index(
            simulation_attempts
        )
        self.simulation_box_max_index = (
            len(original_boxes[self.simulation_box].val_opts_list) - 1
        )
        self.simulation_val = original_boxes[self.simulation_box].val_opts_list[
            self.simulation_box_index
        ]
        self.simulation_outcome = None
        self.simulation_boxes = self.apply_simulated_val(original_boxes)
        self.original_confirmed_count = original_confirmed_count
        self.total_box_count = total_box_count

        self.simulation_outcome = self.simulate_grid_completion()

    def simulate_grid_completion(
        self,
        end_loop=False,
    ):
        confirmed_boxes = self.original_confirmed_count
        while confirmed_boxes < self.total_box_count and not end_loop:
            previous_confirmed_boxes = confirmed_boxes
            simulation_boxes = self.process_invalid_opts_infered(
                self.process_invalid_opts(self.simulation_boxes)
            )
            confirmed_boxes = self.count_confirmed_boxes(simulation_boxes)
            sucesful_simulation = False
            if (previous_confirmed_boxes == confirmed_boxes - 1) or (
                previous_confirmed_boxes == confirmed_boxes
            ):
                end_loop = True

            if confirmed_boxes == self.total_box_count and self.all_vals_unique(
                simulation_boxes
            ):
                sucesful_simulation = True

        return self.prepare_attempt_results(
            simulation_boxes, confirmed_boxes, end_loop, sucesful_simulation
        )

    def find_shortest_opts_list(self, boxes, test_box_omit_list):
        shortest_list_length = 9
        shotest_list_id = None
        for box in boxes:
            box_opts_count = len(boxes[box].val_opts_list)
            if (
                box_opts_count < shortest_list_length
                and boxes[box].confirmed_val is None
                and boxes[box].box_id not in test_box_omit_list
            ):
                shortest_list_length = box_opts_count
                shotest_list_id = boxes[box].box_id

        return shotest_list_id

    def is_first_simulation_attempt(self, simulation_attempts):
        return len(simulation_attempts) == 0

    # TODO: Unclear how if at all this is being used, potentially remove
    def get_next_simulation_id(self, simulation_attempts):
        if self.is_first_simulation_attempt(simulation_attempts):
            return 1
        else:
            # TODO: This potentially can just be the len of sim attempts?
            return self.get_latest_simulation(simulation_attempts).simulation_id + 1

    def get_latest_simulation(self, simulation_attempts):
        return simulation_attempts[len(simulation_attempts) - 1]

    def get_next_simulation_box_index(self, simulation_attempts):
        if self.is_first_simulation_attempt(simulation_attempts):
            next_simulation_box_index = 0
        else:
            latest_simulation_box = self.get_latest_simulation(
                simulation_attempts
            ).simulation_box
            latest_simulation_box_index = self.get_latest_simulation(
                simulation_attempts
            ).simulation_box_index

            if self.simulation_box != latest_simulation_box:
                next_simulation_box_index = 0
            else:
                next_simulation_box_index = latest_simulation_box_index + 1

        return next_simulation_box_index

    def apply_simulated_val(self, boxes):
        boxes[self.simulation_box].confirmed_val = self.simulation_val
        return boxes
