#!/usr/bin/env python
# encoding: utf-8

import unimod_mapper
import pytest

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
    {"function": M.id2mass, "cases": [{"in": {"args": ["9"]}, "out": 494.30142}]},  #
    {
        "function": M.id2composition,
        "cases": [
            {
                "in": {"args": ["9"]},
                "out": {"N": 4, "S": 1, "2H": 8, "O": 6, "C": 22, "H": 30},
            }  #
        ],
    },
    {"function": M.id2name, "cases": [{"in": {"args": "9"}, "out": "ICAT-G:2H(8)"}]},  #
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
        "function": M.name2specificity_site_list,
        "cases": [{"in": {"args": ["Ala->Gln"]}, "out": ["A"]}],  #
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


class TestXMLIntegrity:
    @pytest.mark.parametrize("conversion", CONVERSIONS)
    def test_conversion(self, conversion):
        for case in conversion["cases"]:
            assert case["out"] == conversion["function"](
                *case["in"].get("args", []), **case["in"].get("kwargs", {})
            )

        # def test_set_integirty_test():
        #     for test_id, list_of_test in enumerate(TESTS):
        #         yield input_list_check, list_of_test
        #
        # >>> I dont get this this ...
        #
        # def input_list_check(list_of_test):
        #     """
        #     Checks that the number of tests can actually be zipped
        #     with the unimodMapper functions
        #     """
        #     assert len(list_of_test) <= len(UNIMODMAPPER_FUNCTIONS)

        # def unimodMapper_conversion_test():
        #     for test_id, list_of_test in enumerate(TESTS):
        #         test_function_association = zip(list_of_test, UNIMODMAPPER_FUNCTIONS)
        #         for test_dict, mapper_function in test_function_association:
        #             if "kwargs" not in test_dict["in"].keys():
        #                 test_dict["in"]["kwargs"] = {}
        #             yield mapper_function_check, test_dict, mapper_function

        # def mapper_function_check(test_dict, mapper_function):
        #     mapper_output = mapper_function(
        #         *test_dict["in"]["args"], **test_dict["in"]["kwargs"]
        #     )
        #     print(mapper_output, test_dict["out"])
        #     assert mapper_output == test_dict["out"]

        # class TestResults(unittest.TestCase):
        #     def setUp(self):
        #         self.alt_mapper = pyqms.UnimodMapper()
        #         self.alt_mapper.unimod_xml_name = "wrong_unimod_xml_name.xml"

        #     def crash_test(self):
        #         with self.assertRaises(SystemExit) as system_exit_check:
        #             self.alt_mapper._parseXML()
        #         self.assertEqual(system_exit_check.exception.code, 1)


