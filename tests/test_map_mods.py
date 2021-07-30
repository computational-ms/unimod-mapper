from unimod_mapper import UnimodMapper

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
                "id": 1,
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

unimod_dict = {
    "fix": [
        {
            "aa": "C",
            "position": "any",
            "name": "Carbamidomethyl",
            "_id": 1,
            "mass": 57.021464,
            "pos": "any",
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "org": {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
            },
            "id": "4",
            "unimod": True,
        }
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "name": "Oxidation",
            "_id": 0,
            "mass": 15.994915,
            "pos": "any",
            "composition": {"O": 1},
            "org": {"aa": "M", "type": "opt", "position": "any", "name": "Oxidation"},
            "id": "35",
            "unimod": True,
        },
        {
            "aa": "*",
            "position": "Prot-N-term",
            "name": "Acetyl",
            "_id": 2,
            "mass": 42.010565,
            "pos": "Prot-N-term",
            "composition": {"H": 2, "C": 2, "O": 1},
            "org": {
                "aa": "*",
                "type": "opt",
                "position": "Prot-N-term",
                "name": "Acetyl",
            },
            "id": "1",
            "unimod": True,
        },
    ],
}


unimod_dict_id = {
    "fix": [
        {
            "aa": "C",
            "position": "any",
            "id": 4,
            "_id": 1,
            "mass": 57.021464,
            "pos": "any",
            "name": "Carbamidomethyl",
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "org": {"aa": "C", "type": "fix", "position": "any", "id": 4},
            "unimod": True,
        }
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "id": 35,
            "_id": 0,
            "mass": 15.994915,
            "pos": "any",
            "name": "Oxidation",
            "composition": {"O": 1},
            "org": {"aa": "M", "type": "opt", "position": "any", "id": 35},
            "unimod": True,
        },
        {
            "aa": "*",
            "position": "Prot-N-term",
            "id": 1,
            "_id": 2,
            "mass": 42.010565,
            "pos": "Prot-N-term",
            "name": "Acetyl",
            "composition": {"H": 2, "C": 2, "O": 1},
            "org": {"aa": "*", "type": "opt", "position": "Prot-N-term", "id": 1},
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
            "neutral_loss": [],
            "_id": 1,
            "mass": 57.021464,
            "pos": "any",
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "org": {
                "aa": "C",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "neutral_loss": "unimod",
            },
            "id": "4",
            "unimod": True,
        },
        {
            "aa": "M",
            "position": "any",
            "name": "Carbamidomethyl",
            "neutral_loss": "105.024835",
            "_id": 2,
            "mass": 57.021464,
            "pos": "any",
            "composition": {"H": 3, "C": 2, "N": 1, "O": 1},
            "org": {
                "aa": "M",
                "type": "fix",
                "position": "any",
                "name": "Carbamidomethyl",
                "neutral_loss": "unimod",
            },
            "id": "4",
            "unimod": True,
        },
    ],
    "opt": [
        {
            "aa": "M",
            "position": "any",
            "name": "Oxidation",
            "neutral_loss": 0.0,
            "_id": 0,
            "mass": 15.994915,
            "pos": "any",
            "composition": {"O": 1},
            "org": {
                "aa": "M",
                "type": "opt",
                "position": "any",
                "name": "Oxidation",
                "neutral_loss": 0.0,
            },
            "id": "35",
            "unimod": True,
        }
    ],
}


def test_unode_map_mods():
    # unode = ursgal.unodes["all"]["test_node_v1"]
    # _output = unode.map_mods(mod_list=mod_dict["parameters"]["modifications"])
    _output = UnimodMapper().map_mods(mod_list=mod_dict["parameters"]["modifications"])
    assert _output == unimod_dict


def test_unode_map_mods_mod_not_in_unimod():
    # unode = ursgal.unodes["all"]["test_node_v1"]
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_not_in_unimod["parameters"]["modifications"]
    )
    assert _output == {"fix": [], "opt": []}


def test_unode_map_mods_by_id():
    # unode = ursgal.unodes["all"]["test_node_v1"]
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_id["parameters"]["modifications"]
    )
    assert _output == unimod_dict_id


def test_unode_map_mods_mod_not_in_unimod_by_id():
    # unode = ursgal.unodes["all"]["test_node_v1"]
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_id_not_in_unimod["parameters"]["modifications"]
    )
    assert _output == {"fix": [], "opt": []}


def test_unode_map_mods_nl():
    # unode = ursgal.unodes["all"]["test_node_v1"]
    # _output = unode.map_mods(mod_list=mod_dict["parameters"]["modifications"])
    _output = UnimodMapper().map_mods(
        mod_list=mod_dict_nl["parameters"]["modifications"]
    )
    assert _output == unimod_dict_with_nl
