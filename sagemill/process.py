import shutil
import os

from .builder import DockerBuilder


class ProcessImageBuilder(DockerBuilder):
    def __init__(self, dest_dir: str):
        super().__init__(dest_dir)

    def create_template(self) -> None:
        src_dir = os.path.join(os.path.dirname(__file__), 'docker/process')
        shutil.copytree(src_dir, self.dest_dir)
