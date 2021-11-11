#!/usr/bin/env python
# encoding: utf-8
from pathlib import Path
import pytest

import unimod_mapper


# test_dir = Path(unimod_mapper.__file__).parent.parent / "tests"
# package_dir = test_dir.parent


# def test_mass_to_combos():
#     # the order of the files shouldn't change the unimodIDs
#     um = unimod_mapper.UnimodMapper(add_default_files=False)
#     um._data_list = [
#         {"mono_mass": 0, "unimodname": "0"},
#         {"mono_mass": 1, "unimodname": "1"},
#         {"mono_mass": 2, "unimodname": "2"},
#         {"mono_mass": 3, "unimodname": "3"},
#         {"mono_mass": 4, "unimodname": "4"},
#         {"mono_mass": 5, "unimodname": "5"},
#         {"mono_mass": 6, "unimodname": "6"},
#         {"mono_mass": 7, "unimodname": "7"},
#     ]
#     combo_list = um.mass_to_combos(5, decimals=0)
#     assert len(combo_list) == 27


def test_mass_to_combos_1_decimal():
    # the order of the files shouldn't change the unimodIDs
    um = unimod_mapper.UnimodMapper(add_default_files=False)
    um._data_list = [
        {"mono_mass": 0.4, "unimodname": "0.4"},
        {"mono_mass": 0.5, "unimodname": "0.5"},
        {"mono_mass": 0.7, "unimodname": "0.7"},
        {"mono_mass": 1.1, "unimodname": "1.1"},
        {"mono_mass": 1.4, "unimodname": "1.4"},
        {"mono_mass": 1.5, "unimodname": "1.5"},
    ]
    combo_list = um.mass_to_combos(1, decimals=1)
    assert len(combo_list) == 6
    # a = [
    #     (0.8, ["0.4", "0.4"]),
    #     (0.9, ["0.4", "0.5"]),
    #     (1.0, ["0.5", "0.5"]),
    #     (1.1, ["0.4", "0.7"]),
    #     (1.2, ["0.5", "0.7"]),
    #     (1.4, ["0.7", "0.7"]),
    # ]


def test_mass_to_combos_2_decimal():
    # the order of the files shouldn't change the unimodIDs
    um = unimod_mapper.UnimodMapper(add_default_files=False)
    um._data_list = [
        {"mono_mass": 0.25, "unimodname": "0.25"},
        {"mono_mass": 0.4, "unimodname": "0.4"},
        {"mono_mass": 0.48, "unimodname": "0.48"},
        {"mono_mass": 0.5, "unimodname": "0.5"},
        {"mono_mass": 0.7, "unimodname": "0.7"},
        {"mono_mass": 1.1, "unimodname": "1.1"},
        {"mono_mass": 1.4, "unimodname": "1.4"},
        {"mono_mass": 1.5, "unimodname": "1.5"},
    ]
    combo_list = um.mass_to_combos(1, decimals=2)
    assert len(combo_list) == 4
    # a = [(0.95, ['0.25', '0.7']), (0.96, ['0.48', '0.48']), (0.98, ['0.48', '0.5']), (1.0, ['0.5', '0.5'])]
