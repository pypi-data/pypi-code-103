# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
import shutil


class CopyError(Exception):
    pass


def copy_page(page, site):
    url = page.relurl.strip("/")
    output_path = os.path.join(site.config.output, url)

    if os.path.exists(output_path):
        raise CopyError(f"File exists: {output_path}")

    target_dir = os.path.dirname(output_path)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(page.source.path, target_dir)
