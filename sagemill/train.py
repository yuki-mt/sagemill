import shutil
import os

from .converter import Converter
from .builder import DockerBuilder


class TrainImageBuilder(DockerBuilder):
    def __init__(self, dest_dir: str):
        super().__init__(dest_dir)

    def create_template(self) -> None:
        src_dir = os.path.join(os.path.dirname(__file__), 'docker/train')
        shutil.copytree(src_dir, self.dest_dir)

    def build_image(self, notebook: str, image: str, tag: str = 'latest',
                    skip_generate_requirements: bool = False) -> str:
        dest_pyfile = os.path.join(self.dest_dir, 'entrypoint.py')
        Converter.generate_pyfile(notebook, dest_pyfile)
        return super().build_image(notebook, image, tag, skip_generate_requirements)
