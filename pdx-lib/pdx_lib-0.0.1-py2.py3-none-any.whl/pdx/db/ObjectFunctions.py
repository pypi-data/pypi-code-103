from pdx import Console
from pdx import CodeBlock
from pdx.db import OracleConnection
from pdx.db import ConnectionHolder
from pdx.db import Query
import re


out = Console.get()


def get_queryable_objects(sid, username=None, cache_results=False):
    """
    Get a list of queryable database objects.
    Return a dict with the object as key and object type as the value
    """
    out.trace("get_queryable_objects", [sid, username])

    # Return cached results, if available
    if ConnectionHolder.cached_objects:
        return ConnectionHolder.cached_objects

    # Otherwise, query for them
    select = """\
SELECT object_name, object_type \
  FROM dba_objects aa \
 WHERE object_type IN ('TABLE','VIEW','FUNCTION','PROCEDURE','PACKAGE', 'SEQUENCE') \
   AND NOT REGEXP_LIKE(object_name, '^GS_.*_\d+$') \
   AND EXISTS ( \
     SELECT 'x' FROM dba_objects bb \
      WHERE aa.object_name = bb.object_name AND bb.object_type = 'SYNONYM' \
   ) \
   AND length(object_name) > 4 \
   AND object_name NOT IN ('STRING', 'ACTION', 'EXCEPTIONS', 'DBMS_OUTPUT')
    """.strip()

    # Connect to DB
    oracle = OracleConnection.OracleConnection(sid, username)
    # Prepare the query
    query = Query.Query(oracle, select)

    if cache_results:
        # Run the query, cache and return the results
        ConnectionHolder.cached_objects = query.map()
        del query
        return ConnectionHolder.cached_objects

    else:
        # Run the query and return the results
        return query.map()


def find_queryable_objects(code_snippet, sid, username=None):
    """
    Find queryable objects referenced in a code snippet
    :param code_snippet: Any block of text, or a CodeBlock
    :param sid: Database to check against
    :param username: Database user to check as (default to yourself)
    :return: A map with the object name as the key
    """
    out.trace("find_queryable_objects")

    # Get all known database objects, if not already cached
    if ConnectionHolder.cached_objects is None:
        out.log_debug("Query for database objects")
        ConnectionHolder.cached_objects = get_queryable_objects(sid, username, True)
        out.log_debug("Found {0} objects".format(len(ConnectionHolder.cached_objects)))

    # Track query keywords (SELECT, INSERT, UPDATE, DELETE)
    keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE']

    # List of objects currently being evaluated (for insert, update, delete permissions)
    current_objects = []
    current_keywords = []

    # If the end of a query is identified, track it
    eoq = False

    if 'CodeBlock' in str(type(code_snippet)):
        code = code_snippet
    else:
        code = CodeBlock.CodeBlock(code_snippet)

    # Hold identified objects in a dict
    found_objects = {}

    # Look for known objects in the given code block
    for word in re.split(r"[.\s()]", code.get_without_comments().strip().upper()):
        try:
            # Query keywords always start a new query (even on nested selects)
            if word in keywords and len(current_keywords) > 0:
                eoq = True

            # If the end of a query was identified (above, or previous iteration)
            if eoq:
                try:
                    # The located object(s) get(s) the located permission(s).
                    for object_name in current_objects:
                        # Append to privileges list if already found
                        if object_name in found_objects:
                            found_objects[object_name]['privileges'].extend(current_keywords)
                        # Create a new entry if not yet found
                        else:
                            found_objects[object_name] = {
                                'name': object_name,
                                'type': ConnectionHolder.cached_objects[object_name],
                                'privileges': current_keywords
                            }

                except Exception as ee:
                    out.unexpected_error(
                        ee, "Error reporting privileges for {0}".format(current_objects)
                    )

                # Clear the objects and keywords
                current_objects = []
                current_keywords = []
                eoq = False

            # Is this a query keyword?
            if word in keywords:
                # Add the current keyword to the list and move on to the next word
                current_keywords.append(word)
                continue

            # is this the last word of the query?
            if word.endswith(';') or word == ';':
                eoq = True
                word = word[:-1]  # Strip off the ';' to compare the word

            # Ignore empty strings (consecutive delimiters)
            if word == "":
                continue

            # This is not a query keyword. Ignore other non-object keywords
            if word in ['AND', 'OR', 'WHERE', 'ORDER', 'SORT', 'BY', 'AS']:
                continue
            # Ignore other less common keywords
            if word in ['HAVING', 'DISTINCT', 'UNIQUE', 'CONNECT', 'CREATE', 'REPLACE']:
                continue

            # Look for word in list of known objects
            if word in ConnectionHolder.cached_objects:
                current_objects.append(word)

        except Exception as ee:
            out.unexpected_error(ee, "Could not process word: {0}".format(word))
            continue

    # The final query may not have been included. Add it now
    try:
        for object_name in current_objects:
            # Append to privileges list if already found
            if object_name in found_objects:
                found_objects[object_name]['privileges'].extend(current_keywords)
            # Create a new entry if not yet found
            else:
                found_objects[object_name] = {
                    'name': object_name,
                    'type': ConnectionHolder.cached_objects[object_name],
                    'privileges': current_keywords
                }
    except Exception as ee:
        out.unexpected_error(
            ee, "Error reporting privileges for {0}".format(current_objects)
        )

    # Any functions, procedures, or packages should have execute privileges. No other types should have execute
    for obj, info in found_objects.items():
        if info['type'] in ['FUNCTION', 'PROCEDURE', 'PACKAGE']:
            found_objects[obj]['privileges'] = ['EXECUTE']
        elif 'EXECUTE' in info['privileges']:
            found_objects[obj]['privileges'].remove('EXECUTE')

        # Remove duplicate privileges
        found_objects[obj]['privileges'] = list(set(found_objects[obj]['privileges']))

    # No permissions are needed for dual
    if 'DUAL' in found_objects:
        del found_objects['DUAL']

    return found_objects


def get_user_permissions(sid, check_user, username=None):
    """
    Get a list of permissions on database objects for given user.
    Return a dict with the object as key and permission list as the value
    """
    out.trace("get_user_permissions", [sid, check_user, username])

    # Query for user permissions
    select = """\
    SELECT DISTINCT table_name, privilege \
      FROM dba_tab_privs  \
     WHERE grantee IN ( \
        SELECT granted_role FROM dba_role_privs WHERE grantee = '{0}' \
        UNION \
        SELECT granted_role FROM dba_role_privs WHERE grantee IN ( \
             SELECT granted_role FROM dba_role_privs WHERE grantee = '{0}' \
        ) \
        UNION \
        SELECT granted_role FROM dba_role_privs WHERE grantee IN ( \
            SELECT granted_role FROM dba_role_privs WHERE grantee IN ( \
                SELECT granted_role FROM dba_role_privs WHERE grantee = 'GEN_USER' \
            ) \
        )
     ) \
    UNION \
    SELECT table_name, privilege  \
      FROM dba_tab_privs  \
     WHERE grantee = '{0}' \
    ORDER BY 1 \
    """.format(check_user.upper())

    # Connect to DB
    oracle = OracleConnection.OracleConnection(sid, username)
    # Prepare the query
    query = Query.Query(oracle, select)

    # Run the query
    results = query.list()

    # Create map of tables and privileges
    permissions = {}
    for result in results:
        if result[0] in permissions:
            permissions[result[0]].append(result[1])
        else:
            permissions[result[0]] = [result[1]]

    return permissions
