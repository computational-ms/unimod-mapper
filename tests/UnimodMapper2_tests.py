#!/usr/bin/env python
# encoding: utf-8
import os
import sys

import pytest

# this block is not needed anymore, when we have a proper package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
# EOBlock
import unimod_mapper


M = unimod_mapper.UnimodMapper()

CONVERSIONS = [
    {
        "function": M.name_to_mass,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": [494.30142]}],
    },
    {
        "function": M.name_to_composition,
        "cases": [
            {
                "in": {"args": ["ICAT-G:2H(8)"]},
                "out": [{"H": 30, "C": 22, "O": 6, "S": 1, "2H": 8, "N": 4}],
            }
        ],
    },
    {
        "function": M.name_to_id,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": ["9"]}],  #
    },
    {
        "function": M.id_to_mass,
        "cases": [
            {"in": {"args": ["9"]}, "out": [494.30142]},
        ],
    },
    {
        "function": M.id_to_composition,
        "cases": [
            {
                "in": {"args": ["9"]},
                "out": [{"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30}],
            },
        ],
    },
    {
        "function": M.id_to_name,
        "cases": [
            {"in": {"args": ["9"]}, "out": ["ICAT-G:2H(8)"]},
        ],
    },
    {
        "function": M.mass_to_ids,
        "cases": [
            {
                "in": {"args": [18], "kwargs": {"decimals": 1}},
                "out": ["127", "329", "608", "1079", "1167", "1922"],
            },
            {
                "in": {"args": [9.030], "kwargs": {"decimals": 2}},
                "out": ["184", "1100"],
            },
            {
                "in": {"args": [9.030], "kwargs": {"decimals": 3}},
                "out": ["184"],
            },
        ],
    },
    # {
    #     "function": M.mass_to_compositions,
    #     "cases": [
    #         {
    #             "in": {"args": [9.030], "kwargs": {"decimals": 2}},
    #             "out": [
    #                 {"C": -9, "13C": 9},
    #                 {"H": 3, "C": -3, "N": 3},
    #             ],
    #         }  #
    #     ],
    # },
    {
        "function": M.appMass2name_list,
        "cases": [
            {
                "in": {"args": [18], "kwargs": {"decimal_places": 1}},
                "out": [
                    "Fluoro",
                    "Methyl:2H(3)13C(1)",
                    "Xle->Met",
                    "Glu->Phe",
                    "Pro->Asp",
                    "Pro->HAVA",
                ],
            }  #
        ],
    },
]


@pytest.mark.parametrize("conversion", CONVERSIONS)
def test_conversion_using_query(conversion):
    for case in conversion["cases"]:
        converted = conversion["function"](
            *case["in"].get("args", []), **case["in"].get("kwargs", {})
        )
        print(converted, type(converted))
        assert case["out"] == converted
