from firstimpression.api.request import give_error_message, request_json
from firstimpression.constants import IMG_EXTENSIONS, VIDEO_EXTENSIONS
from firstimpression.file import create_directories, list_files_dir, purge_directories
from firstimpression.scala import ScalaPlayer


def update_placeholders():
    scala = ScalaPlayer('placeholders')

    url = 'https://fi-api.io/placeholder_images'

    extensions = IMG_EXTENSIONS + VIDEO_EXTENSIONS

    create_directories([scala.content_folder, scala.temp_folder])
    purge_directories([scala.content_folder, scala.temp_folder], 5)

    if len(list_files_dir(scala.content_folder)) == 0:
        response, is_error = request_json(url)

        if is_error:
            message = give_error_message(response)

            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        elements = response.get('data', [])
        elements = [elem for elem in elements if '.' +
                    elem.split('.')[-1] in extensions]

        for elem in elements:
            temp_path = scala.download_media_temp(elem)
            scala.install_content(temp_path)
