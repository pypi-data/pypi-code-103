#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains functionality implementing the `search` command.

from bvlapi.data.organizations import get_organizations


def do_search(search_terms):
    """ Gives a list of information of organizations matching search terms.

    :param List[str] search_terms: a list of search terms

    :return: exit code and output
    :rtype: Tuple[int, str]
    """
    if len(search_terms) < 1:
        return 1, "unexpected amount of arguments"
    clubs = _find_clubs(search_terms)
    if not clubs:
        return 0, "could not find any clubs"
    return 0, _generate_output(clubs)


def _find_clubs(search_terms):
    """ Generate list of clubs matching all search terms.

    :param List[str] search_terms: a list of search terms

    :return: a list of organizations
    :rtype: List[Organization]
    """
    clubs = []
    for club in get_organizations():
        if all([(a in club.name) for a in search_terms]):
            clubs.append(club)
    return clubs


def _generate_output(clubs):
    """ Generates output based on list of clubs.

    :param List[Organization] clubs: a list of clubs

    :return: nicely formatted output
    :rtype: str
    """
    name_column_width = _determine_name_column_width(clubs)
    lines = []
    for club in clubs:
        line = _generate_line(club, name_column_width)
        lines.append(line)
    return "\n".join(lines)


def _determine_name_column_width(clubs):
    """ Determines how wide the name column of output should be.

    :param List[Organization] clubs: a list of clubs

    :return: width of name column
    :rtype: int
    """
    return max([len(club.name) for club in clubs])


def _generate_line(club, name_column_width):
    """ Generates a single line of output.

    :param Organization club: object holding information about club
    :param int name_column_width: width of name column

    :return: nicely formatted line of output
    :rtype: str
    """
    name_column = str(club.name) + ":"
    while len(name_column) <= (name_column_width + 3):
        name_column += " "

    stam_column = "{}".format(club.stam)
    while len(stam_column) <= 6:
        stam_column += " "

    guid_column = "({})".format(club.guid)

    return "{}{}{}".format(name_column, stam_column, guid_column)
