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

    def __init__(self, refresh_xml=False, xml_file_list=None):
        if xml_file_list is None:
            xml_file_list = []
        self._data_list = None
        self._mapper = None

        # Check if unimod.xml file exists & if not reset refresh_xml flag
        full_path = Path(__file__).parent / "unimod.xml"
        if full_path.exists() is False:
            refresh_xml = True

        if refresh_xml is True:
            response = requests.get(url)
            with open(full_path, "wb") as file:
                file.write(response.content)

        self.unimod_xml_names = xml_file_list
        names = [x.name for x in xml_file_list]
        for xml in ["usermod.xml", "unimod.xml"]:
            if xml not in names:
                self.unimod_xml_names.append(Path(__file__).parent.joinpath(xml))

    @property
    def data_list(self):
        if self._data_list is None:
            self._data_list = self._parseXML(xml_file_list=self.unimod_xml_names)
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

    def _parseXML(self, xml_file_list=None):
        if xml_file_list is None:
            xml_file_list = []
        data_list = []
        for xml_file in xml_file_list:
            xml_path = Path(xml_file)
            if xml_path.exists():
                logger.info("> Parsing mods file ({0})".format(xml_path))
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
                        # end element
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
                elif xml_path.name == "usermod.xml":
                    logger.info(
                        "No usermod.xml file found. Expected at {0}".format(xml_path)
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
                elif key == "specificity":
                    pass
                else:
                    if value not in mapper.keys():
                        mapper[value] = []
                    mapper[value].append(index)
        return mapper

    # name 2 ....
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

    def name2first_mass(self, unimod_name):
        """
        Converts unimod name to unimod mono isotopic mass returning the first instance

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            float: Unimod mono isotopic mass
        """
        index = min(self.mapper.get(unimod_name, None))
        return self._data_list_2_value(index, "mono_mass")

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

    def name2first_composition(self, unimod_name):
        """
        Converts unimod name to unimod composition returning the first instance only

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            list: list of tuples (specificity sites, classification)Unimod mono isotopic mass
        """
        index = min(self.mapper.get(unimod_name, None))
        return self._data_list_2_value(index, "element")

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

    def name2first_id(self, unimod_name):
        """
        Converts unimod name to unimod ID returning the first instance

        Args:
            unimod_name (str): name of modification (as named in unimod)

        Returns:
            float: Unimod mono isotopic mass
        """
        index = min(self.mapper.get(unimod_name, None))
        return self._data_list_2_value(index, "unimodID")

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
        index = min(self.mapper.get(unimod_id, None))
        return self._data_list_2_value(index, "mono_mass")

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
        index = min(self.mapper.get(unimod_id, None))
        return self._data_list_2_value(index, "element")

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
        index = min(self.mapper.get(unimod_id, None))
        return self._data_list_2_value(index, "unimodname")

    # mass is ambigous therefore a list is returned
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

    def _appMass2whatever(self, mass, decimal_places=2, entry_key=None):
        return_list = []
        for entry in self.data_list:
            umass = entry["mono_mass"]
            rounded_umass = round(float(umass), decimal_places)
            if abs(rounded_umass - mass) <= sys.float_info.epsilon:
                return_list.append(entry[entry_key])
        return return_list

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

# @staticmethod
def map_mods(mod_list):
    """
    Maps modifications defined in params["modification"] using unimod.

    Args:
        umeta (ursgal.umeta.UMeta): umeta object containing all run relevant
                                    information. See _umeta_base for further info.

    Returns:
        mapped_mods["mods"] (dict): dict with modifications mapped with unimod

    Examples:

         >>> [
         ...    "M,opt,any,Oxidation",        # Met oxidation
         ...    "C,fix,any,Carbamidomethyl",  # Carbamidomethylation
         ...    "*,opt,Prot-N-term,Acetyl"    # N-Acteylation
         ... ]

        mod_dict = {
                "amino_acid": "M",
                "mod_option": "opt",
                "position": "any",
                "unimod_name": "Oxidation",
                "unimod_id": None,
                "chemical_formula": None, #Hill notation
                "neutral_loss": 0.0 #can be user-defined value, "unimod" to use the
                default from unimod (if existing)
            }


         >>> [
         ...    "M,opt,any,Oxidation",        # Met oxidation
         ...    "C,fix,any,Carbamidomethyl",  # Carbamidomethylation
         ...    "*,opt,Prot-N-term,Acetyl"    # N-Acteylation
         ... ]


    """
    # ls_dict = [{"amino_acid": "M",
    #             "mod_option": "opt",
    #             "position": "any",
    #             "unimod_name": "Oxidation"},
    #            {"amino_acid": "C",
    #             "mod_option": "fix",
    #             "position": "any",
    #             "unimod_name": "Carbamidomethyl"},
    #            {"amino_acid": "*",
    #             "mod_option": "opt",
    #             "position": "Prot-N-term",
    #             "unimod_name": "Acetyl"}]

    # breakpoint()
    umama = UnimodMapper()
    tmp_dict = {"fix": [], "opt": []}
    # tmp_dict["mods"] = {"fix": [], "opt": []}
    # udict = {}
    # udict["mapped_mods"] = {}
    # udict["mapped_mods"]["mods"] = {"fix": [], "opt": []}
    # if isinstance(mod_input, list):
    #     mod_list = mod_input
    # elif isinstance(mod_input, dict):
    #     sdf
    # else:
    #     logger.error("The supplied modification input is neither list or dict. Please "
    #                  "cha")
    #
    # try:
    #     mod_list = mod_dict.get("modifications", [])
    # except KeyError:
    #     mod_list = mod_dict["parameters"].get("modifications", [])

    for index, mod in enumerate(mod_list):
        # mod_params = mod.split(",")

        # TODO: make a query if any key from the mod dict is not suitable with ursgal!
        # if len(mod_params) >= 6 or len(mod_params) <= 3:
        #     logger.warning(
        #         "For modifications, please use the ursgal_style: 'amino_acid,opt/fix,position,Unimod PSI-MS Name' or 'amino_acid,opt/fix,position,name,chemical_composition'. Continue without modification {0} ".format(
        #             mod
        #         )
        #     )
        #     print(mod_params)
        #     continue

        # aa = mod.get("amino_acid", None)
        # aa = mod_params[0].strip()
        # mod_option
        # mod_option = mod_params[1].strip()
        # pos = mod_params[2].strip()
        unimod = False
        unimod_id = None
        mod_option = mod["mod_option"]

        # if len(mod_params) == 4:
        if mod.get("chemical_formula", None) is None:
            try:
                unimod_id = mod["unimod_id"]
                unimod_name = umama.id2name_list(unimod_id)
                mass = umama.id2mass_list(unimod_id)
                composition = umama.id2composition_list(unimod_id)
                if unimod_name == []:
                    logger.warning(
                        "'{1}' is not a Unimod modification please change it to a valid Unimod Accession # or PSI-MS Unimod Name or add the chemical composition hill notation (including 1) e.g.: H-1N1O2 ursgal_style: 'amino_acid,opt/fix,position,name,chemical_composition'. Continue without modification {0} ".format(
                            mod, unimod_id
                        )
                    )
                    continue
                unimod = True
                name = unimod_name
            except KeyError:
                unimod_name = mod["unimod_name"]
                unimod_id = umama.name2id_list(unimod_name)
                mass = umama.name2mass_list(unimod_name)
                composition = umama.name2composition_list(unimod_name)
                # if unimod_id is None:
                if unimod_id == []:
                    logger.warning(
                        "'{1}' is not a Unimod modification please change it to a valid PSI-MS Unimod Name or Unimod Accession # or add the chemical composition hill notation (including 1) e.g.: H-1N1O2 ursgal_style: 'amino_acid,opt/fix,position,name,chemical_composition'. Continue without modification {0} ".format(
                            mod, unimod_name
                        )
                    )
                    continue
                unimod = True
                name = unimod_name
        # TODO: implement the second part with the chemical_composition mapping
        # elif len(mod_params) == 5:
        #     name = mod_params[3].strip()
        #     chemical_formula = mod_params[4].strip()
        #     chemical_composition = ChemicalComposition()
        #     chemical_composition.add_chemical_formula(chemical_formula)
        #     composition = chemical_composition
        #     composition_unimod_style = chemical_composition.hill_notation_unimod()
        #     unimod_name_list = umama.composition2name_list(composition_unimod_style)
        #     unimod_id_list = umama.composition2id_list(composition_unimod_style)
        #     mass = umama.composition2mass(composition_unimod_style)
        #     for i, unimod_name in enumerate(unimod_name_list):
        #         if unimod_name == name:
        #             unimod_id = unimod_id_list[i]
        #             unimod = True
        #             break
        #     if unimod is False and unimod_name_list != []:
        #         logger.warning(
        #             "'{0}' is not a Unimod modification but the chemical composition you specified is included in Unimod. Please use one of the Unimod names: {1} Continue without modification {2} ".format(
        #                 name, unimod_name_list, mod
        #             )
        #         )
        #         continue
        #     if unimod is False and unimod_name_list == []:
        #         logger.warning(
        #             "'{0}' is not a Unimod modification trying to continue with the chemical composition you specified. This is not working with OMSSA so far".format(
        #                 mod,
        #             )
        #         )
        #         mass = chemical_composition.mass()
        #         # write new userdefined modifications Xml in unimod style

        mod_dict = {
            "_id": index,
            "aa": mod["amino_acid"],
            "mass": mass,
            "pos": mod["position"],
            "name": unimod_name,
            "composition": composition,
            "org": mod,
            "id": unimod_id,
            "unimod": unimod,
        }

        # refactor the dict such as the first element of the list will be taken.
        # Raise a warning if list has more than 1 entry!

        for obj in ["mass", "composition", "name", "id"]:
            if isinstance(mod_dict[obj], list):
                if len(mod_dict[obj]) >= 1:
                    mod_dict[obj] = mod_dict[obj][0]
                elif len(mod_dict[obj]) > 1:
                    # mod_dict[obj] = mod_dict[obj][0]
                    logger.warning(
                        f"More than 1 {obj} was mapped, due to multiple entries for "
                        f"{mod_dict['org']}. The {obj} was assigned to "
                        f"{mod_dict[obj]}."
                    )
        tmp_dict[mod_option].append(mod_dict)
        # output_dict = {"mods": tmp_dict}
    return tmp_dict


if __name__ == "__main__":
    print(__doc__)
    print(UnimodMapper.__doc__)
