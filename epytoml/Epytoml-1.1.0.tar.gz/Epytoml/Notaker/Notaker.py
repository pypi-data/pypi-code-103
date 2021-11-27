"""
Notaker
An Epytoml module
Created by: Zhean 'Z1aaan' Ganituen

Notaker is an note-taking formatter for python.
Uses python syntax, and exports your Notaker document in html or pdf formats.
"""

from datetime import date as dt
import re
import secrets

# REMEMBER: Change version number in ntkGen() function
# REMEMBER: To add a '\n' at the end of each line that is appended in the ntkTitleHead

# variable that stores all of the content of the Notaker file being created
ntk_ContWhole = ""
"""Stores all the whole Notaker document.
"""

# these variables are the variables for the Notaker file being created
# _toc and _main are separated because _toc has to come first but the headers must be complete once it is generated
ntk_ContGen = ""
"""
"""

ntk_ContShut = ""
"""Stores all the created text by the contShut function.
"""

ntk_ContToc = ""
"""Stores all the table of contents of the Notaker document.
"""

ntk_ContMain = ""
"""Stores all the body of the Notaker document.
"""

ntk_ContMakeTitle = ""
"""Stores all the created text by the makeTitle function.
"""


# variable that collects all the headerCounts and their corresponding text in a key
ntk_heads = {}
"""Stores all the headers created using a header function accompanied by the headCountAdd function
"""

# variable that collects all the ntk_links of the headers, to be used in the table of contents
ntk_links = {}
"""Stores all the links created using the makeLink function, this is used in the toc function.
"""

# variable that stores the author name/s
# this variable must have its key as the author surname and the value as the author name/s
# sample: {1: ["FirstName_1", "Surname_1"], 2: ["FirstName_2", "Surname_2"] ... }
ntk_authors = {}
"""Stores the names of the author/s. {1: ["FirstName_N", "Surname_N"] ... }

"""


# variable that stores the creation date of the file
ntk_date = {"month": "", "day": "", "year": ""}
"""Stores the date the Notaker file was created.
"""

ntk_headCount = 1
"""Stores the total number of headers created.
"""


def ntkGen(fileName):
    """Writes all the document type declaration, html document start, html head, and html body.

    Args:
        fileName (str): This is will be the file name of your document.
    """
    # ntkFile is the output of the Notaker, append all user inputs here.
    file = fileName + ".html"

    #'<title>fileName</title>\n'
    ntkTitle = "<title>" + fileName + "</title>\n"
    ntkTitleHead = "<h1><b>" + fileName + "</b></h1>\n"

    # write the beginning of an html document
    # <!DOCTYPE html>
    # <html lang="en">
    # <head>
    # <meta charset="UTF-8">
    # <meta http-equiv="X-UA-Compatible" content="IE=edge">
    # <meta name="viewport" content="width=device-width, initial-scale=1.0">
    # <title>Document</title>
    # </head>
    # <body>

    global ntk_ContGen
    ntk_ContGen += "<!DOCTYPE html>\n"
    ntk_ContGen += '<html lang="en">\n'
    ntk_ContGen += "<head>\n"
    ntk_ContGen += '<meta charset="UTF-8">\n'
    ntk_ContGen += '<meta http-equiv="X-UA-Compatible" content="IE=edge">\n'
    ntk_ContGen += (
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    )
    ntk_ContGen += ntkTitle
    ntk_ContGen += "</head>\n"
    ntk_ContGen += "<body>\n"
    ntk_ContGen += "<!-- Created with Epytoml and Notaker. Version 1.0 --> \n"
    ntk_ContGen += "<!-- Notaker Start --> \n"
    ntk_ContGen += ntkTitleHead


def ntkShut():
    """Writes html document end, and html head end. Always end your Epytoml code with this."""

    # write the end of an html document
    # </body>
    # </html>

    global ntk_ContGen
    global ntk_ContMakeTitle
    global ntk_ContToc
    global ntk_ContMain
    global ntk_ContShut

    ntk_ContShut += "<!-- Notaker End -->\n"
    ntk_ContShut += "</body>\n"
    ntk_ContShut += "</html>\n"

    # append all the content to the ntk_ContWhole variable
    global ntk_ContWhole
    ntk_ContWhole += (
        ntk_ContGen
        + "\n"
        + ntk_ContMakeTitle
        + "\n"
        + ntk_ContToc
        + "\n"
        + ntk_ContMain
        + "\n"
        + ntk_ContShut
        + "\n"
    )


def nl(lines=None):
    """Creates one or multiple line breaks.

    Args:
        lines (int): Specifies how many line breaks are to be created, if lines is not given a value, this function will only create one line.
    """
    global ntk_ContMain
    # check if lines is none
    if lines is None:
        # if it is none, set it to default or 1
        lines = 1
    for i in range(lines):
        ntk_ContMain += "<br> \n"


class headerClass:
    """Contains all the functions needed in creating main headers (h1), creating hyperlinks and hyperlink ids, and adding the table of contents."""

    def __init__(self):
        # variable that counts how many header 1s are created
        ntk_headCount = 1

    def h(self, content):
        """Creates a main header (or h1 in html).

        Args:
            content (str): This is the text the header will display.

        Returns:
            This returns the complete (formatted) main header in html format.
        """
        # Make a header with the given text
        ntkHeader1 = "<h1>" + content + "</h1>\n"

        # Add the header to the ntk_heads dictionary
        ntk_heads[ntk_headCount] = ntkHeader1

        global ntk_ContMain
        ntk_ContMain += ntkHeader1

        return ntkHeader1

    def makeLink(self, content, autoFormat=None):
        """Creates a hyperlink, to be used in the toc function.

        Args:
            content (str): This will be set as the hyperlink URL address.
            autoFormat (bool, optional): The makeLink function automatically adds 'Chapter N:' before the content. Defaults to True.

        Returns:
            This returns the complete (formatted) hyperlink in html format.
        """
        # convert headerNumber to str, so it can be concatenated with ntkRefText
        headerNumberStr = str(ntk_headCount)

        if autoFormat is None:
            # when no autoFormat is given, use defualt or autoFormat = True
            ntkRefText = "Chapter " + headerNumberStr + ": " + content
        else:
            if autoFormat == True:
                ntkRefText = "Chapter " + headerNumberStr + ": " + content
            elif autoFormat == False:
                ntkRefText = content
            else:
                # when autoFormat is given but input not found, use defualt or autoFormat = True
                ntkRefText = "Chapter " + headerNumberStr + ": " + content

        ntkRef = '<a href="#' + content + '">' + ntkRefText + "</a><br>\n"

        ntk_links[ntk_headCount] = ntkRef

        return ntkRef

    def makeId(self, content):
        """Creates an id attribute. Always add this function every h function call.

        Args:
            content (str): This will be set as the hyperlink URL address.

        Returns:
            This returns the complete (formatted) id in html format.
        """
        global ntk_ContMain
        # Make a link id to the said header, to be used in the table of contents
        ntkID = '<a id="' + content + '"></a>\n'

        ntk_ContMain += ntkID

        return ntkID

    def headCountAdd(self):
        """Increments the ntk_heads variable."""
        # increment the headerCount by 1
        global ntk_headCount
        ntk_headCount += 1

    def toc(self, size=None):
        """Creates the table of contents after the title of the Notaker document.

        Args:
            size (int, optional): This specifies what the font size of the table of contents title. Defaults to size 1.
        """
        # make a table of contents

        headerValStart = "<h1>"
        headerValEnd = "</h1>"

        # make size=none to make it default to the header 1 size, unless specified
        if size is None or size == 1:
            headerValStart = "<h1>"
            headerValEnd = "</h1>"
        else:
            if size == 2:
                headerValStart = "<h2>"
                headerValEnd = "</h2>"
            elif size == 3:
                headerValStart = "<h3>"
                headerValEnd = "</h3>"
            elif size == 4:
                headerValStart = "<h4>"
                headerValStart = "</h4>"
            else:
                # if input not found then set to default
                headerValStart = "<h1>"
                headerValEnd = "</h1>"

        global ntk_ContToc

        tocTitle = headerValStart + "<b>Table of Contents</b>" + headerValEnd + "\n"

        ntk_ContToc += tocTitle

        for header in range(1, ntk_headCount):
            linkTitle = ntk_links[header]
            linkTitle += "\n"
            ntk_ContToc += linkTitle


def hh(content):
    """Creates a 2nd subheader (or h2 in html).

    Args:
        content (str): This is the text the header will display.

    Returns:
        This returns the complete (formatted) main header in html format.
    """
    ntkHeader2 = "<h2>" + content + "</h2>\n"
    global ntk_ContMain
    ntk_ContMain += ntkHeader2

    return ntkHeader2


def h3(content):
    """Creates a 3rd subheader (or h3 in html).

    Args:
        content (str): This is the text the header will display.

    Returns:
        This returns the complete (formatted) main header in html format.
    """
    ntkHeader3 = "<h3>" + content + "</h3>\n"
    global ntk_ContMain
    ntk_ContMain += ntkHeader3

    return ntkHeader3


def h4(content):
    """Creates a 4th subheader (or h4 in html).

    Args:
        content (str): This is the text the header will display.

    Returns:
        This returns the complete (formatted) main header in html format.
    """
    ntkHeader4 = "<h4>" + content + "</h4>\n"
    global ntk_ContMain
    ntk_ContMain += ntkHeader4

    return ntkHeader4


def h5(content):
    """Creates a 5th subheader (or h5 in html).

    Args:
        content (str): This is the text the header will display.

    Returns:
        This returns the complete (formatted) main header in html format.
    """
    ntkHeader5 = "<h5>" + content + "</h5>\n"
    global ntk_ContMain
    ntk_ContMain += ntkHeader5

    return ntkHeader5


def h6(content):
    """Creates a 6th subheader (or h6 in html).

    Args:
        content (str): This is the text the header will display.

    Returns:
        This returns the complete (formatted) main header in html format.
    """
    ntkHeader6 = "<h6>" + content + "</h6>\n"
    global ntk_ContMain
    ntk_ContMain += ntkHeader6

    return ntkHeader6


def t(content, emphasis=None):
    """Creates normal text in the Notaker document (or p in html).

    Args:
        content (str): This is the text the t function will display.
        emphasis (str, optional): Adds text emphasis to the content. Defaults to None.

    Returns:
        This returns the complete (formatted) text in html format.
    """
    # write text to the main body of the Notaker file
    # text does not insert a <br> at the end of the text

    if emphasis is None:
        # default text when there are no emphasis tags specified
        ntkP = "<p>" + content + "</p>\n"
    else:
        emphasis = emphasis.lower()
        if emphasis == "b" or emphasis == "bold" or emphasis == "1":
            # bold text
            ntkP = "<p><b>" + content + "</b></p>\n"
        elif emphasis == "i" or emphasis == "italic" or emphasis == "2":
            # italic text
            ntkP = "<p><i>" + content + "</i></p>\n"
        elif emphasis == "u" or emphasis == "underline" or emphasis == "3":
            # underline text
            ntkP = "<p><u>" + content + "</u></p>\n"
        else:
            # if input not found then set to default
            ntkP = "<p>" + content + "</p>\n"

    global ntk_ContMain
    ntk_ContMain += ntkP

    return ntkP


def tL(content, emphasis=None):
    """Creates normal text and a new line at the bottom in the Notaker document.

    Args:
        content (str): This is the text the tL function will display.
        emphasis (str, optional): Adds text emphasis to the content. Defaults to None.

    Returns:
        This returns the complete (formatted) text in html format.
    """
    # write text to the main body of the Notaker file
    # textL inserts a <br> at the end of the text

    if emphasis is None:
        # default text when there are no emphasis tags specified
        ntkP = "<p>" + content + "</p><br>\n"
    else:
        emphasis = emphasis.lower()
        if emphasis == "b" or emphasis == "bold" or emphasis == "1":
            # bold text
            ntkP = "<p><b>" + content + "</b></p><br>\n"
        elif emphasis == "i" or emphasis == "italic" or emphasis == "2":
            # italic text
            ntkP = "<p><i>" + content + "</i></p><br>\n"
        elif emphasis == "u" or emphasis == "underline" or emphasis == "3":
            # underline text
            ntkP = "<p><u>" + content + "</u></p><br>\n"
        else:
            # if input not found then set to default
            ntkP = "<p>" + content + "</p><br>\n"

    global ntk_ContMain
    ntk_ContMain += ntkP

    return ntkP


def makeTitle(authorNames, date=None, dateFormat=None):
    """Adds a title section in the Notaker document.

    Args:
        authorNames (dict): The author/s of the Notaker document as a dict, {1: ["FirstName_N", "Surname_N"] ... }.
        date (dict, optional): The creation date the Notaker document, {"month": "", "day": "", "year": ""}. Defaults to None.
        dateFormat (int, optional): Specifies what date format will be used. Defaults to year-month date format.
    """
    # creates a title for the Notaker file after ntk_ContGen
    global ntk_ContMakeTitle

    # code for name formatting

    authorFirstName = {}
    authorSurname = {}

    titleAuthor = ""

    for author in range(1, len(authorNames) + 1):
        # first name of author
        # save in authorFirstName dictionary
        authorFirstName[author] = authorNames[author][0]

        # surname of author
        # save in authorSurname dictionary
        authorSurname[author] = authorNames[author][1]

    titleDate = ""

    if date is None:
        monthNames = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        # if no date is specified, get the current month and year

        titleYear = dt.today().year
        titleYear = str(titleYear)

        titleMonth = dt.today().month
        # convert month to month name
        titleMonth = monthNames[titleMonth - 1]

        titleDate = titleMonth + " " + titleYear

    else:
        # if a date is specified, use it.
        titleYear = date["year"]

        titleDay = date["day"]

        titleMonth = date["month"]

    if date is not None:
        # only allow date formatting if dates (day, month, and year) is specified
        if dateFormat == 1:
            # dateFormat 1 is Month DD, YYYY
            titleDate = titleMonth + " " + titleDay + ", " + titleYear
        elif dateFormat == 2:
            # dateFormat 2 is YYYY
            titleDate = titleYear
        else:
            # if input not found then set to default
            titleDate = titleYear + " " + titleMonth
    else:
        # if no date format is specified, set the date format to the default (Month YYYY)
        titleDate = titleYear + " " + titleMonth

    # add the title

    # <h2><b> titleAuthor </b></h2>
    # <h2><b> titleDate </b></h2>

    # count authors to check if we're going to use et al. and <abbr>
    titleAuthor += "<h2><b>"
    if len(authorNames) >= 6:
        titleAuthor += authorFirstName[1] + " " + authorSurname[1] + '<abbr title="'
        for i in range(2, len(authorNames) + 1):
            if i == len(authorNames):
                titleAuthor += authorFirstName[i] + " " + authorSurname[i]
            else:
                titleAuthor += authorFirstName[i] + " " + authorSurname[i] + ", "
        titleAuthor += '"> et al. </abbr>'
    else:
        for i in range(1, len(authorNames) + 1):
            if i == len(authorNames):
                titleAuthor += authorFirstName[i] + " " + authorSurname[i]
            else:
                titleAuthor += authorFirstName[i] + " " + authorSurname[i] + ", "

    titleAuthor += "</b></h2>\n"

    titleDate = "<h2><b>" + titleDate + "</b></h2>\n"

    ntk_ContMakeTitle = titleAuthor + titleDate


def lightUpBlock(content, textColor=None, highlightColor=None):
    """Creates a highlighted text block. That automatically opens and closes.

    Args:
        content (str): This is the text displayed in the highlighted text block.
        textColor (str, optional): Specifies the font color. Defaults to black.
        highlightColor (str, optional): Specifies the highlight color. Defaults to yellow.
    """
    # highlight block text with given content

    global ntk_ContMain

    # check if textColor is specified
    if textColor is None:
        # if text color is not specified, set to default
        color = "color: " + "black" + ";"
    else:
        # if text color is specified, use it
        color = "color: " + textColor + ";"

    # check if highlightColor is specified
    if highlightColor is None:
        # if highlight color is not specified, set to default
        bgColor = "background-color: " + "yellow"
    else:
        # if highlightColor is specified, use it
        bgColor = "background-color: " + highlightColor

    ntk_ContMain += '<div style="' + color + bgColor + '">' + content + "</div>"


def lightUpBlockS(textColor=None, highlightColor=None):
    """Opens a highlighted text block. That does not close immediately.

    Args:
        textColor (str, optional): Specifies the font color. Defaults to black.
        highlightColor (str, optional): Specifies the highlight color. Defaults to yellow.
    """
    # start highlighting block
    # not only does it highlight the text, but it highlights the whole line where the text is located

    global ntk_ContMain

    # check if textColor is specified
    if textColor is None:
        # if text color is not specified, set to default
        color = "color: " + "black" + ";"
    else:
        # if text color is specified, use it
        color = "color: " + textColor + ";"

    # check if highlightColor is specified
    if highlightColor is None:
        # if highlight color is not specified, set to default
        bgColor = "background-color: " + "yellow"
    else:
        # if highlightColor is specified, use it
        bgColor = "background-color: " + highlightColor

    ntk_ContMain += '<div style="' + color + bgColor + '">'


def lightUpBlockE():
    """Closes the highlighted text box created."""
    # End highlighting block

    global ntk_ContMain

    ntk_ContMain += "</div>"


def lightUp(content, textColor=None, highlightColor=None):
    """Highlights text

    Args:
        content (str): This is the text displayed with highlight.
        textColor (str, optional): Specifies the font color. Defaults to black.
        highlightColor (str, optional): Specifies the highlight color. Defaults to yellow.
    """
    # highlight text with given content

    global ntk_ContMain

    # check if textColor is specified
    if textColor is None:
        # if text color is not specified, set to default
        color = "color: " + "black" + ";"
    else:
        # if text color is specified, use it
        color = "color: " + textColor + ";"

    # check if highlightColor is specified
    if highlightColor is None:
        # if highlight color is not specified, set to default
        bgColor = "background-color: " + "yellow"
    else:
        # if highlightColor is specified, use it
        bgColor = "background-color: " + highlightColor

    ntk_ContMain += '<span style="' + color + bgColor + '">' + content + "</span>"


def note(content, borderColor=None, textColor=None, autoHide=None, summaryText=None):
    """Creates a blockquote

    Args:

        content (str): This is the text displayed in the highlighted text block.
        borderColor (str, optional): Specified the blockquote left border color. Defaults to red.
        textColor (str, optional): Specifies the font color. Defaults to black.
        autoHide (bool, optional): Wraps the blockquote in a togglable show and hide switch. Defaults to False.
        summaryText (str, optional): This is the text displayed when the blockquote toggle is set to hide. Defaults to 'Notes:' .

    Returns:
        This returns the complete (formatted) note in html format.
    """
    # create a note
    noteContent = ""

    # check if borderColor is specified
    if borderColor is not None:
        # if border color is specified, use it
        borderStyle = "border-left: 5px solid " + borderColor + "; "
    else:
        # if border color is not specified, set to default (red)
        borderStyle = "border-left: 5px solid red; "

    # check if color is specified
    if textColor is not None:
        color = "color: " + textColor
    else:
        # if color is not specified, set to default
        color = "color: black"

    global ntk_ContMain

    blockQuoteStart = '<blockquote style="' + borderStyle + color + '">'
    blockQuoteEnd = "</blockquote>"

    if autoHide == False:
        # if autoHide is False, do not auto hide the note
        noteContent += blockQuoteStart

        noteContent += '<p style="margin-left: 10px">'

        noteContent += content

        noteContent += "</p>"

        noteContent += blockQuoteEnd

        ntk_ContMain += noteContent
    elif autoHide == True:
        # if autoHide is True, auto hide the note

        noteContent += "<details>"

        # check if there is a summaryText specified
        if summaryText is not None:
            # if there is summaryText specified, use it
            noteContent += "<summary>" + summaryText + "</summary>"
        else:
            # if there is no summaryText specified, use default
            noteContent += "<summary>Notes:</summary>"

        noteContent += blockQuoteStart

        noteContent += '<p style="margin-left: 10px">'

        noteContent += content

        noteContent += "</p>"

        noteContent += blockQuoteEnd

        noteContent += "</details>"

        ntk_ContMain += noteContent
    else:
        # if other input is given, use default
        noteContent += blockQuoteStart

        noteContent += '<p style="margin-left: 10px">'

        noteContent += content

        noteContent += "</p>"

        noteContent += blockQuoteEnd

        ntk_ContMain += noteContent

    return noteContent


class shortcutsClass:
    """Contains all the function needed for Notaker shortcuts."""

    def __init__(self):
        # count how many shortcuts are there
        self.shortcutCount = 1
        # dictionary filled with the shortcuts
        # sample: {1: ["Address", "Value"], 2: ["Address_2", "Value_2"] ... }
        self.shortcutList = {}

    def addShortcut(self, address, value):
        """Add a shortcut to the shortcut dictionary

        Args:
            address (str): The address (@, $, `!,`@, `$) of the shortcut.
            value (str): The value of the shortcut.
        """
        # adds a shortcut to the shortcut list
        # check if the key provided has an address

        if "@" in address or "$" in address or "`!" in address or "`@" in address or "`$" in address:
            # key already has an address
            self.shortcutList[self.shortcutCount] = [address, value]
        else:
            # key doesnt have an address
            # set a default address to the key
            address = "@" + address
            self.shortcutList[self.shortcutCount] = [address, value]

        # append 1 to the value of shortcutCount
        self.shortcutCount += 1

    def mergeShortcut(self, dictionary):
        """Merge the shortcut dictionary with an existing dictionary.

        Args:
            dictionary (dict): The dictionary that will be merged with the shortcut dictionary.
        """
        # merge a dictionary with the shortcut list
        self.shortcutList = self.shortcutList | dictionary

    def viewShortcut(self, printList=None, key=None):
        """Returns the shortcut dictionary.

        Args:
            printList (bool, optional): Prints shortcut dictionary. Defaults to False.
            key (str, optional): Specifies what shortcut will be returned. Defaults to None.

        Returns:
            The shortcut dictionary.
        """
        # lets the user view the shortcut list or a specific shortcut
        if key is None:
            # if key is none, return all the shortcuts
            if printList == True:
                # if print is true, print and return the shortcuts
                print(self.shortcutList)
                return self.shortcutList
            else:
                # if print is false, return the shortcuts
                return self.shortcutList
        else:
            # if key is not none, return the specific shortcut
            if printList == True:
                # if print is true, print and return the specific shortcut
                print(self.shortcutList[key])

    def viewRangeShortcut(self, rangeMin, rangeMax, printList=None):
        """Returns a range of keys requested in the shortcut dictionary.

        Args:
            rangeMin (str): The lowest key value requested.
            rangeMax (str): The highest key value requested.
            printList (bool, optional): Prints the range requested in the shortcut dictionary. Defaults to False.

        Returns:
            The range of shortcut dictionary
        """
        # lets the user view a range of shortcuts
        for key in range(rangeMin, rangeMax + 1):
            # for each key in range, print the shortcut
            # check if printList is not None
            if printList is None:
                # if printList is None, return the shortcut
                return self.shortcutList[key]
            else:
                # if printList is not None, print the shortcut
                if printList == True:
                    # if printList is True, print the shortcut
                    print(self.shortcutList[key])
                elif printList == False:
                    # if printList is False, return the shortcut
                    return self.shortcutList[key]
                else:
                    # if printList is not True or False, print the shortcut
                    print(self.shortcutList[key])

    def readMain(self):
        """Reads the ntk_ContMain variable and replaces all shortcuts used with their corresponding value."""
        # read the ntk_ContMain variable (or the main content of the Notaker file created)
        # and check for any shortcuts, and replace the shortcut address with the value
        global ntk_ContMain

        # replace all address symbols (@,$,`!,`@,`$) to "__SHORTCUT__"
        ID = "__SHORTCUT__"

        updated_ContMain = (
            ntk_ContMain.replace("$", ID).replace("@", ID).replace("`@", ID).replace("`$", ID)
        )

        for key in range(1, len(self.shortcutList) + 1):
            # iterate for each key in the shortcut list

            # {key: [shortcutAddress, shortcutValue]

            # give the value of the shortcut value to shortcutValue
            shortcutValue = self.shortcutList[key][1]

            # check if the shortcut address is in the content then replace the key with the value
            matchWhole = r"\b" + ID + str(key) + r"\b"

            final_ntk_ContMain = re.sub(matchWhole, shortcutValue, updated_ContMain)
            updated_ContMain = final_ntk_ContMain
            ntk_ContMain = final_ntk_ContMain


class automationClass:
    def autoLink(self, content):
        """Automatically creates the hyperlink reference, id attribute, and increments the ntk_headCount variable.

        Args:
            content (str): This will be set as the hyperlink URL address.
        """
        headerClass().makeLink(content)
        headerClass().makeId(content)
        # increment the headerCount by 1
        global ntk_headCount
        ntk_headCount += 1
