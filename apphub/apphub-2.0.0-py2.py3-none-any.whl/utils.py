def save_to_disk(filepath, content):
    """
    Save content to a file
    Args:
        filepath: (str) Path to target file
        content: (BytesIO) Bytes of file

    Returns: (None)

    """
    with open(filepath, 'wb+') as f:
        f.write(content.read())


def clean_response(response_data):
    """
    Take in nested dictionaries from AppHub and respond with key/value pairs of {'bundle_name': ['list', 'of','versions']
    Args:
        response_data: response from AppHub get content calls

    Returns: (dict) in the format of {'bundle_name': ['list', 'of','versions']
    """
    if not isinstance(response_data, list):
        response_data = [response_data]
    clean_data = {}
    [
        clean_data.setdefault(item['swimbundle']['name'], []).append(item['swimbundle'].get('version'))
        for item in response_data
    ]
    return clean_data
