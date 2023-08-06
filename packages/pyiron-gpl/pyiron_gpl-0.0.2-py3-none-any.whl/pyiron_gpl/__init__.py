__version__ = "0.1.1"
__all__ = []

from pyiron_atomistics.project import Project
from pyiron_base import Notebook, install_dialog, JOB_CLASS_DICT

# Make classes available for new pyiron version
JOB_CLASS_DICT['ElasticMatrixJob'] = 'pyiron_gpl.elastic.elastic'
JOB_CLASS_DICT['PaceMakerJob'] = 'pyiron_gpl.pacemaker.pacemaker'

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


def install():
    install_dialog()
