import math
import itertools

from tkinter import *
from tkinter.ttk import *
from ui.window import *

from userdata.debriefing_parser import *
from game.game import *
from game import event


class EventResultsMenu(Menu):
    debriefing = None  # type: Debriefing
    player_losses = {}  # type: typing.Dict[UnitType, int]
    enemy_losses = {}  # type: typing.Dict[UnitType, int]

    def __init__(self, window: Window, parent, game: Game, event: Event):
        super(EventResultsMenu, self).__init__(window, parent, game)
        self.frame = window.right_pane
        self.event = event
        self.finished = False

    def display(self):
        self.window.clear_right_pane()

        if not self.finished:
            Button(self.frame, text="no losses, succ", command=self.simulate_result(0, 1, True)).grid(row=0, column=0)
            Button(self.frame, text="no losses, fail", command=self.simulate_result(0, 1, False)).grid(row=0, column=1)

            Button(self.frame, text="half losses, succ", command=self.simulate_result(0.5, 0.5, True)).grid(row=1, column=0)
            Button(self.frame, text="half losses, fail", command=self.simulate_result(0.5, 0.5, False)).grid(row=1, column=1)

            Button(self.frame, text="full losses, succ", command=self.simulate_result(1, 0, True)).grid(row=2, column=0)
            Button(self.frame, text="full losses, fail", command=self.simulate_result(1, 0, False)).grid(row=2, column=1)
        else:
            row = 0
            if self.event.is_successfull(self.debriefing):
                Label(self.frame, text="Operation success").grid(column=0, row=row, columnspan=1); row += 1
            else:
                Label(self.frame, text="Operation failed").grid(column=0, row=row, columnspan=1); row += 1

            Separator(self.frame, orient='horizontal').grid(column=0, row=row, columnspan=1, sticky=NE); row += 1
            Label(self.frame, text="Player losses").grid(row=row, columnspan=1); row += 1
            for unit_type, count in self.player_losses.items():
                Label(self.frame, text=db.unit_type_name(unit_type)).grid(column=0, row=row)
                Label(self.frame, text="{}".format(count)).grid(column=1, row=row)
                row += 1

            Separator(self.frame, orient='horizontal').grid(column=0, row=row, columnspan=1, sticky=NE); row += 1
            Label(self.frame, text="Enemy losses").grid(columnspan=1, row=row); row += 1
            for unit_type, count in self.enemy_losses.items():
                Label(self.frame, text=db.unit_type_name(unit_type)).grid(column=0, row=row)
                Label(self.frame, text="{}".format(count)).grid(column=1, row=row)
                row += 1

            Button(self.frame, text="Okay", command=self.dismiss).grid(column=0, columnspan=1, row=row); row += 1

    def simulate_result(self, player_factor: float, enemy_factor: float, result: bool):
        def action():
            debriefing = Debriefing()

            def count_planes(groups: typing.List[FlyingGroup], mult: float) -> typing.Dict[UnitType, int]:
                result = {}
                for group in groups:
                    for unit in group.units:
                        result[unit.unit_type] = result.get(unit.unit_type, 0) + 1 * mult

                return {x: math.ceil(y) for x, y in result.items() if y >= 1}

            player_planes = self.event.operation.mission.country(self.game.player).plane_group
            enemy_planes = self.event.operation.mission.country(self.game.enemy).plane_group

            self.player_losses = count_planes(player_planes, player_factor)
            self.enemy_losses = count_planes(enemy_planes, enemy_factor)

            debriefing.destroyed_units = {
                self.game.player: self.player_losses,
                self.game.enemy: self.enemy_losses,
            }

            self.finished = True
            self.game.finish_event(self.event, debriefing)
            self.display()
            self.game.pass_turn()

        return action