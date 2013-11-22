#!/usr/bin/env python
# Copyright (C) 2012-2013  Xavier Garrido <garrido@lal.in2p3.fr>
#
# This file is part of qsubmit.
#
# Qsubmit is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

import os, sys, stat
import subprocess
import time
import datetime
import configparser
import logging
import argparse
import re
import paramiko

USERNAME = os.environ['USER']
PASSWORD = 'lol'

class BaseSetup:
    """Base class for defining configuration setup"""
    def __init__ (self, test_ = False):
        self._test_   = test_
        self._logger_ = logging.getLogger ()
        self._script_ = ''

    def parse (self, config_file_):
        """Parsing the configuration file with configparser object"""
        a_config = configparser.ConfigParser ()
        a_config.read (config_file_)

        # Get setup :
        self._default_setup_ = a_config['config']['default_setup']
        self._logger_.debug ('Default setup is ' + self._default_setup_)

        # Get software script :
        self._cadfael_script_ = a_config['config'].get ('cadfael_script', fallback='')
        self._bayeux_script_  = a_config['config'].get ('bayeux_script' , fallback='')
        self._channel_script_ = a_config['config'].get ('channel_script', fallback='')
        self._falaise_script_ = a_config['config'].get ('falaise_script', fallback='')
        self._logger_.debug ('Cadfael script = ' + self._cadfael_script_)
        self._logger_.debug ('Bayeux  script = ' + self._bayeux_script_)
        self._logger_.debug ('Channel script = ' + self._channel_script_)
        self._logger_.debug ('Falaise script = ' + self._falaise_script_)
        # or software directory :
        self._cadfael_directory_ = a_config['config'].get ('cadfael_directory', fallback='')
        self._bayeux_directory_  = a_config['config'].get ('bayeux_directory' , fallback='')
        self._channel_directory_ = a_config['config'].get ('channel_directory', fallback='')
        self._falaise_directory_ = a_config['config'].get ('falaise_directory', fallback='')
        self._logger_.debug ('Cadfael directory = ' + self._cadfael_directory_)
        self._logger_.debug ('Bayeux  directory = ' + self._bayeux_directory_)
        self._logger_.debug ('Channel directory = ' + self._channel_directory_)
        self._logger_.debug ('Falaise directory = ' + self._falaise_directory_)

        if not self._cadfael_script_ and not self._cadfael_directory_:
            raise ValueError ('No Cadfael script nor directory have been set !')
        if not self._bayeux_script_ and not self._bayeux_directory_:
            raise ValueError ('No Bayeux script nor directory have been set !')
        if not self._channel_script_ and not self._channel_directory_:
            raise ValueError ('No Channel script nor directory have been set !')
        if not self._falaise_script_ and not self._falaise_directory_:
            raise ValueError ('No Falaise script nor directory have been set !')

        if self._default_setup_ in 'lyon':
            # Get job resources parameters:
            self._use_hpss_   = a_config['resources'].getboolean ('use_hpss',   fallback=False)
            self._use_sps_    = a_config['resources'].getboolean ('use_sps',    fallback=False)
            self._use_xrootd_ = a_config['resources'].getboolean ('use_xrootd', fallback=False)
            self._memory_     = a_config['resources'].getfloat ('memory',       fallback=0.0)
            self._cpu_time_   = a_config['resources'].get ('cpu_time',          fallback='00:00:00')
            self._space_size_ = a_config['resources'].getfloat ('space_size',   fallback=0.0)
            self._logger_.debug ('Use HPSS         = ' + str (self._use_hpss_))
            self._logger_.debug ('Use SPS          = ' + str (self._use_sps_))
            self._logger_.debug ('Use xrootd       = ' + str (self._use_xrootd_))
            self._logger_.debug ('CPU time value   = ' + str (self._cpu_time_))
            self._logger_.debug ('Memory value     = ' + str (self._memory_))
            self._logger_.debug ('Space size value = ' + str (self._space_size_))

        # Getting commands to be executed:
        self._pre_command_  = a_config['command'].get ('pre_command',  fallback='')
        self._run_command_  = a_config['command'].get ('run_command',  fallback='')
        self._post_command_ = a_config['command'].get ('post_command', fallback='')
        self._logger_.debug ('Pre command  = ' + self._pre_command_)
        self._logger_.debug ('Run command  = ' + self._run_command_)
        self._logger_.debug ('Post command = ' + self._post_command_)

        # # Getting jobs setup:
        self._nbr_jobs_         = a_config['jobs'].get ('nbr_jobs',         fallback=0)
        self._nbr_pending_jobs_ = a_config['jobs'].get ('nbr_pending_jobs', fallback=100)
        self._script_directory_ = a_config['jobs'].get ('script_directory', fallback='')
        self._script_prefix_    = a_config['jobs'].get ('script_prefix',    fallback='')
        self._script_extension_ = a_config['jobs'].get ('script_extension', fallback='.sh')
        self._logger_.debug ('Number of jobs         = ' + self._nbr_jobs_)
        self._logger_.debug ('Number of pending jobs = ' + self._nbr_pending_jobs_)
        self._logger_.debug ('Script prefix          = ' + self._script_prefix_)
        self._logger_.debug ('Script directory       = ' + self._script_directory_)
        self._logger_.debug ('Script extension       = ' + self._script_extension_)

    def _build_header (self):
        header = '#!/bin/bash' + os.linesep
        header += os.linesep
        header += '##########################' + os.linesep
        header += '#'
        header += '    ' + datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M') + '    '
        header += '#'
        header += os.linesep
        header += '##########################' + os.linesep

        if self._default_setup_ in 'lyon':
            header += os.linesep + '# ccage options'                 + os.linesep
            # header += '#$ -j y'                                      + os.linesep
            # header += '#$ -P P_nemo'                                 + os.linesep
            header += '#$ -m be'                                     + os.linesep
            header += '#$ -l hpss='  + str (int (self._use_hpss_))   + os.linesep
            header += '#$ -l sps='   + str (int (self._use_sps_))    + os.linesep
            header += '#$ -l xrootd='+ str (int (self._use_xrootd_)) + os.linesep
            header += '#$ -l ct='    + str (self._cpu_time_)         + os.linesep
            header += '#$ -l vmem='  + str (self._memory_) + 'M'     + os.linesep
            header += '#$ -l fsize=' + str (self._space_size_) + 'G' + os.linesep
        self._logger_.debug ('Header dump:' + header)
        self._script_ += header


    def _build_footer (self):
        footer = os.linesep
        footer += '##########################' + os.linesep
        footer += os.linesep
        footer += 'cat << EOF' + os.linesep
        footer += os.linesep
        footer += self._script_
        footer += os.linesep
        footer += 'EOF' + os.linesep
        footer += os.linesep
        footer += '##########################' + os.linesep
        self._script_ += footer

    def _build_source (self):
        # Define 'source' command:
        cmd = '' + os.linesep

        # Setting setup file to be sourced:
        if self._cadfael_script_:
            cmd += 'source ' + self._cadfael_script_ + ' && do_cadfael_all_setup' + os.linesep
        if self._bayeux_script_:
            cmd += 'source ' + self._bayeux_script_ + ' && do_bayeux_all_setup' + os.linesep
        if self._channel_script_:
            cmd += 'source ' + self._channel_script_ + ' && do_channel_all_setup' + os.linesep
        if self._falaise_script_:
            cmd += 'source ' + self._falaise_script_ + ' && do_falaise_all_setup' + os.linesep

        # Bayeux setup:
        if not self._bayeux_script_:
            # Things are getting more complicated in this case: order matters
            components = [ 'datatools',
                           'brio',
                           'cuts',
                           'mygsl',
                           'geomtools',
                           'genbb_help',
                           'genvtx',
                           'materials',
                           'trackfit' ]
            for icompo in components:
                cmd += 'source ' + self._bayeux_directory_ + '/' + icompo + \
                       '/__install*/etc/' + icompo.lower () + \
                       '_setup.sh && do_' + icompo.lower () + '_setup' + os.linesep

        # Channel setup:
        if not self._channel_script_:
            # Things are getting more complicated in this case: order matters
            components = [ 'TrackerPreClustering',
                           'CellularAutomatonTracker',
                           'TrackerClusterPath' ]
            for icompo in components:
                cmd += 'source ' + self._channel_directory_ + '/' + icompo + \
                       '/__install*/etc/' + icompo.lower () + \
                       '_setup.sh && do_' + icompo.lower () + '_setup' + os.linesep

        # Falaise setup:
        if not self._falaise_script_:
            # Things are getting more complicated in this case: order matters
            components = [ 'sngeometry',
                           'sncore',
                           'sngenvertex',
                           'sngenbb',
                           'sng4',
                           'snreconstruction',
                           'snvisualization',
                           'snanalysis' ]

            for icompo in components:
                cmd += 'source ' + self._falaise_directory_ + '/' + icompo + \
                       '/__install*/etc/' + icompo.lower () + \
                       '_setup.sh && do_' + icompo.lower () + '_setup' + os.linesep

        self._logger_.debug ('Source file dump:' + cmd)
        self._script_ += cmd

    def _build_commands (self):
        command  = os.linesep
        command += '##########################' + os.linesep
        command += os.linesep
        command += self._pre_command_  + os.linesep
        command += self._run_command_  + os.linesep
        command += self._post_command_ + os.linesep
        command += os.linesep
        command += '##########################' + os.linesep
        self._logger_.debug ('Commands dump:' + command)
        self._script_ += command

    def _build (self):
        # Create an header
        self._build_header ()

        # Source config
        self._build_source ()

        # Commands
        self._build_commands ()

        # Create footer
        self._build_footer ()

#     def _replace_variable (self, job_number_ = -1):
#         if job_number_ == -1:
#             print "ERROR: qsubmit::Setup::_replace_variable: Job number is invalid !"
#             sys.exit (2)

#         local_script = self._script_
#         self._script_ = local_script.replace ('@JOB_NUMBER@', str (job_number_))

    def submit (self):
        self._logger_.info ('Generating ' + self._nbr_jobs_ + ' job(s) to ' + self._default_setup_)

        # Build the script:
        self._build ()

        # Open ssh connection
        try:
            self._logger_.debug ('Username = ' + USERNAME + ' password = ' + PASSWORD)
            ssh = paramiko.SSHClient ()
            ssh.load_system_host_keys ()
            ssh.set_missing_host_key_policy (paramiko.WarningPolicy ())
            if self._default_setup_ in 'lyon':
                self._logger_.info ('Connecting to ccage.in2p3.fr...')
                ssh.connect (hostname='ccage.in2p3.fr',
                             username=USERNAME,
                             password=PASSWORD)


            for ijob in range (int (self._nbr_jobs_)):
                self._logger_.info ('Submiting job #' + str (ijob) + '...')

                # # Replacing prefixed variable with @XXX@ label
                # self._replace_variable (ijob)

                # Expand path
                self._script_directory_ = os.path.expandvars (self._script_directory_)
                self._logger_.debug ('Script directory is ' + self._script_directory_)

                # Temporary directory for storing script file
                tmp_dir = os.path.expandvars ('/tmp/${USER}/qsubmit.d')
                if not os.path.exists (tmp_dir):
                    os.makedirs (tmp_dir)

                job_name         = self._script_prefix_ + '_' + str (ijob)
                script_file_name = job_name + self._script_extension_
                script_tmp_path  = tmp_dir + '/' + script_file_name

                script_file = open (script_tmp_path, 'w')
                script_file.write (self._script_)
                script_file.close ()

                self._logger_.debug ('Creating remote path ' + self._script_directory_)
                ssh.exec_command ('mkdir -p ' + self._script_directory_)
                remote_file_path = self._script_directory_ + '/' + script_file_name
                self._logger_.debug ('Copying file ' + script_tmp_path + ' to ' + remote_file_path)
                sftp = ssh.open_sftp ()
                sftp.put (script_tmp_path, remote_file_path)
                sftp.close ()
                ssh.exec_command ('chmod 755 ' + remote_file_path)
                if self._test_:
                    self._logger_.debug ('This is test mode')
                else:
                    qsub_cmd = ''
                    qstat_cmd = ''
                    if self._default_setup_ in 'lyon':
                        sge_cmd = 'export SGE_ROOT=/opt/sge;' \
                                  'export SGE_CELL=ccin2p3;'
                        qprefix_cmd = '/opt/sge/bin/lx-amd64/'

                        qstat_cmd = sge_cmd + qprefix_cmd + 'qstat | wc -l'
                        qsub_cmd = sge_cmd + qprefix_cmd              \
                                   + 'qsub'                           \
                                   + ' -j y -P P_nemo'                \
                                   + ' -N ' + job_name                \
                                   + ' -o ' + self._script_directory_ \
                                   + ' ' + remote_file_path

                    self._logger_.debug ('qsub command = ' + qsub_cmd)
                    ssh.exec_command (qsub_cmd)

                    while True:
                        stderr, stdout, stdin = ssh.exec_command (qstat_cmd)
                        nbr_pending_jobs = re.sub('[b\'n\\\]','', str (stdout.read()))
                        if int (nbr_pending_jobs) < self._nbr_pending_jobs_:
                            self._logger_.debug ('Number of pending jobs is ' + nbr_pending_jobs)
                            break
                            self._logger_.info ('Too much pending jobs... Waiting...')
                            time.sleep (60)
        except Exception as e:
            self._logger_.error ('Caught exception: %s %s' % (e.__class__, e))
            try:
                ssh.close ()
            except:
                pass
                sys.exit(1)

# Main function:
def main ():

    parser = argparse.ArgumentParser (description = 'A python script for running SuperNEMO batch simulations')
    parser.add_argument ('--log',
                         choices = ['critical', 'error', 'warning', 'info', 'debug'],
                         default = 'warning',
                         help = 'logging level')
    parser.add_argument ('--test', action = 'store_true',
                         help = 'only generate file but do not run batch process')
    parser.add_argument ('--config', required = True,
                         help = 'configuration file (mandatory)')
    parser.add_argument ('--username', default = os.environ['USER'],
                         help = 'username for remote connection')
    parser.add_argument ('--password', default = '',
                         help = 'password for remote connection')
    parser.add_argument ('--nbr-pending-jobs', default = 200,
                         help = 'maximum number of pending jobs before resubmitting')
    args = parser.parse_args ()

    # Setting logging level
    numeric_level = getattr(logging, args.log.upper(), None)
    logging.basicConfig(format = '[%(levelname)s:%(module)s::%(funcName)s:%(lineno)d] %(message)s',
                        level = numeric_level)

    global PASSWORD, USERNAME
    USERNAME = args.username
    PASSWORD = args.password

    try:
        setup = BaseSetup (args.test)
        setup.parse (args.config)
        setup.submit ()
    except Exception as e:
        logging.getLogger ().error ('Caught exception: %s' % e)
        sys.exit (1)

# script:
if __name__ == '__main__':
    main ()

# end of qsubmit.py
