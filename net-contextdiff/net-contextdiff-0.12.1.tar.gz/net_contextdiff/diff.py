# diff
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from copy import deepcopy
import re
import sys

from deepops import (
    deepdiff, deepfilter, deepget, deepmerge, deepremoveitems, deepsetdefault)

import yaml



# --- functions ---



def pathstr(path, wildcard_indices=set()):
    """This function converts a path, which is a list of items of
    various types (typically strings and integers), into a string,
    useful for debugging messages.

    The items are separated by commas and elements which are None are
    converted to a '*' since they're wildcards.

    If the index of the item in the path is in the wildcard_indices
    list, that item is prefixed with "*=" to show it matched a wildcard.
    The default for this parameter is an empty list, which causes no
    index to match.

    If we just printed the list, it would by in the more verbose Python
    format, with surrounding square brackets, quotes around strings and
    None for a wildcard, which is a little less readable.
    """

    return ":".join([ ("*=" if i in wildcard_indices else "") + str(v)
                            for i, v in enumerate(path) ])



# --- classes ---



class DiffConvert:
    """This abstract class handles converting the difference between a
    'from' configuration item to the corresponding 'to' configuration
    item.

    The main difference process will use deepops.deepdiff() to work out
    what has been removed and what updated (added/changed) between the
    two configurations.

    Individual differences are checked using child classes, which
    specify the part of the configuration directionaries where they
    occur and the remove() and update() methods called.  For example, if
    the hostname is changed, a 'hostname' converter would specify the
    part of the configuration dictionary where the hostname is stored
    and the update() method would return the commands required to change
    it to the new value.

    The 'context', 'cmd' and 'ext' parameters, below, are all tuples
    giving parts of the path through the keys of the configuration
    dictionary to match for the specific converter.  These can be
    literal keys, or the value None, if that level of the path is a
    wildcard match for all keys - for example, '("interface", None)' to
    match all interfaces.  The part of the configuration dictionary
    that matches the 'context + cmd' parts of the path will be passed
    as the 'old/new' and 'rem/upd' parameters to the action methods.

    The child classes can override the following values:

    context -- the path to the context containing the commands used in
    this conversion: if this context is removed in its entirety, the
    remove() action for this converter will not be called as the
    removal of the context will remove it; this variable defaults to
    the empty tuple, for a command at the top level

    cmd -- the path for this command in the configuration, following
    the context; this part of the dictionary will be passed in the
    'old/new' and 'rem/upd' parameters to the action methods; this
    variable defaults to None and must be defined by a child class

    ext -- an extension to path which must be matched, but this part is
    not used to further specify the part of the dictionaries passed to
    the action functions for the 'old/new' and 'rem/upd' parameters:
    this is useful when a higher level in the configuration dictionary
    is required in the action function

    name -- if there is more than one action acting at a particular path
    point, this can be defined to differentiate them: it's useful when
    using the insert_before parameter, but isn't needed if the order
    does not matter (except for ease of debugging, to clarify which
    converter is being called)

    insert_before -- if this rule needs to happen prior to the actions
    of another rule, this 2-tuple gives the (path, name) before the
    earlier rule; None means the order does not matter

    In addition the remove() and update() methods will likely need to be
    implemented.
    """


    context = tuple()
    cmd = None    # leave as None to cause an error if not defined in child
    ext = tuple()
    name = None
    insert_before = None


    def __init__(self):
        """The constructor just precalculates some details to optimise
        the repeated processing of the converter matches.
        """

        # calculate and store a few things, for efficiency
        self._path_full = self.context + self.cmd + self.ext
        self._context_len = len(self.context)
        self._path_len = len(self.context + self.cmd)

        # store the set of indices of wildcard elements of the path (we
        # need these to get the argument list to pass to the converter
        # action methods)
        self.wildcard_indices = {
            i for i, v in enumerate(self._path_full) if v is None }


    def _path_matches(self, d, path):
        """This method is used to recursively step along the
        paths.  It is initially called by full_matches() from the top of
        the path - see that for more information.
        """

        # if the path is finished, return a single result with an
        # empty list, as there are no more path elements
        #
        # note that this is different from an empty list (which
        # would mean no matches
        if not path:
            return [ [] ]

        # get the path head and tail to make things easier to read
        path_head, path_tail = path[0], path[1:]

        # if this element is not a type we can iterate or search
        # through (we've perhaps reached a value or a None), or the
        # dictionary is empty, there are no matches, so just return
        # an empty list (which will cause all higher levels in the
        # path that matched to be discarded, giving no resulsts)
        if not isinstance(d, (dict, list, set)) or (not d):
            return []

        # if the path element is None, we're doing a wildcard match
        if path_head is None:
            # initialise an empty list for all returned matching
            # results
            results = []

            # go through all the keys at this level in the dictonary
            for d_key in d:
                # are there levels below this one?
                if path_tail:
                    # yes - recursively get the matches from under
                    # this key
                    for matches in self._path_matches(d[d_key], path_tail):
                        # add this match to the list of matches,
                        # prepending this key onto the start of the
                        # path
                        results.append([d_key] + matches)
                else:
                    # no - just add this result (this is a minor
                    # optimisation, as well as avoiding an error by
                    # trying to index into a non-dict type), above
                    results.append([d_key])

            return results

        # we have a literal key to match - if it's found,
        # recursively get the matches under this level
        if path_head in d:
            return [ ([path_head] + matches)
                            for matches
                            in self._path_matches(d[path_head], path_tail) ]

        # we have no matches, return the empty list
        return []


    def full_matches(self, d):
        """This method takes a dictionary and returns any matches for
        the full path in it, as a list of paths; each path is, itself, a
        list of keys.

        If any of the elements of the path are None, this is treated as
        a wildcard and will match all keys at that level.

        If there are no matching entries, the returned list will be
        empty.

        The returned list of matches is not guaranteed to be in any
        particular order.
        """

        return self._path_matches(d, self._path_full)


    def context_removed(self, d, match):
        """This method takes a remove dictionary, as returned by
        deepdiff(), and a specific match into it (which must be from
        the same DiffConvert object as the method is called on) and
        returns True iff the context for this converter is in it
        entirely and exactly.
        """

        # if this converter has no containing context, we definitely
        # can't be removing it, so will need to remove this item
        if not self.context:
            return False

        # get the part of the match fitting the context for this
        # converter
        match_context = match[0 : self._context_len]

        # see if the context is matched in its entirety in the remove
        # dictionary - if it's not empty, or we get an error doing it,
        # we're not removing the context
        #
        # KeyError indicates item not found; TypeError if level is not
        # a dictionary
        try:
            return deepget(d, *match_context, default_error=True) is None
        except (KeyError, TypeError):
            return False


    def remove(self, old, *args):
        """The remove() method is called when the specified path is in
        the remove differences (i.e. it's in the 'from' configuration
        but not in the 'to' configuration), unless the containing
        context is being removed in its entirety.

        The default behaviour of this method is to call truncate() with
        the old value for 'old' and 'remove' as, if there is no specific
        behaviour for removing an entire object, we should remove the
        individual elements.

        Keyword arguments:

        old -- the value of the dictionary item at the matching path in
        the 'from' configuration dictionary (sometimes, the full details
        of the old configuration may be required to remove it)

        *args -- [only] the arguments in the path which were matched
        with wildcards, supplied in the order they were given in the
        context, cmd and ext (e.g. for a match of ["interface", None,
        "standby", None], this will be second and fouth elements of
        the path); if there are no wildcards, no extra arguments will
        be supplied

        The return value is the commands to insert into the
        configuration to convert it.  This can either be a simple
        string, in the case of only one line being required, or an
        iterable containing one string per line.  If the return value is
        None, it is an indication nothing needed to be done.  An empty
        string or iterable indicates the update did something, which did
        not change the configuration (this may have semantic
        differences).
        """

        return self.truncate(old, old, *args)


    def truncate(self, old, rem, *args):
        """The truncate() method is identical to remove() except that it
        is called when an item is partially removed (i.e. something
        remains in the 'to' configuration - it is 'truncated').

        It is useful when amending lists or sets and matching at the
        containing object level.

        Keyword arguments:

        old -- the value of the dictionary item at the matching path in
        the 'from' configuration dictionary (sometimes, the full details
        of the old configuration may be required to remove it)

        rem -- the value of the dictionary item at the matching path in
        the remove differences dictionary (sometimes, it's necessary to
        know only what is removed from the new configuration)

        *args -- [only] the arguments in the path which were matched
        with wildcards, supplied in the order they were given in the
        context, cmd and ext (e.g. for a match of ["interface", None,
        "standby", None], this will be second and fouth elements of
        the path); if there are no wildcards, no extra arguments will
        be supplied

        The return value is the commands to insert into the
        configuration to convert it.  This can either be a simple
        string, in the case of only one line being required, or an
        iterable containing one string per line.  If the return value is
        None, it is an indication nothing needed to be done.  An empty
        string or iterable indicates the update did something, which did
        not change the configuration (this may have semantic
        differences).
        """

        pass


    def add(self, new, *args):
        """The add() method is called when the specified path is in the
        update differences but did not exist in the 'from' configuration
        (i.e. it's something new that is being added to the
        configuration).

        By default, this calls update() with the new configuration as
        the updated and new configuration arguments (and 'args') as, in
        many cases, the process for adding something is the same as
        updating it (e.g. updating an interface description).  It can,
        however, be overridden to do something different or, more
        commonly, implement add() but not update() for a particular
        change (as the updates will be picked up by more specific
        paths in other objects).

        Keyword arguments:

        new -- the value of the dictionary item at the matching path in
        the 'to' configuration dictionary

        *args -- [only] the arguments in the path which were matched
        with wildcards, supplied in the order they were given in the
        context, cmd and ext (e.g. for a match of ["interface", None,
        "standby", None], this will be second and fouth elements of
        the path); if there are no wildcards, no extra arguments will
        be supplied

        The return value is the commands to insert into the
        configuration to convert it.  This can either be a simple
        string, in the case of only one line being required, or an
        iterable containing one string per line.  If the return value is
        None, it is an indication nothing needed to be done.  An empty
        string or iterable indicates the update did something, which did
        not change the configuration (this may have semantic
        differences).
        """

        return self.update(None, new, new, *args)


    def update(self, old, upd, new, *args):
        """The update() method is called when the specified path is in
        the update differences and also in the 'from' configuration
        (i.e. something is being updated in the configuration).

        Keyword arguments:

        old -- the value of the dictionary item at the matching path in
        the 'from' configuration dictionary (sometimes, the old
        configuration must be removed first, before the new
        configuration can be updated, so the details are required)

        upd -- the value of the dictionary item at the matching path in
        the update differences dictionary

        new -- the value of the dictionary item at the matching path in
        the 'to' configuration dictionary (sometimes, the full details
        of the new configuration may be required to update it)

        *args -- [only] the arguments in the path which were matched
        with wildcards, supplied in the order they were given in the
        context, cmd and ext (e.g. for a match of ["interface", None,
        "standby", None], this will be second and fouth elements of
        the path); if there are no wildcards, no extra arguments will
        be supplied

        The return value is the commands to insert into the
        configuration to convert it.  This can either be a simple
        string, in the case of only one line being required, or an
        iterable containing one string per line.  If the return value is
        None, it is an indication nothing needed to be done.  An empty
        string or iterable indicates the update did something, which did
        not change the configuration (this may have semantic
        differences).
        """

        pass


    def get_path(self):
        """Get the non-extended path for this converter (i.e. the
        'context' and 'cmd' paths joined, excluding the 'ext').
        """

        return self.context + self.cmd


    def get_cfg(self, cfg, match):
        """This method returns the configuration to be passed to the
        converter's action methods [remove() and update()].

        By default, it indexes through the configuration using the path
        in the converter.  Converters may wish to override this, in some
        cases, for performance (perhaps if the entire configuration is
        to be returned).

        If the specified match path is not found, or there was a problem
        indexing along the path, None is returned, rather than an
        exception raised.
        """

        # try to get the specified matching path
        try:
            return deepget(cfg, *match[0 : self._path_len])

        except TypeError:
            # we got a TypeError so make the assumption that we've hit
            # a non-indexable element (such as a set) as the final
            # element of the path, so just return None
            return None


    def get_ext(self, cfg):
        """This method gets the extension part of the path, given a
        configuration dictionary starting at the path (i.e. what is
        passed as 'old/new' and 'rem/upd' in the action methods).

        An action method [remove() or update()] can use this to get the
        extension portion without needing to explicitly index through
        it.
        """

        return deepget(cfg, *self.ext)


    def get_wildcard_args(self, match):
        """This method returns a list of the wildcarded parts of the
        specified match as a list.  For example, if the path of this
        converter is 'interface', None) and the match is ['interface',
        'Vlan100'], the returned result will be ['Vlan100'].  This is
        used to supply the 'args' parameter to action methods.
        """

        return [ match[i] for i in self.wildcard_indices ]



class DiffConfig:
    """This abstract class is used to represent a configuration
    difference processor that can convert a configuration from one to
    another, using a method (which can be called once for each pair of
    configuration files).

    It encapsulates the rules for exluding items from the comparison.
    """


    def __init__(self, init_explain=False, init_dump_config=False,
                 init_dump_diff=False, init_debug_convert=0):

        """The constructor initialises the exclude list to empty and
        adds and converters using _add_converters().  It also stores
        some settings controlling the level of information describing
        the conversion process, based on the command line arguments:

        init_explain=False -- include comments in the output
        configuration changes that explain the differences being matched
        by the DiffConvert objects (if available).

        init_dump_config=False -- dump the 'from' and 'to'
        configurations (after exludes)

        init_dump_diff=False -- dump the differences (remove and update
        configurations)

        init_debug_convert=0 -- level of debugging information for the
        conversion process: >= 1: include steps, >= 2: include 'old/new'
        and 'rem/upd' parameters
        """

        # store the [initial] settings for the conversion process
        self._explain = init_explain
        self._dump_config = init_dump_config
        self._dump_diff = init_dump_diff
        self._debug_convert = init_debug_convert

        # initialise the dictionary of excludes, which will be passed
        # to deepremoveitems()
        self.init_rules()

        # initialise the list of converters and add them
        self._cvts = []
        self._add_converters()


    def _add_converters(self):
        """This method adds the converters for a particular object to
        the list used by the convert() method, usually by calling
        _add_converter() for each (see that method).

        The base class does nothing but child classes will implement it
        as they require.
        """

        pass


    def _add_converter(self, cvt):
        """Add an individual convert object, a child of the
        DiffConverter class, to the list of converters to be used by the
        convert() method.

        If the converter has an 'insert_before' entry that is not None,
        the converter will be inserted in the postition immediately
        before the existing entry with that name.  If that entry cannot
        be found, a KeyError will be raised.
        """

        if not cvt.insert_before:
            # no 'insert_before' - just add it to the end
            self._cvts.append(cvt)

        else:
            # 'insert_before' so we need to find that entry

            # get the indexes and entries in the converter list
            for pos, chk_cvt in enumerate(self._cvts):
                # if this entry is the one we're inserting before, put
                # it here and stop
                if chk_cvts.name == cvts.insert_before:
                    self._cvts.insert(pos, cvt)
                    break

            else:
                # we got the end of the list and didn't find it, so
                # raise an exception
                raise KeyError("cannot find existing converter with name: "
                               + cvt.insert_before)


    def _explain_comment(self, path):
        """This method returns a comment or other configuration item
        explaining the path supplied (which will typically be a match
        against a converter).  The path is supplied a list of levels and
        converted to a string using pathstr().

        Child classes can override this to provide a comment appropriate
        for their platform.

        If the function returns None, no comment is inserted.
        """

        return None


    def _diffs_begin(self):
        """This method returns a head (beginning) for a generated
        changes configuration file as an iterable of strings.

        In the abstract class, it returns None (which does not add
        anything) but, in child classes it may return a beginning line
        or similar.

        Note that if there are no changes, this will not be included in
        an otherwise empty file.
        """

        return []


    def _diffs_end(self):
        """This method returns a tail (ending) for a generated changes
        configuration file as an iterable of strings.

        In the abstract class, it returns None (which does not add
        anything) but, in child classes it may return an 'end' line or
        similar.

        Note that if there are no changes, this will not be included in
        an otherwise empty file.
        """

        return []


    def init_rules(self):
        """This method initialises the rules s.  In the base
        class, it the resets it to an empty dictionary, but child
        classes can extend this to add some default exclusions for
        standard system configuration entries which should not be
        changed.

        It is normally only called by the constructor but can be called
        later, to clear the excludes list before adding more (if
        required).
        """

        self.init_rules_tree()
        self.init_rules_active()


    def init_rules_tree(self):
        """This method initialises the rules tree (the dictionary of
        rules typically read from a file.

        In the base class, it just sets it to an empty dictionary but
        some platform-specific classes may wish to extend this to set up
        a default tree (along with init_rules_active()).
        """

        self._rules_tree = {}


    def init_rules_active(self):
        """This method initialises the active rules list (the list of
        rules specifying what should be used from the rules tree).

        In the base class, it just sets it to an empty list but some
        platform-specific classes may wish to extend this to set up a
        default list.
        """

        self._rules_active = []


    def add_rules_tree_file(self, filename):
        """Read a tree of rules items from a YAML file.  This is
        typically done once but then different portions of the rules
        dictionary selected with set_rules_active().

        The contents of the file are added to the current tree.  To
        clear the current tree first, use init_rules_tree().
        """

        try:
            file_rules_tree = yaml.safe_load(open(filename))

        except yaml.parser.ParserError as exception:
            raise ValueError("failed parsing rules file: %s: %s"
                                 % (filename, exception))

        self._rules_tree.update(file_rules_tree)


    def add_rules_active(self, rule_specs, devicename):
        """Add a list of rules to the current rule list, which specifies
        what parts of the rules tree should be used and how (include or
        exclude these items), to control the comparison done by the
        convert() method.

        The rules are specified as a list of strings in the format
        '[!]<path>' where '!' means 'exclude' (if omitted, it means
        'include') and 'path' is a colon-separated list of keys giving
        the path into the rules tree.  A particular element can be
        given as '%', in which case the 'devicename' parameter will be
        used but, if the devicename argument is None/empty (False),
        then a warning is printed and the rule skipped.

        For example, if '!device-excludes:%' is given, and the
        devicename is 'router1', the part of the rules tree indexed by
        ["device-excludes"]["router1"] will be excluded from the
        comparison.

        The rules given will be added to the current rules list; if the
        list is to be cleared first, use init_rules_list().
        """

        for rule_spec in rule_specs:
            # find if this is an include or exclude rule and get the
            # path part

            include = not rule_spec.startswith("!")

            if include:
                rule_spec_path = rule_spec
            else:
                rule_spec_path = rule_spec[1:]


            path_elements = rule_spec_path.split(":")

            if ("%" in path_elements) and (not devicename):
                print("warning: rule specification: %s contains '%%' but no "
                      "device name - ignoring" % rule_spec_path,
                      file=sys.stderr)

                continue


            path = [ devicename if i == "%" else i for i in path_elements ]

            self._rules_active.append( (include, path) )


    def get_rules_tree(self):
        """The method returns the current rules tree (as initialised by
        init_rules_tree() and extended with read_rules_tree()).  This
        should not be modified.
        """

        return self._rules_tree


    def get_rules(self):
        """This method just returns the active rules list and the
        portion of the rules tree it applies to.

        The return value is a list, one entry per rule, containing
        2-tuples: the first entry is the rule specification (a string,
        in the format described by add_rules_active()), and the second
        the portion of the rules tree that the path references (or None,
        if that part of the tree does not exist).

        This method is mainly used for debugging messages.
        """

        r = []
        for include, path in self._rules_active:
            r.append(
                (("" if include else "!") + ":".join(path),
                 deepget(self._rules_tree, *path) ) )

        return r


    def apply_rules(self, d):
        """This method applies the current rules (tree and active list)
        to the supplied configuration dictionary, either only including
        what's specified (using deepfilter()) or excluding (using
        deepremoveitems()) the specified portions.

        The configuration dictionary is modified in place.

        The method can be used on a configuration dictionary, or the
        remove/update dictionaries returned by deepdiff().
        """

        for include, path in self._rules_active:
            # get the porttion of the rules tree specified by the path
            # in this rule
            path_dict = deepget(self._rules_tree, *path)

            # skip to the next entry, if this part was not found
            if path_dict is None:
                continue

            # do either the include or exclude on the configuration
            # dictionary, in place)
            if include:
                d = deepfilter(d, path_dict)
            else:
                deepremoveitems(d, path_dict)


    def convert(self, from_cfg, to_cfg):
        """This method processes the conversion from the 'from'
        configuration to the 'to' configuration, removing excluded parts
        of each and calling the applicable converters' action methods.

        Note that, if excludes are used, the configurations will be
        modified in place by a deepremoveitems().  They will need to be
        copy.deepcopy()ed before passing them in, if this is
        undesirable.

        The returned value is a 2-tuple:

        - the first element is a big string of all the configuration
          changes that need to be made, sandwiched between
          _diffs_begin() and _diffs_end(), or None, if there were no
          differences

        - the second element is a dictionary giving the tree of
          differences (i.e. the elements where a difference was
          encountered - either a remove or an update)
        """


        self.apply_rules(from_cfg)

        if self._dump_config:
            print(">> 'from' configuration (after rules, if specified):",
                  yaml.dump(dict(from_cfg), default_flow_style=False),
                  sep="\n")


        # initialise the list of diffs (the returned configuration
        # conversions) and the tree of differences to empty

        diffs = []
        diffs_tree = {}


        # if no 'to' config was specified, stop here (we assume we're
        # just testing, parsing and excluding items from the 'from'
        # configuration and stopping
        #
        # we check for None explicitly for the difference between no
        # configuration and an empty configuration

        if to_cfg is None:
            return None, diffs_tree


        self.apply_rules(to_cfg)

        if self._dump_config:
            print(">> 'to' configuration (after rules, if specified):",
                yaml.dump(dict(to_cfg), default_flow_style=False), sep="\n")


        # use deepdiff() to work out the differences between the two
        # configuration dictionaries - what must be removed and what
        # needs to be added or updated
        #
        # then use deepfilter() to get the full details of each item
        # being removed, rather than just the top of a subtree being
        # removed

        remove_cfg, update_cfg = deepdiff(from_cfg, to_cfg)
        remove_cfg_full = deepfilter(from_cfg, remove_cfg)


        if self._dump_diff:
            print("=> differences - remove:",
                  yaml.dump(dict(remove_cfg), default_flow_style=False),

                  "=> differences - remove full:",
                  yaml.dump(dict(remove_cfg_full), default_flow_style=False),

                  "=> differences - update (add/change):",
                  yaml.dump(dict(update_cfg), default_flow_style=False),

                  sep="\n")


        # go through the list of converter objects

        for cvt in self._cvts:
            if self._debug_convert:
                print(">> checking difference:",
                      pathstr([ "*" if i is None else i
                                    for i in cvt.get_path() ]),
                      "name:", cvt.name)


            # get all the remove and update matches for this converter
            # and combine them into one list, discarding any duplicates
            #
            # we do this rather than processing each list one after the
            # other so we combine removes and updates on the same part
            # of the configuration together
            #
            # we combine them by manually building a list, rather than
            # using a set as a set requires hashable types

            remove_matches = cvt.full_matches(remove_cfg_full)
            update_matches = cvt.full_matches(update_cfg)

            all_matches = []
            for match in sorted(remove_matches + update_matches):
                if match not in all_matches:
                    all_matches.append(match)


            for match in all_matches:
                # handle REMOVE conversions, if matching

                if match in remove_matches:
                    if self._debug_convert:
                        print("=> remove match:",
                              pathstr(match, cvt.wildcard_indices))


                    # if we're removing the entire context for this
                    # match, we don't need to do it, as that will
                    # remove this, while it's at it

                    if cvt.context_removed(remove_cfg, match):
                        if self._debug_convert:
                            print("-> containing context being removed - skip")

                        continue


                    # check if anything remains at this level or below
                    # in the 'to' configuration - if it does, we're
                    # doing a partial removal

                    remove_is_trunc = False

                    try:
                        # we don't want the result here, just to find
                        # out if the path exists (if not, KeyError will
                        # be raised)
                        deepget(to_cfg, *match, default_error=True)

                    except KeyError:
                        # nothing remains so we're doing a full remove
                        pass

                    else:
                        # something remains so this is partial
                        if self._debug_convert:
                            print("-> subconfiguration not empty - truncate")
                        remove_is_trunc = True


                    # get the 'from' and 'remove' parts of the
                    # configuration and remove difference dictionaries,
                    # for the path specified in the converter (ignoring
                    # the extension 'ext')

                    cvt_old = cvt.get_cfg(from_cfg, match)
                    cvt_rem = cvt.get_cfg(remove_cfg_full, match)

                    if self._debug_convert >= 2:
                        print(
                            "-> from configuration:",
                            yaml.dump(cvt_old, default_flow_style=False),

                            "-> remove configuration:",
                            yaml.dump(cvt_rem, default_flow_style=False),

                            sep="\n")


                    # get elements in the path matching wildcards

                    args = cvt.get_wildcard_args(match)


                    # call the remove converter action method using the
                    # corresponding entry from the 'from' configuration

                    try:
                        if remove_is_trunc:
                            diff = cvt.truncate(cvt_old, cvt_rem, *args)
                        else:
                            diff = cvt.remove(cvt_old, *args)

                    except:
                        print("with: type(cvt)=" + repr(type(cvt)),
                              file=sys.stderr)

                        raise


                    # if some diffs were returned by the action, add
                    # them

                    if diff is not None:
                        # the return can be either a simple string or a
                        # list of strings - if it's a string, make it a
                        # list of one so we can do the rest the same way

                        if isinstance(diff, str):
                            diff = [diff]

                        if self._debug_convert:
                            print("\n".join(diff))


                        # add a comment, explaining the match, if
                        # enabled

                        if self._explain:
                            comment = self._explain_comment(match)
                            if comment:
                                diffs.append(comment)


                        # store this diff on the end of the list of
                        # diffs so far

                        diffs.extend(diff)
                        diffs.append("")


                        # add this match to the differences tree

                        deepsetdefault(diffs_tree, *match)


                    else:
                        if self._debug_convert:
                            print("-> no action")


                # handle UPDATE conversions, if matching

                if match in update_matches:
                    if self._debug_convert:
                        print("=> update match:",
                              pathstr(match, cvt.wildcard_indices))


                    args = cvt.get_wildcard_args(match)


                    # check if there is anything for this level in the
                    # 'from' configuration - if not, we're actually
                    # adding this, rather than updating it, so record
                    # that

                    update_is_add = False

                    try:
                        deepget(from_cfg, *match, default_error=True)

                    except KeyError:
                        if self._debug_convert:
                            print("-> no old configuration - add")
                        update_is_add = True


                    # get the 'from' and 'update' parts of the
                    # configuration and update difference dictionaries,
                    # for the path specified in the converter (ignoring
                    # the extension 'ext')

                    cvt_old = cvt.get_cfg(from_cfg, match)
                    cvt_upd = cvt.get_cfg(update_cfg, match)
                    cvt_new = cvt.get_cfg(to_cfg, match)

                    if self._debug_convert >= 2:
                        print(
                            "-> from configuration:",
                            yaml.dump(cvt_old, default_flow_style=False),

                            "-> update configuration:",
                            yaml.dump(cvt_upd, default_flow_style=False),

                            "-> to configuration:",
                            yaml.dump(cvt_new, default_flow_style=False),

                            sep="\n")


                    # call the update converter action method

                    try:
                        # if we're adding this, call the add() method,
                        # else update()
                        if update_is_add:
                            diff = cvt.add(cvt_new, *args)
                        else:
                            diff = cvt.update(cvt_old, cvt_upd, cvt_new, *args)

                    except:
                        print("with: type(cvt)=" + repr(type(cvt)),
                              file=sys.stderr)

                        raise


                    # (same as in remove, above)

                    if diff is not None:
                        if isinstance(diff, str):
                            diff = [diff]

                        if self._debug_convert:
                            print("\n".join(diff))


                        if self._explain:
                            comment = self._explain_comment(match)
                            if comment:
                                diffs.append(comment)


                        diffs.extend(diff)
                        diffs.append("")

                        deepsetdefault(diffs_tree, *match)

                    else:
                        if self._debug_convert:
                            print("-> no action")


            # print a blank line if debugging, just to space things out
            # nicely

            if self._debug_convert:
                print()

        # if nothing was generated, just return nothing

        if not diffs:
            return None, diffs_tree


        # return the diffs concatenated into a big, multiline string,
        # along with the begin and end blocks

        return ("\n".join(self._diffs_begin() + diffs + self._diffs_end()),
                diffs_tree)
