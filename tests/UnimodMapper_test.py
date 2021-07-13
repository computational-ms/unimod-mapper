#!/usr/bin/env python
# encoding: utf-8
import os
import sys
from pathlib import Path
import pytest

# this block is not needed anymore, when we have a proper package
test_dir = Path(__file__).parent
package_dir = test_dir.parent
sys.path.append(package_dir)
# EOBlock
import unimod_mapper

unimod_path = package_dir.joinpath("unimod_mapper", "unimod.xml")
usermod_path = test_dir.joinpath("usermod.xml")
M = unimod_mapper.UnimodMapper(xml_file_list=[unimod_path, usermod_path, unimod_path])

CONVERSIONS = [
    {
        "function": M.name2mass_list,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": [494.30142, 494.30142]}],
    },
    {
        "function": M.name2first_mass,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": 494.30142}],
    },
    {
        "function": M.name2composition_list,
        "cases": [
            {
                "in": {"args": ["ICAT-G:2H(8)"]},
                "out": [
                    {"H": 30, "C": 22, "O": 6, "S": 1, "2H": 8, "N": 4},
                    {"H": 30, "C": 22, "O": 6, "S": 1, "2H": 8, "N": 4},
                ],
            }
        ],
    },
    {
        "function": M.name2first_composition,
        "cases": [
            {
                "in": {"args": ["ICAT-G:2H(8)"]},
                "out": {"H": 30, "C": 22, "O": 6, "S": 1, "2H": 8, "N": 4},
            }
        ],
    },
    {
        "function": M.name2id_list,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": ["8", "1514"]}],  #
    },
    {
        "function": M.name2first_id,
        "cases": [{"in": {"args": ["ICAT-G:2H(8)"]}, "out": "8"}],  #
    },
    {
        "function": M.id2mass,
        "cases": [
            {"in": {"args": ["8"]}, "out": 494.30142},
            {"in": {"args": [8]}, "out": 494.30142},
        ],
    },  #
    {
        "function": M.id2composition,
        "cases": [
            {
                "in": {"args": ["8"]},
                "out": {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
            },
            {
                "in": {"args": [8]},
                "out": {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
            },  #
        ],
    },
    {
        "function": M.id2name,
        "cases": [
            {"in": {"args": ["8"]}, "out": "ICAT-G:2H(8)"},
            {"in": {"args": [8]}, "out": "ICAT-G:2H(8)"},
        ],
    },  #
    {
        "function": M.mass2name_list,
        "cases": [
            {"in": {"args": [494.30142]}, "out": ["ICAT-G:2H(8)", "ICAT-G:2H(8)"]}
        ],  #
    },
    {
        "function": M.mass2id_list,
        "cases": [{"in": {"args": [494.30142]}, "out": ["8", "1514"]}],  #
    },
    {
        "function": M.mass2composition_list,
        "cases": [
            {
                "in": {"args": [494.30142]},
                "out": [
                    {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
                    {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
                ],
            }  #
        ],
    },
    {
        "function": M.appMass2id_list,
        "cases": [
            {
                "in": {"args": [18], "kwargs": {"decimal_places": 0}},
                "out": [
                    "99",
                    "134",
                    "414",
                    "713",
                    "799",
                    "1413",
                    "1605",
                    "1640",
                    "1920",
                    "2219",
                    "2305",
                    "2919",
                ],
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
        "cases": [
            {"in": {"args": ["C(22)H(30)2H(8)N(4)O(6)S(1)"]}, "out": ["8", "1514"]}
        ],  #
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
        "order": [unimod_path, usermod_path],
        "cases": [
            {"in": "TMTpro", "out": ["1484", "1499"]},
            {"in": "SILAC K+6 TMT", "out": ["1486"]},
            {"in": "ICAT-G:2H(8)", "out": ["8"]},
        ],
    },
    {
        "order": [usermod_path, unimod_path],
        "cases": [
            {"in": "TMTpro", "out": ["13", "1504"]},
            {"in": "SILAC K+6 TMT", "out": ["0"]},
            {"in": "ICAT-G:2H(8)", "out": ["28"]},
        ],
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
        xml_file = test_dir.joinpath("test_only_unimod.xml")
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
            um = unimod_mapper.UnimodMapper(xml_file_list=data["order"])
            for case in data["cases"]:
                assert case["out"] == um.name2id_list(case["in"])
