#!/usr/bin/python 
# -*- coding: utf-8 -*-
# 
# migtruncate - a part of the MiG scripts
# Copyright (C) 2004-2010  MiG Core Developers lead by Brian Vinter
# 
# This file is part of MiG.
# 
# MiG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# MiG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 

"""
This MiG python script was autogenerated by the MiG User Script Generator !!!
Any changes should be made in the generator and not here !!!
"""

import sys
import os
import getopt
import subprocess
import StringIO

def version():
    """Show version details"""
    print 'MiG User Scripts: $Revision: 1251 $,$Revision: 1251 $'

def usage():
    """Usage help for truncate"""

    print "Usage: migtruncate.py [OPTIONS] FILE [FILE ...]"
    print "Where OPTIONS include:"
    print "-c CONF		read configuration from CONF instead of"
    print "		default (~/.mig/miguser.conf)."
    print "-h		display this help"
    print "-s MIG_SERVER	force use of MIG_SERVER."
    print "-v		verbose mode"
    print "-V		display version"
    print "-n N		Truncate file(s) to at most N bytes"

def check_var(name, var):
    """Check that conf variable, name, is set"""

    if not var:
        print "Error: Variable %s not set!" % name
        print "Please set in configuration file or through the command line"
        sys.exit(1)

def read_conf(conf, option):
    """Extract a value from the user conf file: format is KEY and VALUE
    separated by whitespace"""

    try:
        conf_file = open(conf, 'r')
        for line in conf_file:
            line = line.strip()
            # split on any whitespace and assure at least two parts
            parts = line.split() + ['', '']
            opt, val = parts[0], parts[1]
            if opt == option:
                return val
        conf_file.close()
    except Exception:
        return ''


def truncate_file(size, path_list):
    """Execute the corresponding server operation"""

    # Build the path_list string used in wild card expansion:
    # 'path="$1";path="$2";...;path=$N'
    # path_list may be a string or array
    if not isinstance(path_list, basestring):
        path_list = ";path=%s" % ";path=".join(path_list)
    
    if not ca_cert_file:
        ca_check = '--insecure'
    else:
        ca_check = "--cacert %s" % (ca_cert_file)

    if not password:
        password_check = ''
    else:
        password_check = "--pass %s" % (password)

    timeout = ''
    if max_time:
        timeout += "--max-time %s" % (max_time)
    if connect_timeout:
        timeout += " --connect-timeout %s" % (connect_timeout)


    curl = 'curl --compressed'
    target = ''
    location = "cgi-bin/truncate.py"
    post_data = 'output_format=txt;flags=%s;size=%s;%s' % (server_flags, size, path_list)
    query = ""
    data = ''
    if post_data:
        data = '--data "%s"' % post_data
    curl_opts = "--location --fail --silent --show-error"
    command = "%s %s --cert %s --key %s %s %s %s %s %s --url '%s/%s%s'" % \
        (curl, curl_opts, cert_file, key_file, data, ca_check, password_check,
        timeout, target, mig_server, location, query)
    proc = subprocess.Popen(command, shell=True, bufsize=0,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    out_buffer = StringIO.StringIO(proc.communicate()[0])
    proc.stdout.close()
    out = out_buffer.readlines()
    exit_code = proc.returncode

    return (exit_code, out)



# === Main ===

verbose = 0
conf = os.path.expanduser("~/.mig/miguser.conf")
flags = ""
mig_server = ""
server_flags = ""
script_path = sys.argv[0]
script_name = os.path.basename(script_path)
script_dir = os.path.dirname(script_path)
size = 0
opt_args = "c:hrs:vVn:"

# preserve arg 0
arg_zero = sys.argv[0]
args = sys.argv[1:]
try:
    opts, args = getopt.getopt(args, opt_args)
except getopt.GetoptError, e:
    print "Error: ", e.msg
    usage()
    sys.exit(1)

for (opt, val) in opts:
    if opt == "-c":
        conf = val
    elif opt == "-h":
        usage()
        sys.exit(0)
    elif opt == "-s":
        mig_server = val
    elif opt == "-v":
        verbose = True
    elif opt == "-V":
        version()
        sys.exit(0)
    elif opt == "-n":
        size = val

    else:
        print "Error: %s not supported!" % (opt)

    # Drop options while preserving original sys.argv[0] 
    sys.argv = [arg_zero] + args
arg_count = len(sys.argv) - 1
min_count = 1

if arg_count < min_count:
    print "Too few arguments: got %d, expected %d!" % (arg_count, min_count)
    usage()
    sys.exit(1)

if not os.path.isfile(conf):
    print "Failed to read configuration file: %s" % (conf)
    sys.exit(1)

if verbose:
    print "using configuration in %s" % (conf)

if not mig_server:
    mig_server = read_conf(conf, 'migserver')

def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))

# Force tilde and variable expansion on path vars
cert_file = expand_path(read_conf(conf, 'certfile'))
key_file = expand_path(read_conf(conf, 'keyfile'))
ca_cert_file = expand_path(read_conf(conf, 'cacertfile'))
password = read_conf(conf, 'password')
connect_timeout = read_conf(conf, 'connect_timeout')
max_time = read_conf(conf, 'max_time')

check_var('migserver', mig_server)
check_var('certfile', cert_file)
check_var('keyfile', key_file)

# Build the path string used directly:
# 'path="$1";path="$2";...;path=$N'
path_list = "path=%s" % ";path=".join(sys.argv[1:])
(status, out) = truncate_file(size, path_list)
print ''.join(out),
sys.exit(status)