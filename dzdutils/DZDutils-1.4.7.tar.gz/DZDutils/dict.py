def generate_argument_str(
    props: list or dict,
    key_prefix="",
    value_prefix="",
    prefix_seperator=".",
    equal_sign="=",
    separator=",",
) -> str:
    """Generates a list key/val attributes in a concatenated string
            The pattern is <key_prefix><prefix_seperator>propnameN1<equal_sign><value_prefix><prefix_seperator>propnameN1<seperator>
            e.g. n.id=a.id,n.name=a.name,...
            e.g. id:a.id,name:a.name,...
            
            Arguments:
                props {list or dict} -- dictonary of the key and values to be used in the result. If a list is provided key will equal value {"id":1, "company":"SuperCorp"} or ["id","companyname","myotherattr"]
            
            Keyword Arguments:
                key_prefix {str} -- string before key (will be followed by a "." if set) (default: {""})
                value_prefix {str} -- string before value (will be followed by a "." if set) (default: {""})
                equal_sign {str} -- the equal symbol (default: {"="})
                separator {str} -- the seperator inserted between the entries (default: {","})
            
            Returns:
                str -- The concatenated dict one string e.g. id:a.id,name:a.name
    """
    if isinstance(props, list):
        prop_dic = {key: key for key in props}
    else:
        prop_dic = props
    result = ""
    for key, val in prop_dic.items():
        result += (
            key_prefix
            + (prefix_seperator if key_prefix not in [None, ""] else "")
            + key
            + equal_sign
            + value_prefix
            + (prefix_seperator if value_prefix not in [None, ""] else "")
            + val
            + separator
        )
    return result.rstrip(",")
