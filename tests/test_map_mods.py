from unimod_mapper import UnimodMapper
import numpy as np

mod_dict = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
            },
            {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
            },
        ]
    },
}

mod_dict_not_in_unimod = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Yadailation",
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Yadailation",
            },
        ]
    },
}

mod_dict_id = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "id": 35,
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "id": 4,
            },
            {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "id": "1",
            },
        ]
    },
}

mod_dict_id_not_in_unimod = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "id": 987654321,
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "id": 123456789,
            },
        ]
    },
}

mod_dict_nl = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
                "neutral_loss": 0.0,
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "neutral_loss": "unimod",
            },
            {
                "aa": "M",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "neutral_loss": "unimod",
            },
        ]
    },
}

mod_dict_name_id = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
                "id": "35",
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "id": "4",
            },
            {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
                "id": "1",
            },
        ]
    },
}

mod_dict_name_wrong_id = {
    "ufiles": "",
    "parameters": {
        "modifications": [
            {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
                "id": "3567",
            },
            {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "id": "4567",
            },
            {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
                "id": "1",  # only this one is correct
            },
        ]
    },
}

unimod_dict = {
    "fix": [
        {
            "aa": "C",
            "position": "any",
            "name": "Carbamidomethyl",
            "mass": 57.021464,
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "id": "4",
            "neutral_loss": None,
            "_id": 1,
            "org": {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
            },
            "unimod": True,
        }
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "name": "Oxidation",
            "mass": 15.994915,
            "composition": {"O": 1},
            "id": "35",
            "neutral_loss": None,
            "_id": 0,
            "org": {"aa": "M", "type": "opt", "position": "any", "name": "Oxidation"},
            "unimod": True,
        },
        {
            "aa": "*",
            "position": "Prot-N-term",
            "name": "Acetyl",
            "mass": 42.010565,
            "composition": {"H": 2, "C": 2, "O": 1},
            "id": "1",
            "neutral_loss": None,
            "_id": 2,
            "org": {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
            },
            "unimod": True,
        },
    ],
}

unimod_dict_id = {
    "fix": [
        {
            "aa": "C",
            "position": "any",
            "name": "Carbamidomethyl",
            "mass": 57.021464,
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "id": "4",
            "neutral_loss": None,
            "_id": 1,
            "org": {"aa": "C", "type": "fix", "position": "any", "id": "4"},
            "unimod": True,
        }
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "name": "Oxidation",
            "mass": 15.994915,
            "composition": {"O": 1},
            "id": "35",
            "neutral_loss": None,
            "_id": 0,
            "org": {"aa": "M", "type": "opt", "position": "any", "id": "35"},
            "unimod": True,
        },
        {
            "aa": "*",
            "position": "Prot-N-term",
            "name": "Acetyl",
            "mass": 42.010565,
            "composition": {"H": 2, "C": 2, "O": 1},
            "id": "1",
            "neutral_loss": None,
            "_id": 2,
            "org": {"aa": "*", "type": "opt", "position": "Prot-N-term", "id": "1"},
            "unimod": True,
        },
    ],
}

unimod_dict_with_nl = {
    "fix": [
        {
            "aa": "C",
            "position": "any",
            "name": "Carbamidomethyl",
            "mass": 57.021464,
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "id": "4",
            "neutral_loss": 0.0,
            "_id": 1,
            "org": {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "neutral_loss": "unimod",
            },
            "unimod": True,
        },
        {
            "aa": "M",
            "position": "any",
            "name": "Carbamidomethyl",
            "mass": 57.021464,
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "id": "4",
            "neutral_loss": 105.024835,
            "_id": 2,
            "org": {
                "aa": "M",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "neutral_loss": "unimod",
            },
            "unimod": True,
        },
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "name": "Oxidation",
            "mass": 15.994915,
            "composition": {"O": 1},
            "id": "35",
            "neutral_loss": 0.0,
            "_id": 0,
            "org": {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
                "neutral_loss": 0.0,
            },
            "unimod": True,
        }
    ],
}

unimod_dict_name_id = {
    "fix": [
        {
            "aa": "C",
            "position": "any",
            "name": "Carbamidomethyl",
            "mass": 57.021464,
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "id": "4",
            "neutral_loss": None,
            "_id": 1,
            "org": {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "id": "4",
            },
            "unimod": True,
        }
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "name": "Oxidation",
            "mass": 15.994915,
            "composition": {"O": 1},
            "id": "35",
            "neutral_loss": None,
            "_id": 0,
            "org": {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
                "id": "35",
            },
            "unimod": True,
        },
        {
            "aa": "*",
            "position": "Prot-N-term",
            "name": "Acetyl",
            "mass": 42.010565,
            "composition": {"H": 2, "C": 2, "O": 1},
            "id": "1",
            "neutral_loss": None,
            "_id": 2,
            "org": {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
                "id": "1",
            },
            "unimod": True,
        },
    ],
}

unimod_dict_name_wrong_id = {
    "fix": [],
    "opt": [
        {
            "aa": "*",
            "position": "Prot-N-term",
            "name": "Acetyl",
            "mass": 42.010565,
            "composition": {"H": 2, "C": 2, "O": 1},
            "id": "1",
            "neutral_loss": None,
            "_id": 2,
            "org": {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
                "id": "1",
            },
            "unimod": True,
        }
    ],
}


def test_map_mods_by_name():
    _output = UnimodMapper().map_mods(mod_list=mod_dict["parameters"]["modifications"])
    assert _output == unimod_dict


def test_map_mods_by_name_mod_not_in_unimod():
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_not_in_unimod["parameters"]["modifications"]
    )
    assert _output == {"fix": [], "opt": []}


def test_map_mods_by_id():
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_id["parameters"]["modifications"]
    )
    assert _output == unimod_dict_id


def test_map_mods_mod_not_in_unimod_by_id():
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_id_not_in_unimod["parameters"]["modifications"]
    )
    assert _output == {"fix": [], "opt": []}


def test_map_mods_neutral_loss():
    import pprint

    pprint.pprint(mod_dict_nl["parameters"]["modifications"])
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_nl["parameters"]["modifications"]
    )
    print("Output")
    pprint.pprint(_output)
    print("Expected")
    pprint.pprint(unimod_dict_with_nl)
    assert _output == unimod_dict_with_nl


def test_map_mods_name_and_id():
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_name_id["parameters"]["modifications"]
    )
    assert _output == unimod_dict_name_id


def test_map_mods_name_and_wrong_id():
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_name_wrong_id["parameters"]["modifications"]
    )
    assert _output == unimod_dict_name_wrong_id


def test_map_TMTpro18():
    mapper = UnimodMapper()
    mapped = mapper.mass_to_names(304.207146, decimals=4)  # starts working from 3 on
    assert list(mapped) == ["TMTpro"]


# def test_map_all_masses():
#     mapper = UnimodMapper()
#     for mod_dict in mapper.data_list:
#         mono_mass = mod_dict["mono_mass"]
#         name = mod_dict["unimodname"]
#         mapped_name = mapper.mass_to_names(mono_mass, decimals=5)
#         assert name in list(mapped_name)


def test_map_mod_chemical_composition():
    mapper = UnimodMapper()
    mod_list = [
        {
            "aa": "M",  # specify the modified amino acid as a single letter, use '*' if the amino acid is variable
            "type": "opt",  # specify if it is a fixed (fix) or potential (opt) modification
            "position": "any",  # specify the position within the protein/peptide (Prot-N-term, Prot-C-term), use 'any' if the positon is variable
            "name": "Oxidation",  # specify the unimod PSI-MS Name (alternative to id)
            "id": None,  # specify the unimod Accession (alternative to name)
            "composition": None,  # For user-defined mods composition needs to be given as a Hill notation
        },
        {
            "aa": "T",
            "type": "fix",
            "name": "Acetyl",
        },
    ]
    # print(mapper.df.loc[0])

    rdict = mapper.map_mods(mod_list)
    # print(rdict)
    # assert 2 == 1
    assert rdict["opt"][0]["composition"] == {"O": 1}
    assert rdict["fix"][0]["composition"] == {"C": 2, "H": 2, "O": 1}
    assert rdict["fix"][0]["name"] == "Acetyl"
