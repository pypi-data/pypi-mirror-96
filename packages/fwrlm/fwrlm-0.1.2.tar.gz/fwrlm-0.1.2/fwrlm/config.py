#
# config.py
#
# Copyright (C) 2020 IMTEK Simulation
# Author: Johannes Hoermann, johannes.hoermann@imtek.uni-freiburg.de
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""FireWorksRocketLauncherManager configuration."""

import logging
import os

import monty.serialization  # for reading config files

# configuration handling modeled following
# https://github.com/materialsproject/fireworks/blob/master/fireworks/fw_config.py

FWRLM_CONFIG_FILE_DIR = os.path.join(os.path.expanduser('~'), '.fireworks')
FWRLM_CONFIG_FILE_NAME = 'FWRLM_config.yaml'
FWRLM_CONFIG_FILE_ENV_VAR = 'FWRLM_CONFIG_FILE'

# FireWorks config sample skeleton (static files)
FW_CONFIG_SKEL_PREFIX = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "examples", "fw_config")

# FireWorks config sample templates
FW_CONFIG_TEMPLATE_PREFIX = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates", "fw_config")

FW_CONFIG_PREFIX = os.path.join(os.path.expanduser('~'), ".fireworks")
FW_CONFIG_FILE_NAME = "FW_config.yaml"
FW_AUTH_FILE_NAME = "fireworks_mongodb_auth.yaml"

# default loglevel for launcher scripts
DEFAULT_LOGLEVEL = "DEBUG"

LAUNCHPAD_LOC = os.path.join(os.path.expanduser('~'), "fw_launchpad")
LOGDIR_LOC = os.path.join(os.path.expanduser('~'), "fw_logdir")

# allow multiple rlaunch processes (rlaunch multi)
RLAUNCH_MULTI_NPROCESSES = 4
# OMP_NUM_THREADS = 1

# webgui settings
WEBGUI_USERNAME = "fireworks"
WEBGUI_PASSWORD = "fireworks"
WEBGUI_PORT = 19886

# mongodb and ssh tunnel settings
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
FIREWORKS_DB = 'fireworks'
FIREWORKS_USER = 'fireworks'
FIREWORKS_PWD = 'fireworks'

# ssh tunnel settings
SSH = False
SSH_PORT_REMOTE = 27017
SSH_PORT_LOCAL = 27017
SSH_HOST = 'localhost'
SSH_USER = 'sshclient'
SSH_KEY = os.path.join(os.path.expanduser('~'), ".ssh", "id_rsa")

# tls/ssl encryption settings
SSL = False
SSL_CA_CERTS = os.path.join(os.path.expanduser('~'), ".ssl", "root.pem")
SSL_CERTFILE = os.path.join(os.path.expanduser('~'), ".ssl", "cert.pem")
SSL_KEYFILE = os.path.join(os.path.expanduser('~'), ".ssl", "key.pem")
SSL_PEM_PASSPHRASE = None

# run daemon to periodically check offline runs
# RECOVER_OFFLINE = True

# optional instance identifier (use run and distinguish between different instances in same environment)
INSTANCE = None

# MACHINE-specfific settings
MACHINE = "JUWELS"
SCHEDULER = 'SLURM'

RLAUNCH_FWORKER_FILE = None  # by absolute path, or ...
RLAUNCH_FWORKER_FILE_NAME = None  # ... by file name within FW_CONFIG_PREFIX. Absolute overrides relative.
# if not set explicitly, then stick to automatic convention
# "${FW_CONFIG_PREFIX}/${MACHINE:lowercase}_noqueue_worker.yaml"

QLAUNCH_FWORKER_FILE = None  # by absolute path, or ...
QLAUNCH_FWORKER_FILE_NAME = None  # ... by file name within FW_CONFIG_PREFIX. Absolute overrides relative.
# if not set explicitly, then stick to automatic convention
# "${FW_CONFIG_PREFIX}/${MACHINE:lowercase}_queue_offline_worker.yaml"

QADAPTER_FILE = None  # by absolute path, or ...
QADAPTER_FILE_NAME = None  # ... by file name within FW_CONFIG_PREFIX. Absolute overrides relative.
# if not set explicitly, then stick to automatic convention
# "${FW_CONFIG_PREFIX}/${MACHINE:lowercase}_{SCHEDULER_lowercase}_qadapter_offline.yaml"


def override_user_settings():
    """Read config from standard file (if found) when module imported."""
    logger = logging.getLogger(__name__)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(module_dir)  # FW root dir

    config_paths = []

    test_paths = [
        os.getcwd(),
        os.path.join(os.path.expanduser('~'), ".fireworks"),
        os.path.expanduser('~'),
        root_dir,
    ]

    for p in test_paths:
        fp = os.path.join(p, FWRLM_CONFIG_FILE_NAME)
        if fp not in config_paths and os.path.exists(fp):
            config_paths.append(fp)

    if FWRLM_CONFIG_FILE_ENV_VAR in os.environ \
            and os.environ[FWRLM_CONFIG_FILE_ENV_VAR] not in config_paths:
        if os.path.exists(os.environ[FWRLM_CONFIG_FILE_ENV_VAR]):
            config_paths.insert(0, os.environ[FWRLM_CONFIG_FILE_ENV_VAR])
        else:
            logger.warning(
                "Config '%s' specified via environment variable '%s' does not exist." % (config_paths[0],
                                                                                         FWRLM_CONFIG_FILE_ENV_VAR))

    if len(config_paths) > 1:
        logger.warning("Found many potential paths for {}: {}"
            .format(FWRLM_CONFIG_FILE_NAME, config_paths))
        logger.warning("Choosing as default: {}"
            .format(config_paths[0]))

    if len(config_paths) > 0 and os.path.exists(config_paths[0]):
        overrides = monty.serialization.loadfn(config_paths[0])
        for key, v in overrides.items():
            if key not in globals():
                raise ValueError(
                    'Invalid FWRLM_config file has unknown parameter: {}'
                        .format(key))

            logger.info("Set key : value pair '{}' : '{}'"
                .format(key, v))
            globals()[key] = v
    elif len(config_paths) > 0:
        logger.warning("Selected config '%s' does not exist." % config_paths[0])


def config_to_dict():
    """Convert config in globals() to dict."""
    d = {}
    for k, v in globals().items():
        if k.upper() == k:
            d[k] = v
    return d


def config_keys_to_list():
    """Convert config keys in globals() to list."""
    l = []
    for k in globals().keys():
        if k.upper() == k:
            l.append(k)
    return l


def write_config(path=None):
    """Write config key: value dict to file."""
    path = os.path.join(
        FWRLM_CONFIG_FILE_DIR,
        FWRLM_CONFIG_FILE_NAME) if path is None else path
    monty.serialization.dumpfn(config_to_dict(), path)


def write_config_keys(path):
    """Write list of config keys to file."""
    monty.serialization.dumpfn(config_keys_to_list(), path)


override_user_settings()
