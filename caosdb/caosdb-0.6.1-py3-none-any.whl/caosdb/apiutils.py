# -*- coding: utf-8 -*-
#
# ** header v3.0
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Copyright (C) 2020 Timm Fitschen <t.fitschen@indiscale.com>
# Copyright (C) 2020 IndiScale GmbH <info@indiscale.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ** end header
#
"""API-Utils:

Some simplified functions for generation of records etc.
"""

import sys
import tempfile
import warnings
from collections.abc import Iterable
from subprocess import call

from caosdb.common.datatype import (BOOLEAN, DATETIME, DOUBLE, FILE, INTEGER,
                                    REFERENCE, TEXT, is_reference)
from caosdb.common.models import (Container, Entity, File, Property, Query,
                                  Record, RecordType, execute_query,
                                  get_config)


def new_record(record_type, name=None, description=None,
               tempid=None, insert=False, **kwargs):
    """Function to simplify the creation of Records.

    record_type: The name of the RecordType to use for this record.
                 (ids should also work.)
    name: Name of the new Record.
    kwargs: Key-value-pairs for the properties of this Record.

    Returns: The newly created Record.

    Of course this functions requires an open database connection!
    """

    rt = RecordType(name=record_type)
    rt.retrieve()

    r = Record(name)
    r.add_parent(rt)

    if tempid is not None:
        r.id = tempid

    if description is not None:
        r.description = description

    # Add all additional properties, treat iterables als multiple
    # additions.

    for k, v in kwargs.items():
        if hasattr(v, "encode") or not isinstance(v, Iterable):
            v = [v]

        for vv in v:
            p = Property(k)
            p.retrieve()
            p.value = vv
            r.add_property(p)

    if insert:
        r.insert()

    return r


def id_query(ids):
    warnings.warn("Please use 'create_id_query', which only creates"
                  "the string.", DeprecationWarning)

    return execute_query(create_id_query(ids))


def create_id_query(ids):
    return "FIND ENTITY WITH " + " OR ".join(
        ["ID={}".format(id) for id in ids])


def retrieve_entity_with_id(eid):
    return execute_query("FIND ENTITY WITH ID={}".format(eid), unique=True)


def retrieve_entities_with_ids(entities):
    collection = Container()
    step = 20

    for i in range(len(entities)//step+1):
        collection.extend(
            execute_query(
               create_id_query(entities[i*step:(i+1)*step])))

    return collection


def get_type_of_entity_with(id_):
    objs = retrieve_entities_with_ids([id_])

    if len(objs) == 0:
        raise RuntimeError("ID {} not found.".format(id_))

    if len(objs) > 1:
        raise RuntimeError(
            "ID {} is not unique. This is probably a bug in the CaosDB server." .format(id_))
    obj = objs[0]

    if isinstance(obj, Record):
        return Record
    elif isinstance(obj, RecordType):
        return RecordType
    elif isinstance(obj, Property):
        return Property
    elif isinstance(obj, File):
        return File
    elif isinstance(obj, Entity):
        return Entity


class CaosDBPythonEntity(object):

    _last_id = 0

    def __init__(self):
        # Save a copy of the dry state
        # of this object in order to be
        # able to detect conflicts.
        self.do_not_expand = False
        self._parents = []
        self._id = CaosDBPythonEntity._get_id()
        self._path = None
        self._file = None
        self.pickup = None
        # TODO:
        # 3.) resolve references up to a specific depth (including infinity)
        # 4.) resolve parents function -> partially implemented by
        # get_parent_names
        self._references = {}
        self._properties = set()
        self._datatypes = {}
        self._forbidden = dir(self)

    @staticmethod
    def _get_id():
        CaosDBPythonEntity._last_id -= 1

        return CaosDBPythonEntity._last_id

    def _set_property_from_entity(self, ent):
        name = ent.name
        val = ent.value
        pr = ent.datatype
        val, reference = self._type_converted_value(val, pr)
        self.set_property(name, val, reference, datatype=pr)

    def set_property(self, name, value, is_reference=False,
                     overwrite=False, datatype=None):
        """
        overwrite: Use this if you definitely only want one property with that name (set to True).
        """
        self._datatypes[name] = datatype

        if isinstance(name, Entity):
            name = name.name

        if name in self._forbidden:
            raise RuntimeError("Entity cannot be converted to a corresponding "
                               "Python representation. Name of property " +
                               name + " is forbidden!")
        already_exists = (name in dir(self))

        if already_exists and not overwrite:
            # each call to _set_property checks first if it already exists
            #        if yes: Turn the attribute into a list and
            #                place all the elements into that list.
            att = self.__getattribute__(name)

            if isinstance(att, list):
                pass
            else:
                old_att = self.__getattribute__(name)
                self.__setattr__(name, [old_att])

                if is_reference:
                    self._references[name] = [
                        self._references[name]]
            att = self.__getattribute__(name)
            att.append(value)

            if is_reference:
                self._references[name].append(int(value))
        else:
            if is_reference:
                self._references[name] = value
            self.__setattr__(name, value)

        if not (already_exists and overwrite):
            self._properties.add(name)

    add_property = set_property

    def set_id(self, idx):
        self._id = idx

    def _type_converted_list(self, val, pr):
        """Convert a list to a python list of the correct type."""
        prrealpre = pr.replace("&lt;", "<").replace("&gt;", ">")
        prreal = prrealpre[prrealpre.index("<") + 1:prrealpre.rindex(">")]
        lst = [self._type_converted_value(i, prreal) for i in val]

        return ([i[0] for i in lst], lst[0][1])

    def _type_converted_value(self, val, pr):
        """Convert val to the correct type which is indicated by the database
        type string in pr.

        Returns a tuple with two entries:
        - the converted value
        - True if the value has to be interpreted as an id acting as a reference
        """

        if val is None:
            return (None, False)
        elif pr == DOUBLE:
            return (float(val), False)
        elif pr == BOOLEAN:
            return (bool(val), False)
        elif pr == INTEGER:
            return (int(val), False)
        elif pr == TEXT:
            return (val, False)
        elif pr == FILE:
            return (int(val), False)
        elif pr == REFERENCE:
            return (int(val), True)
        elif pr == DATETIME:
            return (val, False)
        elif pr[0:4] == "LIST":
            return self._type_converted_list(val, pr)
        elif isinstance(val, Entity):
            return (convert_to_python_object(val), False)
        else:
            return (int(val), True)

    def attribute_as_list(self, name):
        """This is a workaround for the problem that lists containing only one
        element are indistinguishable from simple types in this
        representation."""
        att = self.__getattribute__(name)

        if isinstance(att, list):
            return att
        else:
            return [att]

    def _add_parent(self, parent):
        self._parents.append(parent.id)

    def add_parent(self, parent_id=None, parent_name=None):
        if parent_id is not None:
            self._parents.append(parent_id)
        elif parent_name is not None:
            self._parents.append(parent_name)
        else:
            raise ValueError("no parent identifier supplied")

    def get_parent_names(self):
        new_plist = []

        for p in self._parents:
            obj_type = get_type_of_entity_with(p)
            ent = obj_type(id=p).retrieve()
            new_plist.append(ent.name)

        return new_plist

    def resolve_references(self, deep=False, visited=dict()):
        for i in self._references:
            if isinstance(self._references[i], list):
                for j in range(len(self._references[i])):
                    new_id = self._references[i][j]
                    obj_type = get_type_of_entity_with(new_id)

                    if new_id in visited:
                        new_object = visited[new_id]
                    else:
                        ent = obj_type(id=new_id).retrieve()
                        new_object = convert_to_python_object(ent)
                        visited[new_id] = new_object

                        if deep:
                            new_object.resolve_references(deep, visited)
                    self.__getattribute__(i)[j] = new_object
            else:
                new_id = self._references[i]
                obj_type = get_type_of_entity_with(new_id)

                if new_id in visited:
                    new_object = visited[new_id]
                else:
                    ent = obj_type(id=new_id).retrieve()
                    new_object = convert_to_python_object(ent)
                    visited[new_id] = new_object

                    if deep:
                        new_object.resolve_references(deep, visited)
                self.__setattr__(i, new_object)

    def __str__(self, indent=1, name=None):
        if name is None:
            result = str(self.__class__.__name__) + "\n"
        else:
            result = name + "\n"

        for p in self._properties:
            value = self.__getattribute__(p)

            if isinstance(value, CaosDBPythonEntity):
                result += indent * "\t" + \
                    value.__str__(indent=indent + 1, name=p)
            else:
                result += indent * "\t" + p + "\n"

        return result


class CaosDBPythonRecord(CaosDBPythonEntity):
    pass


class CaosDBPythonRecordType(CaosDBPythonEntity):
    pass


class CaosDBPythonProperty(CaosDBPythonEntity):
    pass


class CaosDBPythonFile(CaosDBPythonEntity):
    def get_File(self, target=None):
        f = File(id=self._id).retrieve()
        self._file = f.download(target)


def _single_convert_to_python_object(robj, entity):
    robj._id = entity.id

    for i in entity.properties:
        robj._set_property_from_entity(i)

    for i in entity.parents:
        robj._add_parent(i)

    if entity.path is not None:
        robj._path = entity.path

    if entity.file is not None:
        robj._file = entity.file
    # if entity.pickup is not None:
    #     robj.pickup = entity.pickup

    return robj


def _single_convert_to_entity(entity, robj, **kwargs):
    if robj._id is not None:
        entity.id = robj._id

    if robj._path is not None:
        entity.path = robj._path

    if robj._file is not None:
        entity.file = robj._file

    if robj.pickup is not None:
        entity.pickup = robj.pickup
    children = []

    for parent in robj._parents:
        if sys.version_info[0] < 3:
            if hasattr(parent, "encode"):
                entity.add_parent(name=parent)
            else:
                entity.add_parent(id=parent)
        else:
            if hasattr(parent, "encode"):
                entity.add_parent(name=parent)
            else:
                entity.add_parent(id=parent)

    def add_property(entity, prop, name, recursive=False, datatype=None):
        if datatype is None:
            raise ArgumentError("datatype must not be None")

        if isinstance(prop, CaosDBPythonEntity):
            entity.add_property(name=name, value=str(
                prop._id), datatype=datatype)

            if recursive and not prop.do_not_expand:
                return convert_to_entity(prop, recursive=recursive)
            else:
                return []
        else:
            if isinstance(prop, float) or isinstance(prop, int):
                prop = str(prop)
            entity.add_property(name=name, value=prop, datatype=datatype)

            return []

    for prop in robj._properties:
        value = robj.__getattribute__(prop)

        if isinstance(value, list):
            if robj._datatypes[prop][0:4] == "LIST":
                lst = []

                for v in value:
                    if isinstance(v, CaosDBPythonEntity):
                        lst.append(v._id)

                        if recursive and not v.do_not_expand:
                            children.append(convert_to_entity(
                                v, recursive=recursive))
                    else:
                        if isinstance(v, float) or isinstance(v, int):
                            lst.append(str(v))
                        else:
                            lst.append(v)
                entity.add_property(name=prop, value=lst,
                                    datatype=robj._datatypes[prop])
            else:
                for v in value:
                    children.extend(
                        add_property(
                            entity,
                            v,
                            prop,
                            datatype=robj._datatypes[prop],
                            **kwargs))
        else:
            children.extend(
                add_property(
                    entity,
                    value,
                    prop,
                    datatype=robj._datatypes[prop],
                    **kwargs))

    return [entity] + children


def convert_to_entity(python_object, **kwargs):
    if isinstance(python_object, Container):
        # Create a list of objects:

        return [convert_to_python_object(i, **kwargs) for i in python_object]
    elif isinstance(python_object, CaosDBPythonRecord):
        return _single_convert_to_entity(Record(), python_object, **kwargs)
    elif isinstance(python_object, CaosDBPythonFile):
        return _single_convert_to_entity(File(), python_object, **kwargs)
    elif isinstance(python_object, CaosDBPythonRecordType):
        return _single_convert_to_entity(RecordType(), python_object, **kwargs)
    elif isinstance(python_object, CaosDBPythonProperty):
        return _single_convert_to_entity(Property(), python_object, **kwargs)
    elif isinstance(python_object, CaosDBPythonEntity):
        return _single_convert_to_entity(Entity(), python_object, **kwargs)
    else:
        raise ValueError("Cannot convert an object of this type.")


def convert_to_python_object(entity):
    """"""

    if isinstance(entity, Container):
        # Create a list of objects:

        return [convert_to_python_object(i) for i in entity]
    elif isinstance(entity, Record):
        return _single_convert_to_python_object(CaosDBPythonRecord(), entity)
    elif isinstance(entity, RecordType):
        return _single_convert_to_python_object(
            CaosDBPythonRecordType(), entity)
    elif isinstance(entity, File):
        return _single_convert_to_python_object(CaosDBPythonFile(), entity)
    elif isinstance(entity, Property):
        return _single_convert_to_python_object(CaosDBPythonProperty(), entity)
    elif isinstance(entity, Entity):
        return _single_convert_to_python_object(CaosDBPythonEntity(), entity)
    else:
        raise ValueError("Cannot convert an object of this type.")


def getOriginUrlIn(folder):
    """return the Fetch URL of the git repository in the given folder."""
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as t:
        call(["git", "remote", "show", "origin"], stdout=t, cwd=folder)
    with open(t.name, "r") as t:
        urlString = "Fetch URL:"

        for line in t.readlines():
            if urlString in line:
                return line[line.find(urlString) + len(urlString):].strip()

    return None


def getDiffIn(folder, save_dir=None):
    """returns the name of a file where the out put of "git diff" in the given
    folder is stored."""
    with tempfile.NamedTemporaryFile(delete=False, mode="w", dir=save_dir) as t:
        call(["git", "diff"], stdout=t, cwd=folder)

    return t.name


def getBranchIn(folder):
    """returns the current branch of the git repository in the given folder.

    The command "git branch" is called in the given folder and the
    output is returned
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as t:
        call(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=t, cwd=folder)
    with open(t.name, "r") as t:
        return t.readline().strip()


def getCommitIn(folder):
    """returns the commit hash in of the git repository in the given folder.

    The command "git log -1 --format=%h" is called in the given folder
    and the output is returned
    """

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as t:
        call(["git", "log", "-1", "--format=%h"], stdout=t, cwd=folder)
    with open(t.name, "r") as t:
        return t.readline().strip()


COMPARED = ["name", "role", "datatype", "description", "importance"]


def compare_entities(old_entity: Entity, new_entity: Entity):
    """
    Compare two entites.

    Return a tuple of dictionaries, the first index belongs to additional information for old
    entity, the second index belongs to additional information for new entity.

    Additional information means in detail:
    - Additional parents (a list under key "parents")
    - Information about properties:
      - Each property lists either an additional property or a property with a changed:
        - ... datatype
        - ... importance or
        - ... value (not implemented yet)
        In case of changed information the value listed under the respective key shows the
        value that is stored in the respective entity.
    """
    olddiff = {"properties": {}, "parents": []}
    newdiff = {"properties": {}, "parents": []}

    if old_entity is new_entity:
        return (olddiff, newdiff)

    for attr in COMPARED:
        try:
            oldattr = old_entity.__getattribute__(attr)
            old_entity_attr_exists = True
        except BaseException:
            old_entity_attr_exists = False
        try:
            newattr = new_entity.__getattribute__(attr)
            new_entity_attr_exists = True
        except BaseException:
            new_entity_attr_exists = False

        if old_entity_attr_exists and (oldattr == "" or oldattr is None):
            old_entity_attr_exists = False

        if new_entity_attr_exists and (newattr == "" or newattr is None):
            new_entity_attr_exists = False

        if not old_entity_attr_exists and not new_entity_attr_exists:
            continue

        if ((old_entity_attr_exists ^ new_entity_attr_exists)
                or (oldattr != newattr)):

            if old_entity_attr_exists:
                olddiff[attr] = oldattr

            if new_entity_attr_exists:
                newdiff[attr] = newattr

    # properties

    for prop in old_entity.properties:
        matching = [p for p in new_entity.properties if p.name == prop.name]

        if len(matching) == 0:
            olddiff["properties"][prop.name] = {}
        elif len(matching) == 1:
            newdiff["properties"][prop.name] = {}
            olddiff["properties"][prop.name] = {}

            if (old_entity.get_importance(prop.name) !=
                    new_entity.get_importance(prop.name)):
                olddiff["properties"][prop.name]["importance"] = \
                    old_entity.get_importance(prop.name)
                newdiff["properties"][prop.name]["importance"] = \
                    new_entity.get_importance(prop.name)

            if (prop.datatype != matching[0].datatype):
                olddiff["properties"][prop.name]["datatype"] = prop.datatype
                newdiff["properties"][prop.name]["datatype"] = \
                    matching[0].datatype

            if (prop.value != matching[0].value):
                olddiff["properties"][prop.name]["value"] = prop.value
                newdiff["properties"][prop.name]["value"] = \
                    matching[0].value

            if (len(newdiff["properties"][prop.name]) == 0
                    and len(olddiff["properties"][prop.name]) == 0):
                newdiff["properties"].pop(prop.name)
                olddiff["properties"].pop(prop.name)

        else:
            raise NotImplementedError()

    for prop in new_entity.properties:
        if len([0 for p in old_entity.properties if p.name == prop.name]) == 0:
            newdiff["properties"][prop.name] = {}

    # parents

    for parent in old_entity.parents:
        if len([0 for p in new_entity.parents if p.name == parent.name]) == 0:
            olddiff["parents"].append(parent.name)

    for parent in new_entity.parents:
        if len([0 for p in old_entity.parents if p.name == parent.name]) == 0:
            newdiff["parents"].append(parent.name)

    return (olddiff, newdiff)


def describe_diff(olddiff, newdiff, name=None, as_update=True):
    description = ""

    for attr in list(set(list(olddiff.keys())+list(newdiff.keys()))):
        if attr == "parents" or attr == "properties":
            continue
        description += "{} differs:\n".format(attr)
        description += "old version: {}\n".format(
            olddiff[attr] if attr in olddiff else "not set")
        description += "new version: {}\n\n".format(
            newdiff[attr] if attr in newdiff else "not set")

    if len(olddiff["parents"]) > 0:
        description += ("Parents that are only in the old version:\n"
                        + ", ".join(olddiff["parents"]))

    if len(newdiff["parents"]) > 0:
        description += ("Parents that are only in the new version:\n"
                        + ", ".join(olddiff["parents"]))

    for prop in list(set(list(olddiff["properties"].keys())
                         + list(newdiff["properties"].keys()))):
        description += "property {} differs:\n".format(prop)

        if prop not in olddiff["properties"]:
            description += "it does not exist in the old version: \n"
        elif prop not in newdiff["properties"]:
            description += "it does not exist in the new version: \n"
        else:
            description += "old version: {}\n".format(
                olddiff["properties"][prop])
            description += "new version: {}\n\n".format(
                newdiff["properties"][prop])

    if description != "":
        description = ("## Difference between the old and the new "
                       "version of {}\n\n".format(name))+description

    return description


def apply_to_ids(entities, func):
    """ Apply a function to all ids.

    All ids means the ids of the entities themselves but also to all parents,
    properties and referenced entities.

    Parameters
    ----------
    entities : list of Entity
    func : function with one parameter.
    """

    for entity in entities:
        _apply_to_ids_of_entity(entity, func)


def _apply_to_ids_of_entity(entity, func):
    entity.id = func(entity.id)

    for par in entity.parents:
        par.id = func(par.id)

    for prop in entity.properties:
        prop.id = func(prop.id)
        isref = is_reference(prop.datatype)

        if isref:
            if isinstance(prop.value, list):
                prop.value = [func(el) for el in prop.value]
            else:
                if prop.value is not None:
                    prop.value = func(prop.value)


def resolve_reference(prop: Property):
    """resolves the value of a reference property

    The integer value is replaced with the entity object.
    If the property is not a reference, then the function returns without
    change.
    """

    if not prop.is_reference(server_retrieval=True):
        return

    if isinstance(prop.value, list):
        referenced = []

        for val in prop.value:
            if isinstance(val, int):
                referenced.append(retrieve_entity_with_id(val))
            else:
                referenced.append(val)
        prop.value = referenced
    else:
        if isinstance(prop.value, int):
            prop.value = retrieve_entity_with_id(prop.value)
