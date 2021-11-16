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

pd.set_option("max_columns", 100)

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
            new_fn_name = function.__name__.replace("2", "_to_")
            logger.warning(f"{old_fn_name} is deprecated, please use {new_fn_name}")
            return function(*args, **kwargs)

        return wrapper_deprecation_warning

    def __init__(self, refresh_xml=False, xml_file_list=None):
        self._data_list = None
        self._mapper = None
        self._df = None
        self._elements = []
        self._combos = {}
        # Check if unimod.xml file exists & if not reset refresh_xml flag
        package_dir = Path(__file__).parent.resolve()
        full_path = package_dir / "unimod.xml"
        if os.path.exists(full_path) is False:
            refresh_xml = True

        if refresh_xml is True:
            response = requests.get(url)
            with open(full_path, "wb") as file:
                file.write(response.content)

        self.unimod_xml_names = [
            package_dir / "unimod.xml",
            package_dir / "usermods.xml",
        ]
        if xml_file_list is not None:
            self.unimod_xml_names.extend(xml_file_list)

    @property
    def data_list(self):
        if self._data_list is None:
            xml_list = [
                Path(__file__).parent / xml_name for xml_name in self.unimod_xml_names
            ]
            self._data_list = self._parseXML(xml_file_list=xml_list)
        return self._data_list

    @data_list.setter
    def data_list(self, data_list):
        self._data_list = data_list
        return

    @property
    def mapper(self):
        if self._mapper is None:
            self._mapper = self._initialize_mapper()
        return self._mapper

    @mapper.setter
    def mapper(self, mapper):
        self._mapper = mapper
        return

    @property
    def df(self):
        if self._df is None:
            self._df = pd.DataFrame(self._parse_in_more_detail_XML())
            self._df = self._df.explode("specificity").reset_index(drop=True)
            sites = self._df.specificity.str.split("<\|>", expand=True)
            sites.columns = ["Site", "Position"]
            self._df.drop(columns=["specificity"], inplace=True)
            self._df = self._df.join(sites)
            # self._df.drop_duplicates(inplace=True)
        return self._df

    def query(self, query_string):
        return self.df.query(query_string)

    def name_to_mass(self, name):
        return self.df.query("`Name` == @name")["mono_mass"].to_list()

    def name_to_composition(self, name):
        return self.df.query("`Name` == @name")["elements"].to_list()

    def name_to_id(self, name):
        return self.df.query("`Name` == @name")["Accession"].to_list()

    def id_to_mass(self, id):
        return self.df.query("`Accession` == @id")["mono_mass"].to_list()

    def id_to_composition(self, id):
        return self.df.query("`Accession` == @id")["elements"].to_list()

    def id_to_name(self, id):
        return self.df.query("`Accession` == @id")["Name"].to_list()

    def _determine_mass_range(self, mass, decimals=0):
        fraction = 1 / 10 ** (decimals + 1)
        lower_mass = mass - 5 * fraction
        upper_mass = mass + 4 * fraction
        return lower_mass, upper_mass

    def mass_to_ids(self, mass, decimals=0):
        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)
        return (
            self.df.query("@lower_mass <= `mono_mass` <= @upper_mass")["Accession"]
            .unique()
            .tolist()
        )

    def mass_to_compositions(self, mass, decimals=0):
        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)
        return self.df.query("@lower_mass <= `mono_mass` <= @upper_mass")[
            "elements"
        ].tolist()

    def mass_to_names(self, mass, decimals=0):
        lower_mass, upper_mass = self._determine_mass_range(mass, decimals=decimals)
        return (
            self.df.query("@lower_mass <= `mono_mass` <= @upper_mass")["Name"]
            .unique()
            .tolist()
        )

    def mass_to_combos(self, mass, n=2, decimals=3):
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

    def _generate_mass_combos(self, n=2):
        mass_list = []
        for combo in itertools.combinations_with_replacement(
            self.df[["mono_mass", "Name"]].to_numpy(), 2
        ):

            combo_mass = np.sum(np.fromiter((c[0] for c in combo), float))
            combo_name = [c[1] for c in combo]
            mass_list.append((combo_mass, combo_name))
        return sorted(mass_list)

    def _extract_elements(self, element):
        r_dict = {}
        for sub_element in element.iter():
            if sub_element.tag.endswith("}element"):
                number = int(sub_element.attrib["number"])
                if number != 0:
                    r_dict[sub_element.attrib["symbol"]] = number
        return r_dict

    def _parse_in_more_detail_XML(self):
        data_list = []
        for xml_path in self.unimod_xml_names:
            xml_path = Path(xml_path)
            if os.path.exists(xml_path) is False:
                logger.warning(f"{xml_path} does not exist")
                continue

            logger.info("> Parsing mods file ({0})".format(xml_path))
            unimodXML = ET.iterparse(
                codecs.open(xml_path, "r", encoding="utf8"),
                events=(b"start", b"end"),
            )
            for event, element in unimodXML:
                if event == b"start":
                    if element.tag.endswith("}mod"):
                        tmp = {
                            "Name": element.attrib["title"],
                            "Accession": str(element.attrib["record_id"]),
                            "Description": element.attrib.get("full_name", ""),
                            "elements": {},
                            "specificity": [],
                            "neutral_losses": [],
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

                        tmp["specificity"].append(f"{amino_acid}<|>{classification}")
                        if len(element) > 0:
                            for sub_element in element.iter():
                                if (
                                    sub_element.tag.endswith("}NeutralLoss")
                                    and len(sub_element) > 0
                                ):
                                    neutral_loss_elements = self._extract_elements(
                                        sub_element
                                    )
                                    tmp["neutral_losses"].append(
                                        (amino_acid, neutral_loss_elements)
                                    )

                    elif element.tag.endswith("}mod"):
                        data_list.append(tmp)
                    else:
                        pass
        return data_list

    def _parseXML(self, xml_file_list=None):
        # is_frozen = getattr(sys, "frozen", False)
        # if is_frozen:
        #     xml_file = os.path.normpath(
        #         os.path.join(os.path.dirname(sys.executable), self.unimod_xml_name)
        #     )
        # else:
        #     xml_file = os.path.normpath(
        #         os.path.join(
        #             os.path.dirname(__file__), "kb", "ext", self.unimod_xml_name
        #         )
        #     )
        if xml_file_list is None:
            xml_file_list = []
        data_list = []
        for xml_path in xml_file_list:
            xml_path = Path(xml_path)
            if os.path.exists(xml_path):
                logger.info("> Parsing mods file ({0})".format(xml_path))
                unimodXML = ET.iterparse(
                    codecs.open(xml_path, "r", encoding="utf8"),
                    events=(b"start", b"end"),
                )
                collect_element = False
                for event, element in unimodXML:
                    if event == b"start":
                        if element.tag.endswith("}mod"):
                            tmp = {
                                "unimodID": element.attrib["record_id"],
                                "unimodname": element.attrib["title"],
                                "element": {},
                                "specificity": [],
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
                        else:
                            pass
                    else:
                        # end elementy
                        if element.tag.endswith("}delta"):
                            collect_element = False
                        elif element.tag.endswith("}mod"):
                            data_list.append(tmp)
                        else:
                            pass
            else:
                if xml_path.name == "unimod.xml":
                    logger.warning(
                        "No unimod.xml file found. Expected at {0}".format(xml_path)
                    )
                    # at least unimod.xml HAS to be available!
                    print(xml_path)
                    sys.exit(1)
                elif xml_path.name == "usermods.xml":
                    logger.info(
                        "No usermods.xml file found. Expected at {0}".format(xml_path)
                    )
                    continue
                else:
                    logger.warning(
                        "Specified file not found. Expected at {0}".format(xml_path)
                    )
                    sys.exit(1)
        return data_list

    def _initialize_mapper(self):
        """Set up the mapper and generate the index dict"""
        mapper = {}
        for index, unimod_data_dict in enumerate(self.data_list):
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
                elif key == "mono_mass":
                    if value not in mapper.keys():
                        mapper[value] = []
                    mapper[value].append(index)
                elif key == "specificity":
                    pass
                else:
                    if value not in mapper.keys():
                        mapper[value] = index
        return mapper

    # name 2 ....
    @deprecated
    def name2mass(self, unimod_name):
        """
        Converts unimod name to unimod mono isotopic mass

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            float: Unimod mono isotopic mass
        """
        return self._map_key_2_index_2_value(unimod_name, "mono_mass")

    @deprecated
    def name2composition(self, unimod_name):
        """
        Converts unimod name to unimod composition

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            dict: Unimod elemental composition
        """
        return self._map_key_2_index_2_value(unimod_name, "element")

    @deprecated
    def name2id(self, unimod_name):
        """
        Converts unimod name to unimod ID

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            int: Unimod ID
        """
        return self._map_key_2_index_2_value(unimod_name, "unimodID")

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
        list_2_return = None
        index = self.mapper.get(unimod_name, None)
        if index is not None:
            list_2_return = self._data_list_2_value(index, "specificity")
        return list_2_return

    @deprecated  # unimodid 2 ....
    def id2mass(self, unimod_id):
        """
        Converts unimod ID to unimod mass

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            float: Unimod mono isotopic mass
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        return self._map_key_2_index_2_value(unimod_id, "mono_mass")

    @deprecated
    def id2composition(self, unimod_id):
        """
        Converts unimod ID to unimod composition

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            dict: Unimod elemental composition
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        return self._map_key_2_index_2_value(unimod_id, "element")

    @deprecated
    def id2name(self, unimod_id):
        """
        Converts unimod ID to unimod name

        Args:
            unimod_id (int|str): identifier of modification

        Returns:
            str: Unimod name
        """
        if isinstance(unimod_id, int) is True:
            unimod_id = str(unimod_id)
        return self._map_key_2_index_2_value(unimod_id, "unimodname")

    @deprecated  # mass is ambigous therefore a list is returned
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
                list_2_return.append(self._data_list_2_value(index, "unimodname"))
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
                list_2_return.append(self._data_list_2_value(index, "unimodID"))
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
    def _appMass2whatever(self, mass, decimal_places=2, entry_key=None):
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
            return_value = self._data_list_2_value(index, return_key)
        return return_value

    @deprecated
    def _data_list_2_value(self, index, return_key):
        return self.data_list[index][return_key]

    def writeXML(self, modification_dict, xml_file=None):
        """
        Writes a unimod-style usermods.xml file in
        at the same location as the unimod.xml

        Args:
            modification_dict (dict): dictionary containing at least
            'mass' (mass of the modification),
            'name' (name of the modificaton),
            'composition' (chemical composition of the modification as a dictionary {element:number})
        """
        if xml_file == None:
            xml_file = Path(__file__).parent / "usermods.xml"
        else:
            xml_file = Path(xml_file)
        unimod = ET.Element("{usermod}unimod")
        modifications = ET.SubElement(unimod, "{usermod}modifications")
        mod_dicts = [modification_dict]
        if os.path.exists(xml_file):
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
                modification_dict["id"] = "u{0}".format(len(mod_dicts))
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


if __name__ == "__main__":
    print(__doc__)
    print(UnimodMapper.__doc__)
    U = UnimodMapper()
    U.query()
