"""HTML, CSS and JavaScript component templates"""



style = """
:root {
    /* Toggle Checkbox */
	--size: 1.3rem;
    --rsize: calc(var(--size) * 0.7);
    --csize: calc(var(--size) * 1.2);
    --dsize: calc(var(--size) * 1.8);
    --offset: calc((var(--size) - var(--rsize)) / 2);
    --shadow: 3px;
    --transition: 0.15s;

    /* Colors */
    --green: #35c171;
    --red: #d73b4d;
}

body {
    margin: 0;
    padding: 2ch;
    font-family: monospace;
}

#markdown-form {
    width: 100%;
    height: 100%;
}


/* ----------------/
 * INLINE ELEMENTS |
 * ----------------/
 */

input[type="text"], textarea {
    width: 100%;
    max-width: 100%;
}


input[type="radio"] {
    margin-right: 2ch;
}
 
div.checkbox, div.radio {    
    /* Vertically center tick and label */
    display: flex;
    align-items: center;
    vertical-align: middle;
    word-wrap: break-word;
}

div.checkbox, div.radio-buttons {
    padding: 0.5rem 0;
}


/* ----------------/
 * TOGGLE CHECKBOX |
 * ----------------/
 */

div.checkbox input[type="checkbox"] {
    margin-right: 1ch;
}

div.checkbox input[type="checkbox"] {
	-webkit-appearance: none;
	-webkit-tap-highlight-color: transparent;

	position: relative;
    vertical-align: middle;

	border: 0;
	outline: 0;
    
	cursor: pointer;
    margin-right: var(--size);
}

div.checkbox input[type="checkbox"]::after {
	content: "";
	width: var(--dsize);
	height: var(--size);
	display: inline-block;
	background: var(--red);
	border-radius: var(--size);
	clear: both;

    transition: var(--transition);
}

div.checkbox input[type="checkbox"]::before {
	content: "";
	width: var(--rsize);
	height: var(--rsize);
	display: block;
	position: absolute;
	left: var(--offset);
	top: var(--offset);
	border-radius: 50%;
	background: white;

    transition: var(--transition);
}

div.checkbox input[type="checkbox"]:checked::before {
	left: calc(var(--dsize) - var(--rsize) - var(--offset));

    transition: var(--transition);
}

div.checkbox input[type="checkbox"]:checked::after {
	background: var(--green);

    transition: var(--transition);
}
"""

script = """
function submitData(methodName) {
    let documents = document.forms['markdown-form'].elements
    let data = {}

    for (let [key, element] of Object.entries(documents)) {
        // Use element name as key if specified
        key = element.name ? element.name : key
        
        // Set the checked state of a checkbox
        if (element.type && element.type == 'checkbox') {
            data[key] = element.checked
        }

        // Set the value of a radio button if it is checked
        else if (element.type && element.type == 'radio') {
            if (element.checked == true) {
                data[key] = element.value
            }
            else if (!(key in data)) {
                data[key] = undefined
            }
        }

        // Return the value for everything else
        else {
            data[key] = element.value
        }
    }

    pywebview.api.submit_data(methodName, data)
}
"""

html = """
<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <script>
                (( script ))
            </script>

            <style>
                (( style ))
            </style>

            <form id="markdown-form">
                (( body ))
            </form>
        </body>
    </html>
""".replace('(( script ))', script)