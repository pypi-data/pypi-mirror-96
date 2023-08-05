#!/usr/bin/python
"""アプリ作成コマンド

    * アプリのテンプレートを作成する

"""

import os
import shutil
from pathlib import Path

from .init import init_project_dir


class Command:
    def handle(self, argv=None):
        try:
            project_name = argv[0]
        except IndexError:
            raise IndexError("No app name given to command arguments.")
        current_dir = Path(os.getcwd())
        project_dir = current_dir / project_name
        src = Path(os.path.dirname(__file__)) / "../skeleton/app_templates"
        shutil.copytree(src, project_dir, symlinks=False)
