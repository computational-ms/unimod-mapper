#!/usr/bin/env python
# encoding: utf-8
"""
    Unimod Mapper
    -------------

    Python module to interface unimod.xml

    :license: MIT, see LICENSE.txt for more details

    Authors:

        * Leufken, J.
        * Schulze, S.
        * Koesters, M.
        * Fufezan, C.

"""
import sys
import os
import codecs
import xml.etree.ElementTree as ET
import xml.dom.minidom as xmldom
import requests

import bisect
import numpy as np
import itertools
import pandas as pd

from pathlib import Path
from loguru import logger

# define the url from where unimod.xml file should be retrieved
url = "http://www.unimod.org/xml/unimod.xml"


class UnimodMapper(object):
    """
    UnimodMapper class that creates lookup to the unimod.xml offering several helper methods.

    Mapping from e.g. name to composition or unimod ID to mass is possible.

    Please refer to `unimod`_ for further informations on modifications
    including naming, formulas, masses etc.

    .. _unimod:
        http://www.unimod.org/modifications_list.php?

    """

    def deprecated(function):
        def wrapper_deprecation_warning(*args, **kwargs):
            old_fn_name = function.__name__
            new_fn_name = function.__name__.replace("2", "_to_").replace("_list", "")
            logger.warning(f"{old_fn_name} is deprecated, please use {new_fn_name}")
            return function(*args, **kwargs)

        return wrapper_deprecation_warning

    def __init__(self, refresh_xml=False, xml_file_list=None, add_default_files=True):
        """Initialize mapper.

        Args:
            refresh_xml (bool, optional): Force fresh download of unimod.xml
            xml_file_list (None, optional): list of user unimod xml files
            add_default_files (bool, optional): Add default unimod files
        """
        if xml_file_list is None:
            xml_file_list = []
        self._data_list = None
        self._mapper = None
        self._df = None
        self._elements = []
        self._combos = {}

        # Check if unimod.xml file exists & if not reset refresh_xml flag
        full_path = Path(__file__).parent / "unimod.xml"
        if full_path.exists() is False:
            refresh_xml = True

        if refresh_xml is True:
            response = requests.get(url)
            with open(full_path, "wb") as file:
                file.write(response.content)

        self.unimod_xml_names = xml_file_list.copy()
        if add_default_files is True:
            names = [x.name for x in xml_file_list]
            for xml in ["usermod.xml", "unimod.xml"]:
                if xml not in names:
                    self.unimod_xml_names.append(Path(__file__).parent.joinpath(xml))

    @property
    def data_list(self):
        """Get list of unimods."""
        if self._data_list is None:
            self._data_list = self._parseXML(xml_file_list=self.unimod_xml_names)
        return self._data_list

    @data_list.setter
    def data_list(self, data_list):
        """Set list of unimods."""
        self._data_list = data_list
        return

    @property
    def mapper(self):
        """Get mapping dict."""
        if self._mapper is None:
            self._mapper = self._initialize_mapper()
        return self._mapper

    @mapper.setter
    def mapper(self, mapper):
        """Set mapping dict.

        Args:
            mapper (dict): new mapping
        """
        self._mapper = mapper
        return

    @property
    def df(self):
        """Return unimod df.

        Returns:
            pd.DataFrame: unimod table
        """
        if self._df is None:
            self._df = pd.DataFrame(self._parse_in_more_detail_XML())
            self._df = self._df.explode("specificity").reset_index(drop=True)
            sites = self._df.specificity.str.split("<\|>", expand=True)
            sites.columns = [
                "Site",
                "Classification",
                "neutral_loss_elements",
                "neutral_losses",
            ]
            self._df.drop(columns=["specificity"], inplace=True)
            self._df = self._df.join(sites)
            self._df.neutral_losses.fillna(0, inplace=True)
            self._df = self._df.convert_dtypes(convert_floating=False)
            self._df.neutral_losses = self._df.neutral_losses.astype(float)
        return self._df

    def query(self, query_string):
        """Query the dataframe with a pandas style query

        Args:
            query_string (str): Description

        Returns:
            pd.DataFrame: filtered DataFrame
        """
        return self.df.query(query_string)

    def name_to_mass(self, name):
        """Get mass for a given name

        Args:
            name (str): name of the unimod

        Returns:
            list: list of masses
        """
        return self.df.query("`Name` == @name")["mono_mass"].to_list()

    def name_to_composition(self, name):
        """Get composition for a given name

        Args:
            name (str): name of the unimod

        Returns:
            list: list of compositions
        """
        return self.df.query("`Name` == @name")["elements"].to_list()

    def name_to_neutral_loss(self, name):
        """Get neutral loss for a given name

        Args:
            name (str): name of the unimod

        Returns:
            list: list of neutral losses
        """
        return (
            self.df.query("`Name` == @name")[["Site", "neutral_losses"]]
            .to_numpy()
            .tolist()
        )

    def name_to_id(self, name):
        """Get unimod ids for a given name

        Args:
            name (str): name of the unimod

        Returns:
            list: list of unimod ids
        """
        return self.df.query("`Name` == @name")["Accession"].to_list()

    def id_to_mass(self, id):
        """Get mass for a given id

        Args:
            name (str): id of the unimod

        Returns:
            list: list of masses
        """
        return self.df.query("`Accession` == @id")["mono_mass"].to_list()

    def id_to_composition(self, id):
        """Get composition for a given id

        Args:
            name (str): id of the unimod

        Returns:
            list: list of compositions
        """
        return self.df.query("`Accession` == @id")["elements"].to_list()

    def id_to_name(self, id):
        """Get name for a given id

        Args:
            name (str): id of the unimod

        Returns:
            list: list of names
        """
        return self.df.query("`Accession` == @id")["Name"].to_list()

    def _determine_mass_range(self, mass, decimals=5):
        fraction = 1 / 10 ** (decimals + 1)
        lower_mass = mass - 5 * fraction
        upper_mass = mass + 4 * fraction
        return lower_mass, upper_mass

    def mass_to_ids(self, mass, decimals=5):
        """Get ids for a given mass

        Args:
            name (str): mass of the unimod

        Returns:
            list: list of ids
        """
        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)
        return self.df.query("@lower_mass <= `mono_mass` <= @upper_mass")[
            "Accession"
        ].unique()

    def mass_to_compositions(self, mass, decimals=5):
        """Get compositions for a given mass

        Args:
            name (float|int): mass of the unimod

        Returns:
            list: list of compositons
        """
        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)
        return self.df.query("@lower_mass <= `mono_mass` <= @upper_mass")[
            "elements"
        ].tolist()

    def mass_to_names(self, mass, decimals=5):
        """Get names for a given mass

        Args:
            name (float|int): mass of the unimod

        Returns:
            list: list of names
        """
        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)
        return self.df.query("@lower_mass <= `mono_mass` <= @upper_mass")[
            "Name"
        ].unique()

    def mass_to_combos(self, mass, n=2, decimals=5):
        """Generate all combos of length n rounded to `decimals` decimal places

        Args:
            mass (float|int): combined mass
            n (int, optional): number of allowed mods to form the combined mass
            decimals (int, optional): round to n decimal places

        Returns:
            list: list of tuples containing the combined and single masses
        """
        if n not in self._combos.keys():
            self._combos[n] = self._generate_mass_combos(n=n)

        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)

        lower_index = bisect.bisect_left(
            [x[0] for x in self._combos[n]],
            lower_mass,
        )

        upper_index = bisect.bisect_right(
            [x[0] for x in self._combos[n]],
            upper_mass,
        )
        return self._combos[n][lower_index:upper_index]

    def composition_to_names(self, composition):
        """Get names for a given composition

        Args:
            composition (dict): chemical composition dict

        Returns:
            list: list of names
        """
        composition = dict(sorted(list(composition.items())))
        return list(self.df.query("`elements` == @composition")["Name"].unique())

    def composition_to_ids(self, composition):
        """Get ids for a given composition

        Args:
            composition (dict): chemical composition dict

        Returns:
            list: list of ids
        """
        composition = dict(sorted(list(composition.items())))
        return list(self.df.query("`elements` == @composition")["Accession"].unique())

    def composition_to_mass(self, composition):
        """Get mass for a given composition

        Args:
            composition (dict): chemical composition dict

        Returns:
            float: mass
        """
        composition = dict(sorted(list(composition.items())))
        masses = list(self.df.query("`elements` == @composition")["mono_mass"].unique())
        if len(masses) > 1:
            print(f"The Composition {composition} points to {masses} - Seriously!!")
            raise TypeError("We seriously have a problem with this XML")
        elif len(masses) == 0:
            return None
        else:
            return masses[0]

    def _generate_mass_combos(self, n=2):
        """Generate all mass combos of length n

        Args:
            n (int, optional): number of combinated mods

        Returns:
            list: list of tuples with combined and single masses
        """
        mass_list = []
        for combo in itertools.combinations_with_replacement(
            self.df[["mono_mass", "Name"]].drop_duplicates().to_numpy(), 2
        ):

            combo_mass = np.sum(np.fromiter((c[0] for c in combo), float))
            combo_name = [c[1] for c in combo]
            mass_list.append((combo_mass, combo_name))
        return sorted(mass_list)

    def _extract_elements(self, element):
        """Extract xml elements with the name 'element'.

        Args:
            element (xml.etree.ElementTree.Element): xml element

        Returns:
            dict: dict mapping symbol to number
        """
        r_dict = {}
        for sub_element in element.iter():
            if sub_element.tag.endswith("}element"):
                number = int(sub_element.attrib["number"])
                if number != 0:
                    r_dict[sub_element.attrib["symbol"]] = number
        r_dict = dict(sorted(list(r_dict.items())))
        return r_dict

    def _parse_in_more_detail_XML(self):
        """Parse unimod xml.

        Returns:
            list: list of dicts with information regarding a unimod
        """
        data_list = []
        for xml_path in self.unimod_xml_names:
            xml_path = Path(xml_path)
            if os.path.exists(xml_path) is False:
                logger.warning(f"{xml_path} does not exist")
                continue

            logger.info("Parsing mod xml file ({0})".format(xml_path))
            unimodXML = ET.iterparse(
                codecs.open(xml_path, "r", encoding="utf8"),
                events=(b"start", b"end"),
            )
            for event, element in unimodXML:
                if event == b"start":
                    if element.tag.endswith("}mod"):
                        tmp = {
                            "Name": element.attrib["title"],
                            "Accession": str(element.attrib.get("record_id", "")),
                            "Description": element.attrib.get("full_name", ""),
                            "elements": {},
                            "specificity": [],
                            "PSI-MS approved": False,
                        }
                        if element.attrib.get("approved", "0") == "1":
                            tmp["PSI-MS approved"] = True
                            tmp["PSI-MS Name"] = element.attrib["title"]
                    elif element.tag.endswith("}delta"):
                        tmp["mono_mass"] = float(element.attrib["mono_mass"])
                    elif element.tag.endswith("}alt_name"):
                        tmp["Alt Description"] = element.text
                    else:
                        pass
                else:
                    # end mod

                    if element.tag.endswith("}delta"):
                        tmp["elements"] = self._extract_elements(element)

                    elif element.tag.endswith("}specificity"):
                        amino_acid = element.attrib["site"]
                        classification = element.attrib["classification"]
                        if classification == "Artefact":
                            continue

                        neutral_loss_elements = {}
                        neutral_loss_mass = 0
                        if len(element) > 0:
                            for sub_element in element.iter():
                                if (
                                    sub_element.tag.endswith("}NeutralLoss")
                                    and len(sub_element) > 0
                                ):

                                    neutral_loss_elements = self._extract_elements(
                                        sub_element
                                    )
                                    neutral_loss_mass = float(
                                        sub_element.attrib["mono_mass"]
                                    )
                        tmp["specificity"].append(
                            f"{amino_acid}<|>{classification}<|>{neutral_loss_elements}<|>{neutral_loss_mass}"
                        )

                    elif element.tag.endswith("}mod"):
                        data_list.append(tmp)
                    else:
                        pass
        return data_list

    def _parseXML(self, xml_file_list=None):
        """Parse unimod xml.

        Returns:
            list: list of dicts with information regarding a unimod
        """
        if xml_file_list is None:
            xml_file_list = []
        data_list = []
        for xml_file in xml_file_list:
            xml_path = Path(xml_file)
            if xml_path.exists():
                logger.debug("Parsing mods file ({0})".format(xml_path))
                unimodXML = ET.iterparse(
                    codecs.open(xml_path, "r", encoding="utf8"),
                    events=(b"start", b"end"),
                )
                collect_element = False
                for event, element in unimodXML:
                    if event == b"start":
                        if element.tag.endswith("}mod"):
                            try:
                                unimodid = element.attrib["record_id"]
                            except KeyError:
                                unimodid = ""
                            tmp = {
                                "unimodID": unimodid,
                                "unimodname": element.attrib["title"],
                                "element": {},
                                "specificity": [],
                                "neutral_loss": [],
                            }
                        elif element.tag.endswith("}delta"):
                            collect_element = True
                            tmp["mono_mass"] = float(element.attrib["mono_mass"])
                        elif element.tag.endswith("}element"):
                            if collect_element is True:
                                number = int(element.attrib["number"])
                                if number != 0:
                                    tmp["element"][element.attrib["symbol"]] = number
                        elif element.tag.endswith("}specificity"):
                            amino_acid = element.attrib["site"]
                            classification = element.attrib["classification"]
                            if classification != "Artefact":
                                tmp["specificity"].append((amino_acid, classification))
                        elif element.tag.endswith("}NeutralLoss"):
                            if (
                                element.attrib["composition"]
                                and element.attrib["composition"] != "0"
                                and tmp["specificity"]
                            ):
                                amino_acid = tmp["specificity"][-1][0]
                                neutral_loss = element.attrib["mono_mass"]
                                tmp["neutral_loss"].append((amino_acid, neutral_loss))
                    else:
                        # end element
                        if element.tag.endswith("}delta"):
                            collect_element = False
                        elif element.tag.endswith("}mod"):
                            data_list.append(tmp)
                        else:
                            pass
            else:
                if xml_path.name == "unimod.xml":
                    logger.warning(f"No unimod.xml file found. Expected at {xml_path}")
                    # at least unimod.xml HAS to be available!
                    print(xml_path)
                    sys.exit(1)
                elif xml_path.name == "usermod.xml":
                    logger.debug(f"No usermod.xml file found. Expected at {xml_path}")
                    continue
                else:
                    logger.warning(f"Specified file not found. Expected at {xml_path}")
                    sys.exit(1)
        return data_list

    def _initialize_mapper(self):
        """Set up the mapper and generate the index dict."""
        mapper = {}
        for index, unimod_data_dict in enumerate(self.data_list):
            if unimod_data_dict["unimodname"] in mapper.keys():
                name = unimod_data_dict["unimodname"]
                id = unimod_data_dict["unimodID"]
                logger.warning(f"Warning: unimod {name} (ID {id}) is duplicated")

            for key, value in unimod_data_dict.items():
                if key == "element":
                    MAJORS = ["C", "H"]
                    hill_notation = ""
                    for major in MAJORS:
                        if major in unimod_data_dict[key].keys():
                            hill_notation += "{0}({1})".format(
                                major, unimod_data_dict[key][major]
                            )
                    for symbol, number in sorted(unimod_data_dict[key].items()):
                        if symbol in MAJORS:
                            continue
                        hill_notation += "{0}({1})".format(symbol, number)

                    if hill_notation not in mapper.keys():
                        mapper[hill_notation] = []
                    mapper[hill_notation].append(index)
                elif key == "specificity":
                    pass
                elif key == "neutral_loss":
                    pass
                else:
                    if value not in mapper.keys():
                        mapper[value] = []
                    mapper[value].append(index)
        return mapper

    # name 2 ....
    @deprecated
    def name2mass_list(self, unimod_name):
        """
        Converts unimod name to all matching unimod mono isotopic masses

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of Unimod mono isotopic masses
        """
        list_2_return = []
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "mono_mass"))
        return list_2_return

    @deprecated
    def name2first_mass(self, unimod_name):
        """
        Converts unimod name to unimod mono isotopic mass returning the first instance

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            float: Unimod mono isotopic mass
        """
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            index = min(index_list)
            rval = self._data_list_2_value(index, "mono_mass")
        else:
            rval = None
        return rval

    @deprecated
    def name2composition_list(self, unimod_name):
        """
        Converts unimod name to all matching unimod compositions

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of Unimod compositions
        """
        list_2_return = []
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "element"))
        return list_2_return

    @deprecated
    def name2first_composition(self, unimod_name):
        """
        Converts unimod name to unimod composition returning the first instance only

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of tuples (specificity sites, classification)Unimod mono isotopic mass
        """
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            index = min(index_list)
            rval = self._data_list_2_value(index, "element")
        else:
            rval = None
        return rval

    @deprecated
    def name2id_list(self, unimod_name):
        """
        Converts unimod name to unimod id

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of Unimod mono isotopic masses
        """
        list_2_return = []
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "unimodID"))
        return list_2_return

    @deprecated
    def name2first_id(self, unimod_name):
        """
        Converts unimod name to unimod ID returning the first instance

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            float: Unimod mono isotopic mass
        """
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            index = min(index_list)
            rval = self._data_list_2_value(index, "unimodID")
        else:
            rval = None
        return rval

    @deprecated
    def name2neutral_loss_list(self, unimod_name):
        """
        Converts unimod name to neutral_loss

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of Unimod mono isotopic masses
        """
        list_2_return = []
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "neutral_loss"))
        return list_2_return

    @deprecated
    def name2specificity_list(self, unimod_name):
        """
        Converts unimod name to list of tuples containing the
        specified amino acids or sites and the classification

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of tuples (specificity sites, classification)
        """
        list_2_return = []
        index_list = self.mapper.get(unimod_name, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "specificity"))

        return list_2_return

    # unimodid 2 ....
    @deprecated
    def id2mass_list(self, unimod_id):
        """
        Converts unimod ID to unimod mass

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            float: Unimod mono isotopic mass
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        list_2_return = []
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "mono_mass"))
        return list_2_return

    @deprecated
    def id2first_mass(self, unimod_id):
        """
        Converts unimod ID to mono_mass returning the first instance

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            float: Unimod mono isotopic mass
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            index = min(index_list)
            rval = self._data_list_2_value(index, "mono_mass")
        else:
            rval = None
        return rval

    @deprecated
    def id2composition_list(self, unimod_id):
        """
        Converts unimod ID to unimod composition

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            dict: Unimod elemental composition
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        list_2_return = []
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "element"))
        return list_2_return

    @deprecated
    def id2first_composition(self, unimod_id):
        """
        Converts unimod ID to composition returning the first instance

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            dict: Unimod composition
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            index = min(index_list)
            rval = self._data_list_2_value(index, "element")
        else:
            rval = None
        return rval

    @deprecated
    def id2name_list(self, unimod_id):
        """
        Converts unimod ID to unimod name

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            str: Unimod name
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        list_2_return = []
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "unimodname"))
        return list_2_return

    @deprecated
    def id2first_name(self, unimod_id):
        """
        Converts unimod ID to composition returning the first instance

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            dict: Unimod composition
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            index = min(index_list)
            rval = self._data_list_2_value(index, "unimodname")
        else:
            rval = None
        return rval

    @deprecated
    def id2neutral_loss_list(self, unimod_id):
        """
        Converts unimod name to neutral_loss

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of Unimod mono isotopic masses
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        list_2_return = []
        index_list = self.mapper.get(unimod_id, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "neutral_loss"))
        return list_2_return

    # mass is ambigous therefore a list is returned
    @deprecated
    def mass2name_list(self, mass):
        """
        Converts unimod mass to unimod name list,
        since a given mass can map to mutiple entries in the XML.

        Args:
            mass (float): mass of modification

        Returns:
            list: Unimod names
        """
        list_2_return = []
        for index in self.mapper[mass]:
            list_2_return.append(self._data_list_2_value(index, "unimodname"))
        return list_2_return

    @deprecated
    def mass2id_list(self, mass):
        """
        Converts unimod mass to unimod name list,
        since a given mass can map to mutiple entries in the XML.

        Args:
            mass (float): mass of modification

        Returns:
            list: Unimod IDs
        """
        list_2_return = []
        index_list = self.mapper.get(mass, None)
        if index_list is not None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "unimodID"))
        return list_2_return

    @deprecated
    def mass2composition_list(self, mass):
        """
        Converts unimod mass to unimod element composition list,
        since a given mass can map to mutiple entries in the XML.

        Args:
            mass (float): mass of modification

        Returns:
            list: Unimod elemental compositions
        """

        list_2_return = []
        for index in self.mapper[mass]:
            list_2_return.append(self._data_list_2_value(index, "element"))
        return list_2_return

    @deprecated
    def appMass2id_list(self, mass, decimal_places=2):
        """
        Creates a list of unimod IDs for a given approximate mass

        Args:
            mass (float): approximate mass of modification

        Keyword Arguments:
            decimal_places (int): Precision with which the masses in the
                Unimod is compared to the input, i.e. round( mass, decimal_places )

        Returns:
            list: Unimod IDs

        Examples::

            >>> import pyqms
            >>> U = pyqms.UnimodMapper()
            >>> U.appMass2id_list(18, decimal_places=0)
                ['127', '329', '608', '1079', '1167']

        """
        return_list = self._appMass2whatever(
            mass, decimal_places=decimal_places, entry_key="unimodID"
        )
        return return_list

    @deprecated
    def appMass2element_list(self, mass, decimal_places=2):
        """
        Creates a list of element composition dicts for a given approximate mass

        Args:
            mass (float): approximate mass of modification

        Keyword Arguments:
            decimal_places (int): Precision with which the masses in the
                Unimod is compared to the input, i.e. round( mass, decimal_places )

        Returns:
            list: Dicts of elements

        Examples::

            >>> import pyqms
            >>> U = pyqms.UnimodMapper()
            >>> U.appMass2element_list(18, decimal_places=0)
                [{'F': 1, 'H': -1}, {'13C': 1, 'H': -1, '2H': 3},
                {'H': -2, 'C': -1, 'S': 1}, {'H': 2, 'C': 4, 'O': -2},
                {'H': -2, 'C': -1, 'O': 2}]


        """
        return_list = self._appMass2whatever(
            mass, decimal_places=decimal_places, entry_key="element"
        )
        return return_list

    @deprecated
    def appMass2name_list(self, mass, decimal_places=2):
        """
        Creates a list of unimod names for a given approximate mass

        Args:
            mass (float): approximate mass of modification

        Keyword Arguments:
            decimal_places (int): Precision with which the masses in the
                Unimod is compared to the input, i.e. round( mass, decimal_places )

        Returns:
            list: Unimod names

        Examples::

            >>> import pyqms
            >>> U = pyqms.UnimodMapper()
            >>> U.appMass2name_list(18, decimal_places=0)
                ['Fluoro', 'Methyl:2H(3)13C(1)', 'Xle->Met', 'Glu->Phe', 'Pro->Asp']

        """
        return_list = self._appMass2whatever(
            mass, decimal_places=decimal_places, entry_key="unimodname"
        )
        return return_list

    @deprecated
    def composition2name_list(self, composition):
        """
        Converts unimod composition to unimod name list,
        since a given composition can map to mutiple entries in the XML.

        Args:
            composition (dict): element composition (element, count pairs)

        Returns:
            list: Unimod names
        """
        list_2_return = []
        index_list = self.mapper.get(composition, None)
        if index_list is not None:
            for index in index_list:
                value = self._data_list_2_value(index, "unimodname")
                list_2_return.append(value)
        return list_2_return

    @deprecated
    def composition2id_list(self, composition):
        """
        Converts unimod composition to unimod name list,
        since a given composition can map to mutiple entries in the XML.

        Args:
            composition (dict): element composition (element, count pairs)

        Returns:
            list: Unimod IDs
        """
        list_2_return = []
        index_list = self.mapper.get(composition, None)
        if index_list is not None:
            for index in index_list:
                value = self._data_list_2_value(index, "unimodID")
                list_2_return.append(value)
        return list_2_return

    @deprecated
    def composition2mass(self, composition):
        """
        Converts unimod composition to unimod monoisotopic mass.

        Args:
            composition (dict): element composition (element, count pairs)

        Returns:
            float: monoisotopic mass
        """
        mass_2_return = None
        list_2_return = []
        index_list = self.mapper.get(composition, None)
        if index_list != None:
            for index in index_list:
                list_2_return.append(self._data_list_2_value(index, "mono_mass"))
            assert (
                len(set(list_2_return)) == 1
            ), """
            Unimod chemical composition {0}
            maps on different monoisotopic masses. This should not happen.
            """.format(
                composition
            )
            mass_2_return = list_2_return[0]
        return mass_2_return

    @deprecated
    def _appMass2whatever(self, mass, decimal_places=5, entry_key=None):
        return_list = []
        for entry in self.data_list:
            umass = entry["mono_mass"]
            rounded_umass = round(float(umass), decimal_places)
            if abs(rounded_umass - mass) <= sys.float_info.epsilon:
                return_list.append(entry[entry_key])
        return return_list

    @deprecated
    def _map_key_2_index_2_value(self, map_key, return_key):
        index = self.mapper.get(map_key, None)
        if index is None:
            print(
                "Cannot map {0} while trying to return {1}".format(map_key, return_key),
                file=sys.stderr,
            )
            return_value = None
        else:
            return_value = self._data_list_2_value(index[0], return_key)
        return return_value

    def _data_list_2_value(self, index, return_key):
        return self.data_list[index][return_key]

    def writeXML(self, modification_dict, xml_file=None):
        """
        Writes a unimod-style usermod.xml file in
        at the same location as the unimod.xml

        Args:
            modification_dict (dict): dictionary containing at least
            'mass' (mass of the modification),
            'name' (name of the modificaton),
            'composition' (chemical composition of the modification as a dictionary {element:number})
        """
        if xml_file == None:
            xml_file = Path(__file__).parent / "usermod.xml"
        else:
            xml_file = Path(xml_file)
        unimod = ET.Element("{usermod}unimod")
        modifications = ET.SubElement(unimod, "{usermod}modifications")
        mod_dicts = [modification_dict]
        if xml_file.exists():
            data_list = self._parseXML(xml_file_list=[xml_file])
            for data_dict in data_list:
                mod_dict = {
                    "mass": data_dict["mono_mass"],
                    "name": data_dict["unimodname"],
                    "composition": data_dict["element"],
                    "id": data_dict["unimodID"],
                }
                mod_dicts.insert(-1, mod_dict)

        for modification_dict in mod_dicts:
            if modification_dict.get("id", None) == None:
                modification_dict["id"] = f"u{len(mod_dicts)}"
            mod = ET.SubElement(
                modifications,
                "{usermod}mod",
                title=modification_dict["name"],
                record_id=modification_dict["id"],
            )
            delta = ET.SubElement(
                mod, "{usermod}delta", mono_mass=str(modification_dict["mass"])
            )

            for symbol, number in modification_dict["composition"].items():
                element = ET.SubElement(
                    delta, "{usermod}element", symbol=symbol, number=str(number)
                )

        tree = ET.ElementTree(unimod)
        tree.write(str(xml_file), encoding="utf-8")
        xml = xmldom.parse(str(xml_file))
        pretty_xml_as_string = xml.toprettyxml()
        with open(xml_file, "w") as outfile:
            print(pretty_xml_as_string, file=outfile)
        xml_list = [
            Path(__file__).parent / xml_name for xml_name in self.unimod_xml_names
        ]
        xml_list.append(xml_file)
        self._reparseXML(xml_file_list=xml_list)
        return

    def _reparseXML(self, xml_file_list=[]):
        self._data_list = self._parseXML(xml_file_list=xml_file_list)
        self._mapper = self._initialize_mapper()

    def map_mods(self, mod_list):
        """
        Maps modifications defined in params["modification"] using unimods or user-defined modifications. Using the
        dict format for the mods, the dict can be adjusted depending on the purpose of
        the mapping. Moreover, it can have the minimal amount of items (i.e.: engine-specific ones).
        At the end the mapped values will be updated to the original dict.
        Note:
            Provided compositions are only accepted if they don't exist in the given unimod file already (or if the provided name fits as well).
            In general, if name and id are given, the modification will be chosen based on the name, not the id.
            If a unimod entry has an interim name and PSI-MS name, only the PSI-MS name will be accepted (but interim names are accepted if no PSI-MS name exists for that entry).

        Args:
            mod_list (list): list of mod_dicts containing all relevant info about a
                             given modification

        Returns:
            rdict (dict): dict with mod types as keys and corresponding lists of
                             mod dicts mapped to unimod

        Examples:

            mod_list = [
                {
                    "aa": "M",              # specify the modified amino acid as a single letter, use '*' if the amino acid is variable
                    "type": "opt",          # specify if it is a fixed (fix) or potential (opt) modification
                    "position": "any",      # specify the position within the protein/peptide (Prot-N-term, Prot-C-term), use 'any' if the positon is variable
                    "name": "Oxidation",    # specify the unimod PSI-MS Name (alternative to id)
                    "id": None,             # specify the unimod Accession (alternative to name)
                    "composition": None,    # For user-defined mods composition needs to be given as dict (e.g.: {"H":2, "O":1})
                }
            ]

        """

        rdict = {"fix": [], "opt": []}
        for index, mod in enumerate(mod_list):

            # Generate a default mod_dict with minimal required keys

            mod_dict = {
                "aa": None,
                "type": None,
                "position": None,
                "name": None,
                "mass": None,
                "composition": None,
                "id": None,
                "neutral_loss": None,
            }

            # - User input could be int or string, but has to be converted to string
            #   internally as map_mods output returns a string unimod_id!
            # - Has to happen here as mod will be written into mod_dict["org"]
            # - Thus, the user is more flexible, but the check will still work.
            if isinstance(mod.get("id", None), int):
                mod["id"] = str(mod["id"])

            mod_dict.update(mod)

            unimod = False
            unimod_id = None
            type = mod_dict["type"]
            if type not in ["opt", "fix"]:
                logger.warning(
                    "You selected a modification type, which is not supported. Only 'fix and 'opt' "
                    "modifications are accepted! Please contact the unimod-mapper dev team if you wish your"
                    "modification type to be considered."
                )
                # break

            if mod_dict["aa"] is None:
                logger.warning(
                    "The unimod mapper requires the information about the modified amino acid. "
                    "Please provide it in a single letter code, or '*' if the mod is not specific to a single"
                    "amino acid."
                )
                # break

            if mod_dict["position"] is None:
                logger.warning(
                    "Positional argument was not specified, which might impact further processing of the "
                    "modification."
                )
                # break

            if mod_dict["composition"] is None:
                if mod_dict["name"] is not None:
                    unimod_name = mod_dict["name"]
                    unimod_id = self.name_to_id(unimod_name)
                    mass = self.name_to_mass(unimod_name)
                    composition = self.name_to_composition(unimod_name)
                    if unimod_id == []:
                        logger.warning(
                            "'{1}' is not a Unimod modification please change it to a valid PSI-MS Unimod Name or Unimod Accession # or add the chemical composition as hill notation to the mod_dict, e.g: 'composition': 'H-1N1O2'. Continue without modification {0} ".format(
                                mod, unimod_name
                            )
                        )
                        continue
                    unimod = True
                elif mod_dict["id"] is not None:
                    unimod_id = mod_dict["id"]
                    unimod_name = self.id_to_name(unimod_id)
                    mass = self.id_to_mass(unimod_id)
                    composition = self.id_to_composition(unimod_id)
                    if unimod_name == []:
                        logger.warning(
                            "'{1}' is not a Unimod modification please change it to a valid Unimod Accession # or PSI-MS Unimod Name or add the chemical composition as hill notation to the mod_dict, e.g: 'composition': 'H-1N1O2'. Continue without modification {0} ".format(
                                mod_dict, unimod_id
                            )
                        )
                        continue
                    unimod = True
                else:
                    logger.warning(
                        "You have to provide either unimod_name, unimod_id or mod composition"
                        "to use the unimod mapping."
                    )
                    break
            else:
                unimod_name = mod_dict["name"]
                composition = mod_dict["composition"]
                unimod_name_list = self.composition_to_names(composition)
                unimod_id_list = self.composition_to_ids(composition)
                mass = self.composition_to_mass(composition)
                for i, name in enumerate(unimod_name_list):
                    if name == unimod_name:
                        unimod_id = unimod_id_list[i]
                        unimod = True
                        break
                if unimod is False and unimod_name_list != []:
                    logger.warning(
                        "'{0}' is not a Unimod modification but the chemical composition you specified is included in Unimod. Please use one of the Unimod names: {1} Continue without modification {2} ".format(
                            unimod_name, unimod_name_list, mod_dict
                        )
                    )
                    continue
                if unimod is False and unimod_name_list == []:
                    logger.warning(
                        "'{0}' is not a Unimod modification trying to continue with the chemical composition you specified. This is not working with OMSSA so far".format(
                            mod,
                        )
                    )
                    from chemical_composition import ChemicalComposition

                    cc_string = "+" + "".join(
                        ["{0}({1})".format(k, v) for k, v in composition.items()]
                    )
                    chemical_composition = ChemicalComposition()
                    chemical_composition.use(formula=cc_string)
                    mass = chemical_composition.mass()

            neutral_loss = []
            if mod_dict["neutral_loss"] == "unimod":

                for nl_item in self.name_to_neutral_loss(unimod_name):
                    if nl_item[0] == mod_dict["aa"]:
                        neutral_loss.append(nl_item[1])
            else:
                neutral_loss.append(mod_dict["neutral_loss"])

            mapped_dict = {
                "name": unimod_name,
                "id": unimod_id,
                "mass": mass,
                "composition": composition,
                "neutral_loss": neutral_loss,
            }

            # refactor the mapped_dict such as the first element of the list will be taken.
            # Raise a warning if list has more than 1 entry!
            # The double check allows to only modify those lists that were generated
            # by the x2x_list functions, but accept lists in other mod_params
            for key in mapped_dict.keys():
                if isinstance(mapped_dict[key], list):
                    if len(mapped_dict[key]) == 1:
                        mapped_dict[key] = mapped_dict[key][0]
                    elif len(mapped_dict[key]) > 1:
                        mapped_dict[key] = mapped_dict[key][0]
                        logger.warning(
                            f"More than 1 {key} was mapped. The {key} was assigned to the "
                            f"first element: {mapped_dict[key]}."
                        )

            wrong_mapping = False
            for key in mapped_dict.keys():
                if mod_dict[key] is None:
                    mod_dict[key] = mapped_dict[key]
                elif mod_dict[key] is not None:
                    if mod_dict[key] == mapped_dict[key]:
                        continue
                    elif mod_dict[key] != mapped_dict[key]:
                        if key == "neutral_loss" and mod_dict[key] == "unimod":
                            mod_dict[key] = mapped_dict[key]
                        else:
                            logger.warning(
                                f"The mapped key {mapped_dict[key]} does not match to the provided key {mod_dict[key]} value. "
                                f"Please resolve the inconsistency! The {mod} will be skipped!"
                            )
                            wrong_mapping = True

            # Finally add the last meta info to the mod_dict
            mod_dict.pop("type")
            mod_dict.update(
                {
                    "_id": index,
                    "org": mod,
                    "unimod": unimod,
                }
            )
            if wrong_mapping is False:
                rdict[type].append(mod_dict)
        return rdict


if __name__ == "__main__":
    print(__doc__)
    print(UnimodMapper.__doc__)
