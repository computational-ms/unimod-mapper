#!/usr/bin/env python
# encoding: utf-8
import os
import sys
from pathlib import Path
import pytest

# this block is not needed anymore, when we have a proper package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
# EOBlock
import unimod_mapper


M = unimod_mapper.UnimodMapper()

CONVERSIONS = [
    {
        "function": M.name2mass,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": 494.30142}],
    },
    {
        "function": M.name2composition,
        "cases": [
            {
                "in": {"args": ["ICAT-G:2H(8)"]},
                "out": {"H": 30, "C": 22, "O": 6, "S": 1, "2H": 8, "N": 4},
            }  # pyqms.UnimodMapper.name2composition,
        ],
    },
    {
        "function": M.name2id,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": "9"}],  #
    },
    {
        "function": M.id2mass,
        "cases": [
            {"in": {"args": ["9"]}, "out": 494.30142},
            {"in": {"args": [9]}, "out": 494.30142},
        ],
    },  #
    {
        "function": M.id2composition,
        "cases": [
            {
                "in": {"args": ["9"]},
                "out": {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
            },
            {
                "in": {"args": [9]},
                "out": {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
            },  #
        ],
    },
    {
        "function": M.id2name,
        "cases": [
            {"in": {"args": ["9"]}, "out": "ICAT-G:2H(8)"},
            {"in": {"args": [9]}, "out": "ICAT-G:2H(8)"},
        ],
    },  #
    {
        "function": M.mass2name_list,
        "cases": [{"in": {"args": [494.30142]}, "out": ["ICAT-G:2H(8)"]}],  #
    },
    {
        "function": M.mass2id_list,
        "cases": [{"in": {"args": [494.30142]}, "out": ["9"]}],  #
    },
    {
        "function": M.mass2composition_list,
        "cases": [
            {
                "in": {"args": [494.30142]},
                "out": [{"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30}],
            }  #
        ],
    },
    {
        "function": M.appMass2id_list,
        "cases": [
            {
                "in": {"args": [18], "kwargs": {"decimal_places": 0}},
                "out": ["127", "329", "608", "1079", "1167", "1922"],
            }  #
        ],
    },
    {
        "function": M.appMass2element_list,
        "cases": [
            {
                "in": {"args": [18], "kwargs": {"decimal_places": 0}},
                "out": [
                    {"F": 1, "H": -1},
                    {"13C": 1, "H": -1, "2H": 3},
                    {"H": -2, "C": -1, "S": 1},
                    {"H": 2, "C": 4, "O": -2},
                    {"H": -2, "C": -1, "O": 2},
                    {"H": 2, "O": 1},
                ],
            }  #
        ],
    },
    {
        "function": M.appMass2name_list,
        "cases": [
            {
                "in": {"args": [18], "kwargs": {"decimal_places": 0}},
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
    {
        "function": M.composition2name_list,
        "cases": [
            {
                "in": {"args": ["C(2)H(3)N(1)O(1)"]},
                "out": ["Carbamidomethyl", "Ala->Gln", "Gly->Asn", "Gly"],
            }
        ],
    },
    {
        "function": M.name2specificity_list,
        "cases": [{"in": {"args": ["Ala->Gln"]}, "out": [("A", "AA substitution")]}],  #
    },
    {
        "function": M.composition2id_list,
        "cases": [{"in": {"args": ["C(22)H(30)2H(8)N(4)O(6)S(1)"]}, "out": ["9"]}],  #
    },
    {
        "function": M.composition2mass,
        "cases": [
            {"in": {"args": ["C(22)H(30)2H(8)N(4)O(6)S(1)"]}, "out": 494.30142}  #
        ],
    },
    {
        "function": M._map_key_2_index_2_value,
        "cases": [{"in": {"args": ["ThisKeyIsNotPresent", "mass"]}, "out": None}],  #
    },
]

MULTIFILE_TESTS = [
    {
        "order": ["unimod.xml", "usermod.xml"],
        "cases": [
            {"in": "TMTpro", "out": "2016"},
            {"in": "SILAC K+6 TMT", "out": "10000"},
            {"in": "ICAT-G:2H(8)", "out": "9"},
        ]
    },
    {
        "order": ["usermod.xml", "unimod.xml"],
        "cases": [
            {"in": "TMTpro", "out": "10013"},
            {"in": "SILAC K+6 TMT", "out": "10000"},
            {"in": "ICAT-G:2H(8)", "out": "9"},
        ]
    },
]

class TestXMLIntegrity:
    @pytest.mark.parametrize("conversion", CONVERSIONS)
    def test_conversion(self, conversion):
        for case in conversion["cases"]:
            assert case["out"] == conversion["function"](
                *case["in"].get("args", []), **case["in"].get("kwargs", {})
            )

        #     def crash_test(self):
        #         with self.assertRaises(SystemExit) as system_exit_check:
        #             self.alt_mapper._parseXML()
        #         self.assertEqual(system_exit_check.exception.code, 1)

    def test_write(self):
        xml_file = Path(__file__).parent.joinpath("test_only_unimod.xml")
        if xml_file.exists():
            xml_file.unlink()
        assert xml_file.exists() is False
        mod_dict = {
            "mass": 1337.42,
            "name": "GnomeChompski",
            "composition": {"L": 4, "D": 2},
        }
        M.writeXML(mod_dict, xml_file=xml_file)
        assert os.path.exists(xml_file)
        assert M.mass2name_list(1337.42) == ["GnomeChompski"]
        xml_file.unlink()

    def test_read_multiple_unimod_files(self):
        for data in MULTIFILE_TESTS:
            path_list = [Path(__file__).parent.parent.joinpath("unimod_mapper", x) for x in data["order"]]
            um = unimod_mapper.UnimodMapper(xml_file_list=path_list)
            for case in data["cases"]:
                assert case["out"] == um.name2id(case["in"])
