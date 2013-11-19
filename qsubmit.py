#!/usr/bin/env python
# qsubmit.py
# Author: Xavier Garrido <garrido@lal.in2p3.fr>
# Copyright: 2012 (C) NEMO - LAL (IN2P3/CNRS)

import os, sys
# import subprocess
# import getopt, ConfigParser
import datetime
import configparser
import logging
import argparse

class BaseSetup:
    def __init__ (self):
        self._test_             = False
        self._default_setup_    = ""
        self._cadfael_version_  = "pro"
        self._bayeux_version_   = "trunk"
        self._channel_version_  = "trunk"
        self._falaise_version_  = "trunk"
        self._pre_command_      = ""
        self._run_command_      = ""
        self._post_command_     = ""
        self._nbr_jobs_         = 0
        self._script_directory_ = ""
        self._script_prefix_    = ""
        self._script_extension_ = ".sh"
        self._script_           = ""
        self._logger_ = logging.getLogger ()

    def _parse (self, config_file_):
        a_config = configparser.ConfigParser ()
        a_config.read (config_file_)

        # Get default setup :
        self._default_setup_ = a_config['config']['default_setup']

        if not self._default_setup_ in ("lyon", "lal", "local"):
            raise ValueError ('Default setup ' + self._default_setup_ + ' is not supported !')
        self._logger_.debug ('Default setup is ' + self._default_setup_)

        # Get software version :
        self._cadfael_version_ = a_config['config']['cadfael_version']
        self._bayeux_version_  = a_config['config']['bayeux_version']
        self._channel_version_ = a_config['config']['channel_version']
        self._falaise_version_ = a_config['config']['falaise_version']

        if not self._check_version ():
            raise ValueError ('Checking software version fails!')

        self._logger_.debug ('Cadfael version = ' + self._cadfael_version_)
        self._logger_.debug ('Bayeux  version = ' + self._bayeux_version_)
        self._logger_.debug ('Channel version = ' + self._channel_version_)
        self._logger_.debug ('Falaise version = ' + self._falaise_version_)

        if self._default_setup_ in "lyon":
            # Get job resources parameters:
            self._use_hpss_   = a_config['resources'].getboolean ('use_hpss', fallback=False)
            self._use_sps_    = a_config['resources'].getboolean ('use_sps', fallback=False)
            self._use_xrootd_ = a_config['resources'].getboolean ('use_xrootd', fallback=False)
            self._memory_     = a_config['resources'].getfloat ('memory', fallback=0.0)
            self._cpu_time_   = a_config['resources'].get ('cpu_time', fallback='00:00:00')
            self._space_size_ = a_config['resources'].getfloat ('space_size', fallback=0.0)
            self._logger_.debug ('Use HPSS         = ' + str (self._use_hpss_))
            self._logger_.debug ('Use SPS          = ' + str (self._use_sps_))
            self._logger_.debug ('Use xrootd       = ' + str (self._use_xrootd_))
            self._logger_.debug ('CPU time value   = ' + str (self._cpu_time_))
            self._logger_.debug ('Memory value     = ' + str (self._memory_))
            self._logger_.debug ('Space size value = ' + str (self._space_size_))

        # Getting commands to be executed:
        self._pre_command_  = a_config['command'].get ('pre_command')
        self._run_command_  = a_config['command'].get ('run_command')
        self._post_command_ = a_config['command'].get ('post_command')
        self._logger_.debug ('Pre command  = ' + self._pre_command_)
        self._logger_.debug ('Run command  = ' + self._run_command_)
        self._logger_.debug ('Post command = ' + self._post_command_)

        # # Getting jobs setup:
        # sdir = a_config.get ("jobs", "script_directory")
        # self._script_directory_ = os.path.expandvars (sdir)
        self._nbr_jobs_         = a_config['jobs'].get ('nbr_jobs')
        self._script_directory_ = a_config['jobs'].get ('script_directory')
        self._script_prefix_    = a_config['jobs'].get ('script_prefix')
        self._script_extension_ = a_config['jobs'].get ('script_extension')
        self._logger_.debug ('Number of jobs   = ' + self._nbr_jobs_)
        self._logger_.debug ('Script prefix    = ' + self._script_prefix_)
        self._logger_.debug ('Script directory = ' + self._script_directory_)
        self._logger_.debug ('Script extension = ' + self._script_extension_)

    def _check_version (self):
        if self._cadfael_version_ and self._cadfael_version_ not in ("pro", "trunk"):
            self._logger_.error ('Cadfael version ' + self._cadfael_version_ + ' is unkown')
            return False
        if self._bayeux_version_ and self._bayeux_version_ not in ("pro", "trunk"):
            self._logger_.error ('Bayeux version ' + self._bayeux_version_ + ' is unkown')
            return False
        if self._channel_version_ and self._channel_version_ not in ("pro", "trunk"):
            self._logger_.error ('Channel version ' + self._channel_version_ + ' is unkown')
            return False
        if self._falaise_version_ and self._falaise_version_ not in ("pro", "trunk"):
            self._logger_.error ('Falaise version ' + self._falaise_version_ + ' is unkown')
            return False
        return True

    def _build_header (self):
        header  = "#!/bin/bash" + os.linesep
        header += os.linesep
        header += "##########################" + os.linesep
        header += "#"
        header += "    " + datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M") + "    "
        header += "#"
        header += os.linesep
        header += "##########################" + os.linesep

        if self._default_setup_ in "lyon":
            header += os.linesep + "# ccage options"                 + os.linesep
            # header += "#$ -j y"                                      + os.linesep
            # header += "#$ -P P_nemo"                                 + os.linesep
            header += "#$ -m be"                                     + os.linesep
            header += "#$ -l hpss="  + str (int (self._use_hpss_))   + os.linesep
            header += "#$ -l sps="   + str (int (self._use_sps_))    + os.linesep
            header += "#$ -l xrootd="+ str (int (self._use_xrootd_)) + os.linesep
            header += "#$ -l ct="    + str (self._cpu_time_)         + os.linesep
            header += "#$ -l vmem="  + str (self._memory_) + "G"     + os.linesep
            header += "#$ -l fsize=" + str (self._space_size_) + "G" + os.linesep

        self._script_ += header


#     def _build_footer (self):
#         footer = os.linesep
#         footer += "##########################" + os.linesep
#         footer += os.linesep
#         footer += "cat << EOF" + os.linesep
#         footer += os.linesep
#         footer += self._script_
#         footer += os.linesep
#         footer += "EOF" + os.linesep
#         footer += os.linesep
#         footer += "##########################" + os.linesep
#         self._script_ += footer

#     def _build_commands (self):
#         command  = os.linesep
#         command += "##########################" + os.linesep
#         command += os.linesep
#         command += self._run_command_  + os.linesep
#         command += self._post_command_ + os.linesep
#         command += os.linesep
#         command += "##########################" + os.linesep
#         self._script_ += command

#     def _build_source (self):
#         nemo_base_dir_tmp = ""
#         nemo_pro_dir_tmp  = ""
#         nemo_dev_dir_tmp  = ""

#         cadfael_setup_file = ""
#         bayeux_setup_file  = ""
#         channel_setup_file = ""
#         falaise_setup_file = ""

#         if self._default_setup_ in "lyon":
#             nemo_base_dir_tmp = "/sps/nemo/scratch/garrido/workdir/"
#             nemo_pro_dir_tmp  = nemo_base_dir_tmp + "/supernemo/snware"
#             nemo_dev_dir_tmp  = nemo_base_dir_tmp + "/supernemo/development"
#             cadfael_setup_file = nemo_pro_dir_tmp + \
#                 "/cadfael/install/master/etc/cadfael_setup.sh"
#         elif self._default_setup_ in "lal":
#             nemo_base_dir_tmp = "/exp/nemo/snsw"
#             nemo_pro_dir_tmp  = nemo_base_dir_tmp + "/supernemo/snware"
#             nemo_dev_dir_tmp  = nemo_base_dir_tmp + "/supernemo/development"
#             cadfael_setup_file = nemo_pro_dir_tmp + \
#                 "/cadfael/cadfael/install/0.1.0/etc/cadfael_setup.sh"
#         elif self._default_setup_ in "local":
#             nemo_base_dir_tmp = "/home/garrido/Workdir/NEMO"
#             nemo_pro_dir_tmp  = nemo_base_dir_tmp + "/supernemo/snware"
#             nemo_dev_dir_tmp  = nemo_base_dir_tmp + "/supernemo/development"
#             cadfael_setup_file = nemo_pro_dir_tmp + \
#                 "/cadfael/cadfael/install/0.1.0/etc/cadfael_setup.sh"

#         # Define 'source' command:
#         cmd = "" + os.linesep

#         # Setting setup file to be sourced:
#         if not cadfael_setup_file:
#             pass
#         else:
#             cmd += "source " + cadfael_setup_file + " && do_cadfael_all_setup" + os.linesep

#         # Bayeux setup:
#         if not bayeux_setup_file:
#             if self._bayeux_version_ in "pro":
#                 self._bayeux_version_ = "0.1.0"
#                 bayeux_setup_file = nemo_pro_dir_tmp + "/bayeux/install/" \
#                     + self._bayeux_version_ + "/etc/bayeux_setup.sh"
#             elif self._bayeux_version_ in "trunk":
#                 # Things are getting more complicated in this case: order matters
#                 components = [ "datatools", "brio", "cuts", "mygsl", "geomtools", "genbb_help", "genvtx", "materials", "trackfit" ]

#                 for icompo in components:
#                     cmd += "source " + nemo_dev_dir_tmp + "/bayeux/" + icompo + \
#                         "/__install*/etc/" + icompo.lower () + \
#                         "_setup.sh && do_" + icompo.lower () + "_setup" + os.linesep
#         else:
#             cmd += "source " + bayeux_setup_file + " && do_bayeux_all_setup" + os.linesep

#         # Channel setup:
#         if not channel_setup_file:
#             if self._channel_version_ in "pro":
#                 self._channel_version_ = "0.1.0"
#                 channel_setup_file = nemo_pro_dir_tmp + "/channel/install/" \
#                     + self._channel_version_ + "/etc/channel_setup.sh"
#             elif self._channel_version_ in "trunk":
#                 # Things are getting more complicated in this case: order matters
#                 components = [ "TrackerPreClustering", "CellularAutomatonTracker", "TrackerClusterPath" ]

#                 for icompo in components:
#                     cmd += "source " + nemo_dev_dir_tmp + "/channel/" + icompo + \
#                         "/__install*/etc/" + icompo.lower () + \
#                         "_setup.sh && do_" + icompo.lower () + "_setup" + os.linesep
#         else:
#             cmd += "source " + channel_setup_file + " && do_channel_all_setup" + os.linesep

#         # Falaise setup:
#         if not falaise_setup_file:
#             if self._falaise_version_ in "pro":
#                 self._falaise_version_ = "0.1.0"
#                 falaise_setup_file = nemo_pro_dir_tmp + "/falaise/install/" \
#                     + self._falaise_version_ + "/etc/falaise_setup.sh"
#             elif self._falaise_version_ in "trunk":
#                 # Things are getting more complicated in this case: order matters
#                 components = [ "sngeometry", "sncore", "sngenvertex", "sngenbb", "sng4", "snreconstruction", "snvisualization", "snanalysis" ]

#                 for icompo in components:
#                     cmd += "source " + nemo_dev_dir_tmp + "/falaise/" + icompo + \
#                         "/__install*/etc/" + icompo.lower () + \
#                         "_setup.sh && do_" + icompo.lower () + "_setup" + os.linesep
#         else:
#             cmd += "source " + _setup_file + " && do_falaise_all_setup" + os.linesep

#         self._script_ += cmd

    def _build (self):
        # Create an header
        self._build_header ()

        # # Source config
        # self._build_source ()

        # # Commands
        # self._build_commands ()

        # # Create footer
        # self._build_footer ()

#     def _print (self):
#         print self._script_

#     def _replace_variable (self, job_number_ = -1):
#         if job_number_ == -1:
#             print "ERROR: qsubmit::Setup::_replace_variable: Job number is invalid !"
#             sys.exit (2)

#         local_script = self._script_
#         self._script_ = local_script.replace ('@JOB_NUMBER@', str (job_number_))

#     def _run_pre_command (self):
#         if self._debug_:
#             print "DEBUG: qsubmit::Setup::_run_pre_command: Pre command is", self._pre_command_
#         print "NOTICE: qsubmit::Setup::_run_pre_command: Running 'pre-command'..."
#         subprocess.call (self._pre_command_, shell=True)

#     def _run_post_command (self):
#         if self._debug_:
#             print "DEBUG: qsubmit::Setup::_run_post_command: Post command is", self._post_command_
#         print "NOTICE: qsubmit::Setup::_run_post_command: Running 'post-command'..."
#         subprocess.call (self._post_command_, shell=True)

    def _submit (self):
        self._logger_.info ('Generating ' + self._nbr_jobs_ + ' job(s) to ' + self._default_setup_)

        # Build the script:
        self._build ()

#         # Run precommand:
#         self._run_pre_command ()

#         for ijob in range (int (self._nbr_jobs_)):
#             if not os.path.exists (self._script_directory_):
#                 os.makedirs (self._script_directory_)

#             # Replacing prefixed variable with @XXX@ label
#             self._replace_variable (ijob)

#             a_job_name        = self._script_prefix_ + "_" + str (ijob)
#             a_script_filename = self._script_directory_ + "/" + \
#                 a_job_name + self._script_extension_

#             a_script_file = open (a_script_filename, 'w')
#             a_script_file.write (self._script_)
#             a_script_file.close ()

#             # Change file right permission to make it executable
#             os.chmod (a_script_filename, 0755)

#             if self._default_setup_ in "lyon":
#                 print "NOTICE: qsubmit::Setup::_submit: Submiting job #" + str (ijob), "..."

#                 qsub_cmd = "qsub -j y -P P_nemo"       \
#                     + " -N " + a_job_name              \
#                     + " -o " + self._script_directory_ \
#                     + " " + a_script_filename

#                 if self._debug_:
#                     print "DEBUG: qsubmit::Setup::_submit: qsub command = " + qsub_cmd

#                 if not self._test_ :
#                     subprocess.call (qsub_cmd, shell=True)
#                     # This prevent same seed (fixed now by F. Mauger)
#                     time.sleep (1)
#                 else:
#                     print "NOTICE: qsubmit::Setup::_submit: Mode test"

#         # Run postcommand:
#         self._run_post_command ()


class LyonSetup (BaseSetup):
    def __init__ (self):
        self._use_hpss_         = 0
        self._use_sps_          = 0
        self._use_xrootd_       = 0
        self._cpu_time_         = ""
        self._memory_           = ""
        self._space_size_       = ""

# main function:
def main ():

    parser = argparse.ArgumentParser (description='A python script for running SuperNEMO batch simulations')
    parser.add_argument ('--log',
                         choices=['critical', 'error', 'warning', 'info', 'debug'],
                         default='warning',
                         help='logging level')
    parser.add_argument ('--test', action='store_true',
                         help='only generate file but do not run batch process')
    parser.add_argument ('--config', required=True,
                         help='configuration file (mandatory)')

    args = parser.parse_args ()

    numeric_level = getattr(logging, args.log.upper(), None)
    logging.basicConfig(format='[%(levelname)s:%(module)s::%(funcName)s:%(lineno)d] %(message)s', level=numeric_level)

    logger = logging.getLogger ()
    logger.info ('Parsing ' + args.config + ' config file')

    # Read the config file:
    a_setup = BaseSetup ()
    # a_setup._set_test (test)
    a_setup._parse (args.config)

    # Run jobs:
    a_setup._submit ()

# script:
if __name__ == "__main__":
    main ()

# end of qsubmit.py
