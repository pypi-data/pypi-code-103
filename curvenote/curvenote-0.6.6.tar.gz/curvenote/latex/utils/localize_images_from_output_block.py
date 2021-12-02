import logging
import os

from ...models import BlockVersion, OutputSummaryKind
from ...utils import fetch
from .index import fetch
from .localize_images import ImageFormats
from .patch_local_images_from_tex_block import patch_local_images_from_tex_block
from .regex import (
    OUTPUT_IMAGE_BLOCK_REGEX,
    OUTPUT_IMAGE_OXA_REGEX,
    OUTPUT_SVG_BLOCK_REGEX,
    OUTPUT_SVG_OXA_REGEX,
)


def localize_images_from_output_block(assets_folder: str, output_version: BlockVersion):
    all_content = ""
    for i, output_summary in enumerate(output_version.outputs):
        if (
            output_summary.kind == OutputSummaryKind.image
            or output_summary.kind == OutputSummaryKind.svg
        ):
            logging.info("Output Summary %s", output_summary.kind)
            if output_summary.kind == OutputSummaryKind.image:
                regex_matchers = [OUTPUT_IMAGE_BLOCK_REGEX, OUTPUT_IMAGE_OXA_REGEX]
            else:
                regex_matchers = [OUTPUT_SVG_BLOCK_REGEX, OUTPUT_SVG_OXA_REGEX]

            patch = patch_local_images_from_tex_block(
                regex_matchers, output_summary.content
            )
            if patch is not None:
                # TODO won't work for non image outputs or multi outputs with
                # mixed image and non image
                if not output_summary.link:
                    raise ValueError(
                        f"OutputSummary {i} in version "
                        f"{output_version.id.project}/{output_version.id.block}/"
                        f"{output_version.id.version} has no download link"
                    )

                fetched_content = fetch(output_summary.link)

                extension = ImageFormats[output_summary.content_type.lower()]
                local_path_with_extension = f"{patch.local_paths[0]}.{extension}"
                patched_content_with_ext = patch.content.replace(
                    patch.local_paths[0], local_path_with_extension
                )
                all_content = all_content + "\n" + patched_content_with_ext

                logging.info("Writing %s", local_path_with_extension)
                with open(
                    os.path.join(assets_folder, local_path_with_extension), "wb+"
                ) as file:
                    file.write(fetched_content)

        elif output_summary.kind == OutputSummaryKind.text:
            logging.info("Output Summary %s", output_summary.kind)
            if output_summary.link:
                # text content can be large and may be stored in a file
                content = fetch(output_summary.link).decode("utf-8")
            else:
                content = output_summary.content
            all_content = (
                all_content + "\n\n" + r"\begin{verbatim}" + content + r"\end{verbatim}"
            )
        else:
            logging.info("WARNING: Unknown Output Summary: %s", output_summary.kind)
            patch = None

    return all_content
