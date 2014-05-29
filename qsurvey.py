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
import time
import subprocess
import logging
import argparse
import re
import paramiko

USERNAME = os.environ['USER']
PASSWORD = 'lol'
HOSTNAME = ''

def survey ():
    """Basic function to send command through ssh and parse their results into
    string. Results are send to notify through the call of subprocess"""
    # Open ssh connection
    try:
        ssh = paramiko.SSHClient ()
        ssh.load_system_host_keys ()
        ssh.set_missing_host_key_policy (paramiko.WarningPolicy ())
        hostname = HOSTNAME
        if not hostname:
            hostname = 'ccage.in2p3.fr'
            logging.getLogger ().info ('Connecting to ' + hostname + '...')
            ssh.connect (hostname=hostname,
                         username=USERNAME,
                         password=PASSWORD)

            while True:
                sge_cmd = 'export SGE_ROOT=/opt/sge;' \
                          'export SGE_CELL=ccin2p3;'
                qprefix_cmd = '/opt/sge/bin/lx-amd64/'
                qstat_cmd = sge_cmd + \
                            'echo -ne "Total number of jobs: ";' + qprefix_cmd + 'qstat | tail -n+3 | wc -l;' + \
                            'echo -ne "Number of running jobs: ";' + \
                            qprefix_cmd + 'qstat -s r | tail -n+3 | wc -l;' + \
                            'echo "Number of jobs run by NEMO users:";' + \
                            qprefix_cmd + 'qstat -u \* -ext -s r | tail -n+3 | grep nemo | awk "{print \$5}" | sort | uniq -c'
                logging.getLogger ().debug ('qstat_cmd = ' + qstat_cmd)
                stderr, stdout, stdin = ssh.exec_command (qstat_cmd)
                text = ''
                for line in stdout:
                    text += re.sub('b\'|\\\\n|\'','', str (line)) # + '\n'
                logging.getLogger ().debug (text)
                subprocess.call('notify-send -t 5000 -i stock_dialog-info "qsurvey" "' + text +'"', shell=True)
                time.sleep (60)
    except Exception as e:
        logging.getLogger ().error ('Caught exception: %s %s' % (e.__class__, e))
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
    parser.add_argument ('--hostname', default = '',
                         help = 'hostname for remote connection')
    parser.add_argument ('--username', default = os.environ['USER'],
                         help = 'username for remote connection')
    parser.add_argument ('--password', default = '',
                         help = 'password for remote connection')
    args = parser.parse_args ()

    # Setting logging level
    numeric_level = getattr(logging, args.log.upper(), None)
    logging.basicConfig(format = '[%(levelname)s:%(module)s::%(funcName)s:%(lineno)d] %(message)s',
                        level = numeric_level)

    global PASSWORD, USERNAME, HOSTNAME
    HOSTNAME = args.hostname
    USERNAME = args.username
    PASSWORD = args.password

    try:
        survey ()
    except Exception as e:
        logging.getLogger ().error ('Caught exception: %s' % e)
        sys.exit (1)

# script:
if __name__ == '__main__':
    main ()

# end of qsubmit.py
