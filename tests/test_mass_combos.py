#!/usr/bin/env python
# encoding: utf-8
from pathlib import Path
import pandas as pd

import unimod_mapper


# test_dir = Path(unimod_mapper.__file__).parent.parent / "tests"
# package_dir = test_dir.parent


# def test_mass_to_combos():
#     # the order of the files shouldn't change the unimodIDs
#     um = unimod_mapper.UnimodMapper(add_default_files=False)
#     um._df = pd.DataFrame([
#         {"mono_mass": 0, "Name": "0"},
#         {"mono_mass": 1, "Name": "1"},
#         {"mono_mass": 2, "Name": "2"},
#         {"mono_mass": 3, "Name": "3"},
#         {"mono_mass": 4, "Name": "4"},
#         {"mono_mass": 5, "Name": "5"},
#         {"mono_mass": 6, "Name": "6"},
#         {"mono_mass": 7, "Name": "7"},
#     ])
#     combo_list = um.mass_to_combos(5, decimals=0)
#     assert len(combo_list) == 27


def test_mass_to_combos_0_decimal():
    # the order of the files shouldn't change the unimodIDs
    um = unimod_mapper.UnimodMapper()
    um._df = pd.DataFrame(
        [
            {"mono_mass": 0.4, "Name": "0.4"},
            {"mono_mass": 0.5, "Name": "0.5"},
            {"mono_mass": 0.7, "Name": "0.7"},
            {"mono_mass": 1.1, "Name": "1.1"},
            {"mono_mass": 1.4, "Name": "1.4"},
            {"mono_mass": 1.5, "Name": "1.5"},
        ]
    )
    combo_list = um.mass_to_combos(1, decimals=0)
    assert len(combo_list) == 6
    breakpoint()
    # a = [
    #     (0.8, ["0.4", "0.4"]),
    #     (0.9, ["0.4", "0.5"]),
    #     (1.0, ["0.5", "0.5"]),
    #     (1.1, ["0.4", "0.7"]),
    #     (1.2, ["0.5", "0.7"]),
    #     (1.4, ["0.7", "0.7"]),
    # ]


def test_mass_to_combos_1_decimal():
    # the order of the files shouldn't change the unimodIDs
    um = unimod_mapper.UnimodMapper()
    um._df = pd.DataFrame(
        [
            {"mono_mass": 0.34, "Name": "0.34"},
            {"mono_mass": 0.45, "Name": "0.45"},
            {"mono_mass": 0.60, "Name": "0.60"},
            {"mono_mass": 0.64, "Name": "0.64"},
            {"mono_mass": 0.45, "Name": "0.45"},
            {"mono_mass": 0.56, "Name": "0.56"},
            {"mono_mass": 0.67, "Name": "0.67"},
            {"mono_mass": 0.78, "Name": "0.78"},
        ]
    )
    combo_list = um.mass_to_combos(1, decimals=1)
    assert len(combo_list) == 3
    # a = [
    #     (0.98, ["0.34", "0.64"]),
    #     (1.01, ["0.34", "0.67"]),
    #     (1.01, ["0.45", "0.56"]),
    #     (1.01, ["0.45", "0.56"]),
    #     (1.04, ["0.45", "0.59"]),
    #     (1.04, ["0.59", "0.45"]),
    # ]


def test_mass_to_combos_1B_decimal():
    # the order of the files shouldn't change the unimodIDs
    um = unimod_mapper.UnimodMapper()
    um._df = pd.DataFrame(
        [
            {"mono_mass": 0.33, "Name": "0.33"},
            {"mono_mass": 0.45, "Name": "0.45"},
            {"mono_mass": 0.60, "Name": "0.60"},
            {"mono_mass": 0.64, "Name": "0.64"},
            {"mono_mass": 0.45, "Name": "0.45"},
            {"mono_mass": 0.56, "Name": "0.56"},
            {"mono_mass": 0.67, "Name": "0.67"},
            {"mono_mass": 0.78, "Name": "0.78"},
        ]
    )
    combo_list = um.mass_to_combos(1, decimals=2)
    assert len(combo_list) == 1
    # a = [
    #     (0.98, ["0.34", "0.64"]),
    #     (1.01, ["0.34", "0.67"]),
    #     (1.01, ["0.45", "0.56"]),
    #     (1.01, ["0.45", "0.56"]),
    #     (1.04, ["0.45", "0.59"]),
    #     (1.04, ["0.59", "0.45"]),
    # ]
