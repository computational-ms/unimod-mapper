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


def test_map_composition_to_names():
    mapper = UnimodMapper()
    mapped = mapper.composition_to_names({"C": 1, "O": 1})
    assert list(mapped) == ["Formyl", "Ser->Asp", "Thr->Glu"]


def test_map_composition_to_ids():
    mapper = UnimodMapper()
    mapped = mapper.composition_to_ids({"C": 1, "O": 1})
    assert list(mapped) == ["122", "1196", "1205"]


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

    rdict = mapper.map_mods(mod_list)

    assert rdict["opt"][0]["composition"] == {"O": 1}
    assert rdict["fix"][0]["composition"] == {"C": 2, "H": 2, "O": 1}
    assert rdict["fix"][0]["id"] == "1"


def test_map_mod_userdefined_compositions():
    mapper = UnimodMapper()
    mod_list = [
        {
            "aa": "M",  # specify the modified amino acid as a single letter, use '*' if the amino acid is variable
            "type": "opt",  # specify if it is a fixed (fix) or potential (opt) modification
            "position": "any",  # specify the position within the protein/peptide (Prot-N-term, Prot-C-term), use 'any' if the positon is variable
            "name": "TheOneAndOnly",  # specify the unimod PSI-MS Name (alternative to id)
            "composition": {
                "H": 2,
                "O": 1,
            },  # For user-defined mods composition needs to be given as a Hill notation
        },
    ]

    rdict = mapper.map_mods(mod_list)
    assert (
        len(rdict["opt"]) == 0
    )  # cause the name is not a unimod mod, but the composition exists already

    mod_list = [
        {
            "aa": "M",  # specify the modified amino acid as a single letter, use '*' if the amino acid is variable
            "type": "opt",  # specify if it is a fixed (fix) or potential (opt) modification
            "position": "any",  # specify the position within the protein/peptide (Prot-N-term, Prot-C-term), use 'any' if the positon is variable
            "name": "TheOneAndOnly",  # specify the unimod PSI-MS Name (alternative to id)
            "composition": {
                "H": 222,
                "O": 111,
            },  # For user-defined mods composition needs to be given as a Hill notation
        },
    ]

    rdict = mapper.map_mods(mod_list)

    assert rdict["opt"][0]["composition"] == {"H": 222, "O": 111}
    assert rdict["opt"][0]["name"] == "TheOneAndOnly"


def test_map_mod_chemical_composition_fails():
    mapper = UnimodMapper()

    # Using PSI-MS name works
    mod_list = [
        {
            "aa": "N",
            "type": "opt",
            "name": "Ammonia-loss",
        },
    ]
    rdict = mapper.map_mods(mod_list)
    assert rdict["opt"][0]["name"] == "Ammonia-loss"

    # Using Interim name for same ID doesn't work
    mod_list = [
        {
            "aa": "D",
            "type": "opt",
            "name": "N-oxobutanoic",
        },
    ]
    rdict = mapper.map_mods(mod_list)
    assert len(rdict["opt"]) == 0

    # Using Interim name and ID doesn't work (cause name is checked first)
    # But using a wrong ID but correct name works (see test_map_mods_name_and_wrong_id)
    # Seems inconsistent
    mod_list = [
        {
            "aa": "D",
            "type": "opt",
            "name": "N-oxobutanoic",
            "id": 385,
        },
    ]
    rdict = mapper.map_mods(mod_list)
    assert len(rdict["opt"]) == 0

    # Using just ID works
    mod_list = [
        {
            "aa": "D",
            "type": "opt",
            "id": 385,
        },
    ]
    rdict = mapper.map_mods(mod_list)
    assert rdict["opt"][0]["name"] == "Ammonia-loss"

    # Using Interim name if PSI MS name doesn't exist works
    mod_list = [
        {
            "aa": "S",
            "type": "opt",
            "name": "Galactosyl",
        },
    ]
    rdict = mapper.map_mods(mod_list)
    assert rdict["opt"][0]["composition"] == {"C": 6, "H": 10, "O": 6}


def test_read_mapped_mods(self):
    mapper = UnimodMapper()

    mod_list = [
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
    rdict = mapper.map_mods(mod_list)
    df = mapper.read_mapped_mods_as_df(rdict)
    assert len(df) == 3
    assert df["Accession"].to_list() == ["4", "35", "1"]
