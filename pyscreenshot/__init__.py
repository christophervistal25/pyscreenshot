from PIL import Image
import logging
import os
import sys

from pyscreenshot.about import __version__
from pyscreenshot.loader import Loader, FailedBackendError
from pyscreenshot.procutil import run_in_childprocess


log = logging.getLogger(__name__)
log.debug('version=%s', __version__)


def _grab_simple(to_file, backend=None, bbox=None, filename=None):
    loader = Loader()
    loader.force(backend)
    backend_obj = loader.selected()

    if to_file:
        return backend_obj.grab_to_file(filename)
    else:
        return backend_obj.grab(bbox)


def coder(im):
    if im:
        data = {
            'pixels': im.tobytes(),
            'size': im.size,
            'mode': im.mode,
        }
        return data


def decoder(data):
    if data:
        im = Image.frombytes(data['mode'], data['size'], data['pixels'])
        return im


def _grab(to_file, childprocess=False, backend=None, bbox=None, filename=None):
    if childprocess:
        log.debug('running "%s" in child process' % backend)
        return run_in_childprocess(_grab_simple, (coder, decoder), to_file, backend, bbox, filename)
    else:
        return _grab_simple(to_file, backend, bbox, filename)


def grab(bbox=None, childprocess=False, backend=None):
    """Copy the contents of the screen to PIL image memory.

    :param bbox: optional bounding box (x1,y1,x2,y2)
    :param childprocess: pyscreenshot can cause an error,
            if it is used on more different virtual displays
            and back-end is not in different process.
            Some back-ends are always different processes: scrot, imagemagick
    :param backend: back-end can be forced if set (examples:scrot, wx,..),
                    otherwise back-end is automatic

    """
    return _grab(to_file=False, childprocess=childprocess, backend=backend, bbox=bbox)


def grab_to_file(filename, childprocess=False, backend=None):
    """Copy the contents of the screen to a file.

    :param filename: file for saving
    :param childprocess: see :py:func:`grab`
    :param backend: see :py:func:`grab`

    """
    return _grab(to_file=True, childprocess=childprocess, backend=backend, filename=filename)


def backends():
    '''Back-end names as a list'''
    return Loader().all_names


def _backend_version(backend):
    loader = Loader()
    loader.force(backend)
    try:
        x = loader.selected()
        v = x.backend_version()
    except Exception:
        v = None
    return v


def backend_version(backend, childprocess=False):
    '''Back-end version'''
    if not childprocess:
        return _backend_version(backend)
    else:
        run_in_childprocess(_backend_version, None, backend)
