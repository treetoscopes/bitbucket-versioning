import os
from src.version_manager import VersionManager


def test_version_manager():
    version_manager = VersionManager()
    assert version_manager is not None
    default_version = version_manager.get_version_string()
    assert default_version == "1.0.0"


def test_version_manager_set():
    version_manager = VersionManager()
    assert version_manager is not None
    version_manager.set_version(x=2, y=2, z=2)
    version = version_manager.get_version_string()
    assert version == "2.2.2"


def test_version_manager_env():
    os.environ = {'VERSION_X': 3, 'VERSION_Y': 3, 'VERSION_Z': 3}
    version_manager = VersionManager()
    assert version_manager is not None
    default_version = version_manager.get_version_string()
    assert default_version == "3.3.3"

    image_tag = version_manager.generate_image_tag()
    assert image_tag.startswith('python-app-local-')
    assert image_tag.endswith('-3.3.3')


def test_image_tag():
    # clear the prvious set environment variables
    os.environ = {}
    version_manager = VersionManager()
    assert version_manager is not None
    default_version = version_manager.get_version_string()
    assert default_version == "1.0.0"

    image_tag = version_manager.generate_image_tag()
    assert image_tag.startswith('python-app-local-')
    assert image_tag.endswith('-1.0.0')
    
