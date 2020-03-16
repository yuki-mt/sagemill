from typing import Dict
import boto3
import docker
import base64
from botocore.exceptions import ClientError
from abc import ABCMeta, abstractmethod
import os
import tempfile
from .converter import Converter
import shutil
import subprocess


class DockerBuilder(metaclass=ABCMeta):
    def __init__(self, dest_dir: str):
        self.dest_dir = dest_dir
        self.docker_client = docker.from_env()
        self.ecr = boto3.client('ecr')
        self.region = boto3.session.Session().region_name
        self.account_num = boto3.client('sts').get_caller_identity().get('Account')

    @abstractmethod
    def create_template(self) -> None:
        pass

    def generate_requirements(self, notebook: str):
        filepath = os.path.join(self.dest_dir, 'requirements.txt')
        if os.path.exists(filepath):
            os.remove(filepath)

        with tempfile.TemporaryDirectory() as dname:
            Converter.generate_pyfile(notebook, os.path.join(dname, 'tmp.py'))
            subprocess.run(f'pipreqs {dname}', shell=True)
            shutil.move(os.path.join(dname, 'requirements.txt'), self.dest_dir)

    def build_image(self, notebook: str, image: str, tag: str = 'latest',
                    skip_generate_requirements: bool = False) -> str:
        if not skip_generate_requirements:
            self.generate_requirements(notebook)
        full_name = f'{self.account_num}.dkr.ecr.{self.region}.amazonaws.com/{image}:{tag}'
        self.docker_client.images.build(path=self.dest_dir, tag=full_name)
        return full_name

    def _get_ecr_auth(self) -> Dict[str, str]:
        authorization_token = self.ecr.get_authorization_token()['authorizationData'][0]
        token_bytes = base64.b64decode(authorization_token['authorizationToken'])
        token = token_bytes.decode().split(':')
        return {'username': token[0], 'password': token[1]}

    def push_image(self, name: str):
        repo_name = name.split('/', 1)[1].split(':')[0]
        try:
            self.ecr.create_repository(repositoryName=repo_name)
        except ClientError as e:
            code = e.response['Error']['Code']
            if code != 'RepositoryAlreadyExistsException':
                raise e
        print(self.docker_client.images.push(name, auth_config=self._get_ecr_auth()))
