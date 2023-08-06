#
# fwrlm.py
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
"""Manages FireWorks rocket launchers and associated scripts as daemons."""

import os
import subprocess
import time

from .base import FireWorksRocketLauncherManager


class DummyManager(FireWorksRocketLauncherManager):
    """Testing purpose daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix='.dummy.')

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc,"dummy_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc,"dummy_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """Simple system shell dummy while loop for testing purposes"""
        args = ['while [ True ]; do printf "."; sleep 5; done']
        self.logger.debug("Evoking '{cmd:s}'".format(cmd=' '.join(args)))
        p = subprocess.Popen(args, cwd=self.launchpad_loc, shell=True)
        outs, errs = p.communicate()
        self.logger.debug("Subprocess exited with return code = {}"
             .format(p.returncode))


class SSHTunnelManager(FireWorksRocketLauncherManager):
    """Permanent SSH tunnel via paramiko daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix=".ssh_tunnel.{local_port:d}:@{remote_host:s}:{remote_port:d}"
                                           ":{jump_user:s}@{jump_host:}.".format(
                                                local_port = self.local_port,
                                                remote_host = self.remote_host,
                                                remote_port = self.remote_port,
                                                jump_user = self.jump_user,
                                                jump_host = self.jump_host))

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc, "ssh_tunnel_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc, "ssh_tunnel_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """SSH forward based on FWRLM_config.yaml settings."""
        from .utils.ssh_forward import forward
        forward(
            remote_host = self.remote_host,
            remote_port = self.remote_port,
            local_port  = self.local_port,
            ssh_host    = self.jump_host,
            ssh_user    = self.jump_user,
            ssh_keyfile = self.ssh_key,
            ssh_port    = self.ssh_port,
            port_file   = None)


class RLaunchManager(FireWorksRocketLauncherManager):
    """FireWorks rlaunch daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix='.rlaunch.')

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc, "rlaunch_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc, "rlaunch_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """Spawn rlaunch."""
        args = [
            'rlaunch',
            '-l', self.fw_auth_file_path,
            '-w', self.rlaunch_fworker_file,
            '--loglvl', self.loglevel, 'rapidfire',
            '--nlaunches', 'infinite',
            '--sleep', self.rlaunch_interval,
        ]
        args = [a if isinstance(a, str) else str(a) for a in args]
        self.logger.info("Evoking '{cmd:s}'".format(cmd=' '.join(args)))
        p = subprocess.Popen(args, cwd=self.launchpad_loc)
        outs, errs = p.communicate()
        self.logger.info("Subprocess exited with return code = {}"
             .format(p.returncode))


class QLaunchManager(FireWorksRocketLauncherManager):
    """FireWorks qlaunch daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix='.qlaunch.')

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc,"qlaunch_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc,"qlaunch_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """Spawn qlaunch."""
        args = [
            'qlaunch', '-r',
            '-l', self.fw_auth_file_path,
            '-w', self.qlaunch_fworker_file,
            '-q', self.qadapter_file,
            '--loglvl', self.loglevel, 'rapidfire',
            '--nlaunches', 'infinite',
            '--sleep', self.qlaunch_interval,
        ]
        args = [a if isinstance(a, str) else str(a) for a in args]
        self.logger.info("Evoking '{cmd:s}'".format(cmd=' '.join(args)))
        p = subprocess.Popen(args, cwd=self.launchpad_loc)
        outs, errs = p.communicate()
        self.logger.info("Subprocess exited with return code = {}"
             .format(p.returncode))


class MLaunchManager(FireWorksRocketLauncherManager):
    """FireWorks rlaunch multi daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix='.mlaunch.')

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc, "mlaunch_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc, "mlaunch_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """Spawn raunch multi."""
        args = [
            'rlaunch',
            '-l', self.fw_auth_file_path,
            '-w', self.rlaunch_fworker_file,
            '--loglvl', self.loglevel, 'multi', self.rlaunch_multi_nprocesses,
            '--nlaunches', 'infinite',
            '--sleep', self.rlaunch_interval,
        ]
        args = [a if isinstance(a, str) else str(a) for a in args]
        self.logger.info("Evoking '{cmd:s}'".format(cmd=' '.join(args)))
        p = subprocess.Popen(args, cwd=self.launchpad_loc)
        outs, errs = p.communicate()
        self.logger.info("Subprocess exited with return code = {}"
             .format(p.returncode))


class LPadRecoverOfflineManager(FireWorksRocketLauncherManager):
    """FireWorks recover offline loop daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix='.lpad_recover_offline.')

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc, "lpad_recover_offline_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc, "lpad_recover_offline_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """Spawn recover offline loop."""
        args = [
            'lpad',
            '-l', self.fw_auth_file_path,
            '--loglvl', self.loglevel,
            'recover_offline',
            '-w', self.qlaunch_fworker_file,
        ]
        args = [a if isinstance(a, str) else str(a) for a in args]
        self.logger.info("Evoking '{cmd:s}' repeatedly in a loop"
            .format(cmd=' '.join(args)))

        while True:
            p = subprocess.Popen(args, cwd=self.launchpad_loc)
            outs, errs = p.communicate()
            self.logger.info("Subprocess exited with return code = {}"
                .format(p.returncode))
            time.sleep(self.lpad_recover_offline_interval)


class LPadWebGuiManager(FireWorksRocketLauncherManager):
    """FireWorks web gui daemon."""

    @property
    def pidfile_name(self):
        return super().pidfile_name(prefix='.lpad_webgui.', suffix=':{port:}'.format(port=self.webgui_port))

    @property
    def outfile_name(self):
        return os.path.join(self.logdir_loc,"webgui_{:s}.out"
            .format(self.timestamp))

    @property
    def errfile_name(self):
        return os.path.join(self.logdir_loc,"webgui_{:s}.err"
            .format(self.timestamp))

    def spawn(self):
        """Spawn webgui."""
        args = [
            'lpad', 'webgui',
            '--server_mode', '--nworkers', 1,
            '--webgui_username', self.webgui_username,
            '--webgui_password', self.webgui_password,
        ]
        args = [a if isinstance(a, str) else str(a) for a in args]
        self.logger.info("Evoking '{cmd:s}'".format(cmd=' '.join(args)))
        p = subprocess.Popen(args, cwd=self.launchpad_loc)
        outs, errs = p.communicate()
        self.logger.info("Subprocess exited with return code = {}"
             .format(p.returncode))
