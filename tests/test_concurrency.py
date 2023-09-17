import time
import uuid
from multiprocessing import Process
from pathlib import Path

import docker
import pytest
import requests
from docker.errors import DockerException
from docker.models.containers import Container

try:
    docker_client = docker.from_env()
except DockerException:
    pytest.skip('Docker not available', allow_module_level=True)

test_port = 5001
address = f'http://localhost:{test_port}/'


class Container:
    def __init__(self, workers: int = 4, port: int = test_port):
        self.container = None
        self.port = port
        self.options = {
            'WEB_CONCURRENCY': workers,
            'KIOSK_FQDN': f'localhost:{port}',
            'AUTO_UPDATE': 'True',
        }

    @staticmethod
    def start_docker_container(port: int, options: dict):
        # Build the docker image
        dockerfile_path = str(Path(__file__).parent.parent)
        docker_client.images.build(path=dockerfile_path,
                                   tag='test_feideutstyrbase',
                                   rm=True)

        # Run the docker image
        docker_client.containers.run(
            "test_feideutstyrbase",
            name='test_feideutstyrbase',
            detach=True,
            environment=options,
            ports={'5000/tcp': port},
            remove=True,
        )

    @staticmethod
    def add_mock_data() -> None:
        """Send a POST request to the API to add a category, on a separate process."""
        endpoint = f'{address}/categories'
        c = requests.get(f'{address}', allow_redirects=True).cookies
        requests.put(endpoint, data={'categories': 'category'}, cookies=c, allow_redirects=True)

    def __enter__(self) -> docker.models.containers.Container:
        """Start a docker container with the specified options."""
        Process(target=self.start_docker_container(port=self.port, options=self.options)).start()

        # Wait for the container to spin up
        time.sleep(3)
        self.container = docker_client.containers.get('test_feideutstyrbase')

        # Ensure the container is running and the worker is up
        while 'worker' not in self.container.logs().decode('utf-8'):
            time.sleep(1)

        # Add required mock data for the tests (categories)
        self.add_mock_data()

        # Return the container object
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop the docker container."""
        self.container.stop()
        time.sleep(5)


def add_item(item: dict):
    """Send a POST request to the API to add an item, on a separate process."""
    endpoint = f'{address}/items'
    c = requests.get(f'{address}', allow_redirects=True).cookies
    requests.post(endpoint, data=item, cookies=c, allow_redirects=True)


def get_items_len() -> int:
    """Send a GET request to the API to get the amount of items, on a separate process."""
    endpoint = f'{address}/items'
    c = requests.get(f'{address}', allow_redirects=True).cookies
    response = requests.get(endpoint, cookies=c, allow_redirects=True)
    return len(response.json())


def generate_items(amount: int):
    return [{
        'id': uuid.uuid4().hex,
        'name': 'Item',
        'category': 'category',
    } for _ in range(amount)]


def test_concurrent_requests() -> None:
    with Container(workers=8):
        # Test single request
        old_amount = get_items_len()
        p = Process(target=add_item, args=(generate_items(1)[0],))
        p.start()
        p.join()
        assert get_items_len() == old_amount + 1

        # Test concurrent requests
        amount_of_items = 200
        old_amount = get_items_len()
        processes = [Process(target=add_item, args=(item,)) for item in generate_items(amount_of_items)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        assert get_items_len() == old_amount + amount_of_items
