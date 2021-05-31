# -*- coding: utf-8 -*-
# SPORE: Symbolic Partial sOlvers for REalizability. 
# Copyright (C) 2021 - Charly Delfosse (University of Mons), Gaëtan Staquet (University of Mons), Clément Tamines (University of Mons)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from collections import defaultdict

from regular.gpg2arena import gpg2arena


def retrieve_expected_pg_arena(path):
    # open file
    with open(path, "r") as pg_file:
        info_line = pg_file.readline()  # first line has max index for vertices, vertices index start at 0

        max_index = int(info_line.rstrip().split(" ")[1][:-1])

        nbr_vertices = max_index + 1

        expected_arena = [[], [], []]  # vertices, priorities, successors

        expected_arena[0] = []

        expected_arena[1] = defaultdict(lambda: [])

        expected_arena[2] = [[] for _ in range(nbr_vertices)]

        # iterate over vertices
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priority = int(infos[1])
            player = int(infos[2])
            successors = [int(succ) for succ in infos[3].split(",")]

            expected_arena[0].append(index)

            expected_arena[1][priority].append(index)

            expected_arena[2][index].extend(successors)

        return expected_arena


def retrieve_expected_gpg_arena(path):
    # open file
    with open(path, "r") as gpg_file:

        # first line has max index for vertices and number of priority functions; vertices and function index start at 0
        info_line = gpg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

        nbr_vertices = max_index + 1

        expected_arena = [[], [], []]  # vertices, priorities, successors

        expected_arena[0] = []

        expected_arena[1] = [defaultdict(lambda: []) for _ in range(nbr_functions)]

        expected_arena[2] = [[] for _ in range(nbr_vertices)]

        # iterate over vertices
        for line in gpg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priority = [int(p) for p in infos[1].split(",")]
            player = int(infos[2])
            successors = [int(succ) for succ in infos[3].split(",")]

            expected_arena[0].append(index)

            for func in range(len(priority)):
                expected_arena[1][func][priority[func]].append(index)

            expected_arena[2][index].extend(successors)

        return expected_arena


class TestArena(unittest.TestCase):
    """
    Test cases for arenas encoded as BDDs.
    """

    def setUp(self):
        self.pg_test_files_path = "./arenas/pg/"
        self.pg_test_files = ["example_1.pg", "example_2.pg", "example_3.pg", "example_4.pg",
                              "example_5.pg"]
        self.pg_expected_values = [] * len(self.pg_test_files)

        self.gpg_test_files_path = "./arenas/gpg/"
        self.gpg_test_files = ["example_1.gpg", "example_2.gpg", "example_3.gpg", "example_4.gpg", "example_1_pg.gpg",
                               "example_2_pg.gpg", "example_3_pg.gpg", "example_4_pg.gpg", "example_5_pg.gpg"]
        self.gpg_expected_values = [] * len(self.gpg_test_files)

    def test_gpg_arena_creation(self):
        """
        Check if arenas are correctly loaded from files.
        """

        for file in self.gpg_test_files:

            file_path = self.gpg_test_files_path + file

            # load arena and get number of vertices
            arena = gpg2arena(file_path)

            nbr_vertices = arena.nbr_vertices

            expected_arena = retrieve_expected_gpg_arena(file_path)

            self.assertEqual(arena.nbr_functions, len(expected_arena[1]))

            actual_vertices = set(arena.vertices)

            expected_vertices = set(expected_arena[0])

            self.assertEqual(expected_vertices, actual_vertices)

            for func in range(arena.nbr_functions):
                for priority, s in expected_arena[1][func].items():
                    actual_priority = set(arena.priorities[func][priority])

                    expected_priority = set(s)

                    self.assertEqual(expected_priority, actual_priority)

            for index in range(nbr_vertices):

                actual_successors = set(arena.successors[index])

                expected_successors = set(expected_arena[2][index])

                self.assertEqual(expected_successors, actual_successors)


if __name__ == '__main__':
    unittest.main()
