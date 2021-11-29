import inspect
import sys

separators = "-_ "
alphabet = "abcdefghijklmnopqrstuvwxyz"

def getcases():
    """
    Function that scans all available cases of this repository.
    
    :returns: **cases**: (:py:class:`yield`: **1-D yield of string**) - Names of avalaible cases of this module
    
    :Example: Import the module and run the function without any argument.
    
    .. code-block:: python
        :linenos:
    
        import casing
        print([case for case in casing.getcases()])
        >>> ['attachedcase', 'attacheduppercase', 'camelcase', 'dashcase', 'dashuppercase', 'normalcase', 'normaluppercase', 'pascalcase', 'prettycase', 'reversedcase', 'sentencecase', 'snakecase', 'snakeuppercase']
    """
    return filter(lambda fct:fct.endswith("case"), dir(__import__(inspect.getmodulename(__file__))))


def detect(var):
    """
    Function that will detect the casing of the input variable.
    
    :param var: Variable to detect the casing
    :type var: :py:class:`str`
    
    :returns: **case**: (:py:class:`str`) - Names of avalaible cases of this module
    
    :Example: Import the module and run the function with the variable to detect.
    
    .. code-block:: python
        :linenos:
    
        import casing
        print(casing.detect("stringToDetect"))
        >>> "camel"
    """
    var_list = analyze(var)
    for fct in getcases():
        case = fct[:-len("case")]
        result = transform(var, case)   
        if result == var:
            break
    else:
        case = "unknow"
    return case


def analyze(var):
    """
    Split the input `var` in each elements.
    
    :param str var: Variable to analyze
    :type var: :py:class:`str`
    
    :returns: **case**: (:py:class:`list`: **1-D list of string**) - Analyze input `var` splited in lowercase
    
    :Example: Import the module and run the function with the variable to analyze.
    
    .. code-block:: python
        :linenos:
    
        import casing
        print(casing.analyze("stringToAnalyze"))
        >>> ['string', 'to', 'analyze']
    """    
    var_list = []
    buffer = ""
    for i, charact in enumerate(var):
        if charact in separators:
            var_list.append(buffer)
            buffer = ""
        elif charact in alphabet.upper():
            if i > 0 and var[i - 1].isupper():
                buffer += charact.lower()
            else:
                var_list.append(buffer)
                buffer = charact.lower()
        elif charact in alphabet:
            buffer += charact
    var_list.append(buffer)
    return list(filter(len, var_list))


def transform(var, case="snake"):
    """
    Transform the input into the indicated case.
    
    :param var: Variable to transform
    :param case: Case convention. Can be any available case. 
    
    :type var: :py:class:`str` / :py:class:`list`
    :type case: :py:class:`str`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input `var` in `case` convention
    
    .. code-block:: python
        :linenos:
    
        import casing
        print(casing.transform("stringToTransform", "snakeuppercase"))
        >>> "STRING_TO_TRANSFORM"
        print(casing.transform(['string', 'to', 'transform'], "dashcase"))
        >>> "string-to-transform"
    """ 
    if case.endswith("case"):
        case = case[:-len("case")]
    for fct in getcases():
        if "{0}case".format(case) == fct:
            function = globals()[fct]
            if type(var) is str:
                return function(analyze(var))
            elif type(var) is list:
                return function(var)
            else:
                Exception("Invalid type input")
    else:
        raise Exception("Case '{0}' don't exists".format(case))
    
    
def snakecase(var):  # some_variable
    """
    Snake case convention. Include '_' between each elements.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``snake_case`` convention.
    """
    return "_".join(var)
    
    
def snakeuppercase(var):  # SOME_VARIABLE
    """
    Snake uppercase convention. Include '_' between each element and transform in uppercase.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``SNAKE_UPPERCASE`` convention.
    """
    return "_".join(var).upper()
    
    
def dashcase(var):  # some-variable
    """
    Dash case convention. Include '-' between each element.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``dash-case`` convention.
    """
    return "-".join(var)
    
    
def dashuppercase(var):  # SOME-VARIABLE
    """
    Dash uppercase convention. Include '-' between each element and transform in uppercase.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``DASH-UPPERCASE`` convention.
    """
    return "-".join(var).upper()
    
    
def pascalcase(var):  # SomeVariable
    """
    Pascal case convention. Include an uppercase at every first element.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``PascalCase`` convention.
    """
    result = ""
    for element in var:
        element = list(element)
        element[0] = element[0].upper()
        result += "".join(element)
    return result
    
    
def camelcase(var):  # someVariable
    """
    Camel case convention. Include an uppercase at every first element except the first.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``camelCase`` convention.
    """
    result = ""
    for i, element in enumerate(var):
        element = list(element)
        if i > 0:
            element[0] = element[0].upper()
        result += "".join(element)
    return result
    
    
def normalcase(var):  # some variable
    """
    Normal case convention. Include space between each element.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``normal case`` convention.
    """
    return " ".join(var)
    
    
def prettycase(var):  # Some Variable
    """
    Pretty case convention. Include space between each element and uppercase the first letter of element.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``Pretty Case`` convention.
    """
    result = ""
    for i, element in enumerate(var):
        element = list(element)
        element[0] = element[0].upper()
        result += "".join(element) + " "
    return result[:-1]
    
    
def sentencecase(var):  # Some variable
    """
    Sentence case convention. Include space between each element and uppercase the first letter of first element.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``Sentence case`` convention.
    """
    result = ""
    for i, element in enumerate(var):
        element = list(element)
        if i == 0:
            element[0] = element[0].upper()
        result += "".join(element) + " "
    return result[:-1]
    
    
def normaluppercase(var):  # SOME VARIABLE
    """
    Normal uppercase convention. Include space between each element and transform in uppercase.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``NORMAL UPPERCASE`` convention.
    """
    return " ".join(var).upper()
    
    
def attachedcase(var):  # samevariable
    """
    Attached case convention. Join all elements together.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``attachedcase`` convention.
    
    .. warning:: It will lost the possibility to analyse or transform the output.
    """
    return "".join(var)
    
    
def attacheduppercase(var):  # SOMEVARIABLE
    """
    Attached uppercase convention. Join all elements together and transform in uppercase.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``ATTACHEDCASE`` convention.
    
    .. warning:: It will lost the possibility to analyse or transform the output.
    """
    return "".join(var).upper()


def reversedcase(var):  # some Variable
    """
    Reverse uppercase convention. Join all elements and uppercase first letter of alls except the first.
    
    :param var: Variable to transform
    :type var: :py:class:`list`
    
    :returns: **transformed**: (:py:class:`str`) - Transformed input in ``reverseCase`` convention.
    
    .. note:: Different from camelcase except on 2 or less elements input. 
    """
    result = list(prettycase(var))
    result[0] = result[0].lower()
    return "".join(result)


if __name__ == "__main__":
    cases = getcases()
    
    txt = "stringToDetect"
    print(f"{txt = }")
    
    sequence = analyze(txt)
    print(f"{sequence = }")
    print("-" * 50)
    
    for case in cases:
        print(f"{case}: {globals()[case](sequence)}")
    
    print(detect("string_to_detect"))