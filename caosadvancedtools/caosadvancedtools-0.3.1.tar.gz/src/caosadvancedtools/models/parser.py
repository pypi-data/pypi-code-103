"""
This module (and script) provides methods to read a DataModel from a YAML file.

If a file name is passed to parse_model_from_yaml it is parsed and a DataModel
is created. The yaml file needs to be structured in a certain way which will be
described in the following.

The file should only contain a dictionary. The keys are the names of
RecordTypes or Properties. The values are again dictionaries describing the
entities. This information can be defined via the keys listed in KEYWORDS.
Notably, properties can be given in a dictionary under the xxxx_properties keys
and will be added with the respective importance. These properties can be
RecordTypes or Properties and can be defined right there.
Every Property or RecordType only needs to be defined once anywhere. When it is
not defined, simply the name can be supplied with no value.
Parents can be provided under the 'inherit_from_xxxx' keywords. The value needs
to be a list with the names. Here, NO NEW entities can be defined.
"""
import re
import sys

import caosdb as db
import yaml

from .data_model import DataModel

# Keywords which are allowed in data model descriptions.
KEYWORDS = ["parent",
            "importance",
            "datatype",  # for example TEXT, INTEGER or REFERENCE
            "unit",
            "description",
            "recommended_properties",
            "obligatory_properties",
            "suggested_properties",
            "inherit_from_recommended",
            "inherit_from_suggested",
            "inherit_from_obligatory", ]

# These KEYWORDS are not forbidden as properties, but merely ignored.
KEYWORDS_IGNORED = [
    "unit",
]


def _get_listdatatype(dtype):
    """matches a string to check whether the type definition is a list

    returns the type within the list or None, if it cannot be matched with a
    list definition
    """
    # TODO: string representation should be the same as used by the server:
    # e.g. LIST<TEXT>
    # this should be changed in the module and the old behavour should be
    # marked as depricated
    match = re.match(r"^LIST[(<](?P<dt>.*)[)>]$", dtype)

    if match is None:
        return None
    else:
        return match.group("dt")

# Taken from https://stackoverflow.com/a/53647080, CC-BY-SA, 2018 by
# https://stackoverflow.com/users/2572431/augurar


class SafeLineLoader(yaml.SafeLoader):
    """Load a line and keep meta-information.

    Note that this will add a `__line__` element to all the dicts.
    """

    def construct_mapping(self, node, deep=False):
        """Overwritung the parent method."""
        mapping = super().construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping['__line__'] = node.start_mark.line + 1

        return mapping
# End of https://stackoverflow.com/a/53647080


class TwiceDefinedException(Exception):
    def __init__(self, name):
        super().__init__("The Entity '{}' was defined multiple times!".format(
            name))


class YamlDefinitionError(RuntimeError):
    def __init__(self, line, template=None):
        if not template:
            template = "Error in YAML definition in line {}."
        super().__init__(template.format(line))


def parse_model_from_yaml(filename):
    """Shortcut if the Parser object is not needed."""
    parser = Parser()

    return parser.parse_model_from_yaml(filename)


def parse_model_from_string(string):
    """Shortcut if the Parser object is not needed."""
    parser = Parser()

    return parser.parse_model_from_string(string)


class Parser(object):
    def __init__(self):
        self.model = {}
        self.treated = []

    def parse_model_from_yaml(self, filename):
        """Create and return a data model from the given file.

        Parameters
        ----------
        filename : str
          The path to the YAML file.

        Returns
        -------
        out : DataModel
          The created DataModel
        """
        with open(filename, 'r') as outfile:
            ymlmodel = yaml.load(outfile, Loader=SafeLineLoader)

        return self._create_model_from_dict(ymlmodel)

    def parse_model_from_string(self, string):
        """Create and return a data model from the given YAML string.

        Parameters
        ----------
        string : str
          The YAML string.

        Returns
        -------
        out : DataModel
          The created DataModel
        """
        ymlmodel = yaml.load(string, Loader=SafeLineLoader)

        return self._create_model_from_dict(ymlmodel)

    def _create_model_from_dict(self, ymlmodel):
        """Create and return a data model out of the YAML dict `ymlmodel`.

        Parameters
        ----------
        ymlmodel : dict
          The dictionary parsed from a YAML file.

        Returns
        -------
        out : DataModel
          The created DataModel
        """

        if not isinstance(ymlmodel, dict):
            raise ValueError("Yaml file should only contain one dictionary!")

        # Extern keyword:
        # The extern keyword can be used to include Properties and RecordTypes
        # from existing CaosDB datamodels into the current model.
        # Any name included in the list specified by the extern keyword
        # will be used in queries to retrieve a property or (if no property exists)
        # a record type with the name of the element.
        # The retrieved entity will be added to the model.
        # If no entity with that name is found an exception is raised.

        if "extern" not in ymlmodel:
            ymlmodel["extern"] = []

        for name in ymlmodel["extern"]:
            if db.execute_query("COUNT Property {}".format(name)) > 0:
                self.model[name] = db.execute_query(
                    "FIND Property WITH name={}".format(name), unique=True)

            elif db.execute_query("COUNT RecordType {}".format(name)) > 0:
                self.model[name] = db.execute_query(
                    "FIND RecordType WITH name={}".format(name), unique=True)
            else:
                raise Exception("Did not find {}".format(name))

        ymlmodel.pop("extern")

        # add all names to ymlmodel; initialize properties

        for name, entity in ymlmodel.items():
            self._add_entity_to_model(name, entity)
        # initialize recordtypes
        self._set_recordtypes()
        self._check_and_convert_datatypes()

        for name, entity in ymlmodel.items():
            self._treat_entity(name, entity, line=ymlmodel["__line__"])

        return DataModel(self.model.values())

    @staticmethod
    def _stringify(name, context=None):
        """Make a string out of `name`.

        Warnings are emitted for difficult values of `name`.

        Parameters
        ----------
        name :
          The value to be converted to a string.

        context : obj
          Will be printed in the case of warnings.

        Returns
        -------
        out : str
          If `name` was a string, return it. Else return str(`name`).
        """

        if name is None:
            print("WARNING: Name of this context is None: {}".format(context),
                  file=sys.stderr)

        if not isinstance(name, str):
            name = str(name)

        return name

    def _add_entity_to_model(self, name, definition):
        """ adds names of Properties and RecordTypes to the model dictionary

        Properties are also initialized.
        """

        if name == "__line__":
            return
        name = self._stringify(name)

        if name not in self.model:
            self.model[name] = None

        if definition is None:
            return

        if (self.model[name] is None
                and isinstance(definition, dict)
                # is it a property
                and "datatype" in definition
                # but not simply an RT of the model
                and not (_get_listdatatype(definition["datatype"]) == name and
                         _get_listdatatype(definition["datatype"]) in self.model)):

            # and create the new property
            self.model[name] = db.Property(name=name,
                                           datatype=definition["datatype"])

        # add other definitions recursively

        for prop_type in ["recommended_properties",
                          "suggested_properties", "obligatory_properties"]:

            if prop_type in definition:
                # Empty property mapping should be allowed.

                if definition[prop_type] is None:
                    definition[prop_type] = {}
                try:
                    for n, e in definition[prop_type].items():
                        if n == "__line__":
                            continue
                        self._add_entity_to_model(n, e)
                except AttributeError as ate:
                    if ate.args[0].endswith("'items'"):
                        line = definition["__line__"]

                        if isinstance(definition[prop_type], list):
                            line = definition[prop_type][0]["__line__"]
                        raise YamlDefinitionError(line) from None
                    raise

    def _add_to_recordtype(self, ent_name, props, importance):
        """Add properties to a RecordType."""

        for n, e in props.items():
            if n in KEYWORDS:
                if n in KEYWORDS_IGNORED:
                    continue
                raise YamlDefinitionError("Unexpected keyword in line {}: {}".format(
                    props["__line__"], n))

            if n == "__line__":
                continue
            n = self._stringify(n)

            if (isinstance(e, dict) and "datatype" in e
                    and (_get_listdatatype(e["datatype"]) is not None)):
                self.model[ent_name].add_property(
                    name=n,
                    importance=importance,
                    datatype=db.LIST(_get_listdatatype(e["datatype"])))
            else:
                self.model[ent_name].add_property(name=n,
                                                  importance=importance)

    def _inherit(self, name, prop, inheritance):
        if not isinstance(prop, list):
            raise YamlDefinitionError("Parents must be a list, error in line {}".format(
                prop["__line__"]))

        for pname in prop:
            if not isinstance(pname, str):
                raise ValueError("Only provide the names of parents.")
            self.model[name].add_parent(name=pname, inheritance=inheritance)

    def _treat_entity(self, name, definition, line=None):
        """Parse the definition and the information to the entity."""

        if name == "__line__":
            return
        name = self._stringify(name)

        try:
            if definition is None:
                return

            if ("datatype" in definition
                    and definition["datatype"].startswith("LIST")):

                return

            if name in self.treated:
                raise TwiceDefinedException(name)

            for prop_name, prop in definition.items():
                if prop_name == "__line__":
                    continue
                line = definition["__line__"]

                if prop_name == "unit":
                    self.model[name].unit = prop

                elif prop_name == "description":
                    self.model[name].description = prop

                elif prop_name == "recommended_properties":
                    self._add_to_recordtype(
                        name, prop, importance=db.RECOMMENDED)

                    for n, e in prop.items():
                        self._treat_entity(n, e)

                elif prop_name == "obligatory_properties":
                    self._add_to_recordtype(
                        name, prop, importance=db.OBLIGATORY)

                    for n, e in prop.items():
                        self._treat_entity(n, e)

                elif prop_name == "suggested_properties":
                    self._add_to_recordtype(
                        name, prop, importance=db.SUGGESTED)

                    for n, e in prop.items():
                        self._treat_entity(n, e)

                # datatype is already set
                elif prop_name == "datatype":
                    continue

                elif prop_name == "inherit_from_obligatory":
                    self._inherit(name, prop, db.OBLIGATORY)
                elif prop_name == "inherit_from_recommended":
                    self._inherit(name, prop, db.RECOMMENDED)
                elif prop_name == "inherit_from_suggested":
                    self._inherit(name, prop, db.SUGGESTED)

                else:
                    raise ValueError("invalid keyword: {}".format(prop_name))
        except AttributeError as ate:
            if ate.args[0].endswith("'items'"):
                raise YamlDefinitionError(line) from None
        except Exception as e:
            print("Error in treating: "+name)
            raise e
        self.treated.append(name)

    def _check_and_convert_datatypes(self):
        """ checks if datatype is valid.
        datatype of properties is simply initialized with string. Here, we
        iterate over properties and check whether it is a base datatype of a
        name that was defined in the model (or extern part)

        the string representations are replaced with caosdb objects

        """

        for key, value in self.model.items():

            if isinstance(value, db.Property):
                dtype = value.datatype
                is_list = False

                if _get_listdatatype(value.datatype) is not None:
                    dtype = _get_listdatatype(value.datatype)
                    is_list = True

                if dtype in self.model:
                    if is_list:
                        value.datatype = db.LIST(self.model[dtype])
                    else:
                        value.datatype = self.model[dtype]

                    continue

                if dtype in [db.DOUBLE,
                             db.REFERENCE,
                             db.TEXT,
                             db.DATETIME,
                             db.INTEGER,
                             db.FILE,
                             db.BOOLEAN]:

                    if is_list:
                        value.datatype = db.LIST(db.__getattribute__(dtype))
                    else:
                        value.datatype = db.__getattribute__(dtype)

                    continue

                raise ValueError("Property {} has an unknown datatype: {}".format(value.name, value.datatype))

    def _set_recordtypes(self):
        """ properties are defined in first iteration; set remaining as RTs """

        for key, value in self.model.items():
            if value is None:
                self.model[key] = db.RecordType(name=key)


if __name__ == "__main__":
    model = parse_model_from_yaml('data_model.yml')
    print(model)
