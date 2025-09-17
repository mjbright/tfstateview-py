#!/usr/bin/env python3

# Not portable to macOs:
#!/usr/bin/env /home/student/.venv/py-tfstateview/bin/python3

import os
import sys
import time
# For timestamp handling:
from datetime import datetime
import json
import copy # For deepcopy

# For api playback: 'current resources' save/restore
# import pickle

# For loading config: see https://toml.io/en/
# import toml

from datetime import datetime, timezone

# import display_k8s_d2bin

DEFAULT_CONFIG = {
    'show_types': False
}

'''
DEFAULT_CONFIG = {
    'namespace': None,
    'resources': [],
    'show_types': True,
    'verbose': False,
    #'display_type': 'tui',
    'display_type': 'd2',
    'display_options': {
        'type':      'd2',
        'tooltip':   True,
        'links':     False,
        'ext_label': False,
        'inside':    True,
    },
    'loads': None,
    'snapshots': 0,
    'record': '',
}
'''

tfstate_file = '../terraform.tfstate'

## -- Func: --------------------------------------------------------------------------------

'''
def die(msg):
    """ exit after printing bold-red error 'msg' text"""
    print(f"\ndie: { bold_red(msg) }")
    sys.exit(1)
'''

from inspect import currentframe, getframeinfo

def die(msg):
    previous_frame_info = getframeinfo(currentframe().f_back)
    context = [ previous_frame_info.filename , str(previous_frame_info.lineno) ]
    #sys.stderr.write(f'die: {sys.argv[0]} <{context}>: {msg}\n')

    sys.stderr.write(f'\n\ndie: line {context[1]}@{context[0]}:\n  { bold_red(msg) }\n')
    sys.exit(1)

def file1newer(file1, file2, verbose=False):
    file1_mtime = os.stat(file1).st_mtime
    file2_mtime = os.stat(file2).st_mtime

    if verbose:
        print(f'File {file1:20} => {file1_mtime}')
        print(f'File {file2:20} => {file2_mtime}')

    if file1_mtime > file2_mtime:
        return True
    return False
    '''
    if file1_mtime > file2_mtime:
        print(f'File {file1} is newer than {file2}')
        return True
    else:
        print(f'File {file1} is older than {file2}')
        print(f'File {file1:20} => {file1_mtime}')
        print(f'File {file2:20} => {file2_mtime}')
    return False
    '''

def naive_utcnow():
    #return datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    return datetime.now(timezone.utc)

def timer_start():
    return time.time()

def timer_end(start_ts):
    time_ts = time.time() - start_ts
    hms     = timer_hms(time_ts)
    return hms

def timer_hms(time_ts):
    # Difference between two timestamps

    days      = int(time_ts / (60 * 60 * 24))
    rem_secs  = time_ts - ( days * 60 * 60 * 24 )
    hours     = int(rem_secs / (60 * 60))
    rem_secs -= hours * 60 * 60
    mins      = int(rem_secs / 60)
    rem_secs -= mins * 60

    if days > 0:
        #print(f'Took [{time_ts:.2f}s]  {days}d {hours}h {mins}m {rem_secs:.2f}s: {command}')
         return f' {days}d {hours}h {mins}m {rem_secs:.2f}s'
    elif hours > 0:
        #print(f'Took [{time_ts:.2f}s]  {hours}h {mins}m {rem_secs:.2f}s: {command}')
         return f' {hours}h {mins}m {rem_secs:.2f}s'
    elif mins > 0:
        #print(f'Took [{time_ts:.2f}s]  {mins}m {rem_secs:.2f}s: {command}')
         return f' {mins}m {rem_secs:.2f}s'

    #print(f'Took  {rem_secs:.2f}s: {command}')
    return f' {rem_secs:.2f}s'


def showResources(tfstate):
    for resource_type in tfstate['resources']:
        print(f'{resource_type["type"]}/{resource_type["name"]}')
        #for instance in tfstate['resources']['instances']:
        if DEFAULT_CONFIG['show_types']:
            continue

        for instance in resource_type['instances']:
            if VERBOSE:
                print(f'\t{instance}')
            else:
                print(f'\t{instance["attributes"]["id"]}')

def parse_args():
    global DEFAULT_CONFIG

    arg_idx=0
    while arg_idx <= (len(sys.argv)-1):
        arg=sys.argv[arg_idx]
        arg_idx+=1

        if arg == "-t":
            DEFAULT_CONFIG['show_types']=True

        '''
        if arg == "-c":
            runconfig_file=sys.argv[arg_idx]
            with open(runconfig_file, 'r') as f:
                read_runconfig = toml.load(f)
                runconfig.update(read_runconfig)
            runconfig['runconfig_file']=runconfig_file
            print(f'runconfig merged from {runconfig_file} ==>\n\t{runconfig}')
            arg_idx+=1
            continue
        '''

## -- Args: --------------------------------------------------------------------------------

parse_args()

## -- Main: --------------------------------------------------------------------------------

VERBOSE=False

loop=0

while not os.path.exists(tfstate_file):
    print(f'No such file as {tfstate_file} ... sleeping')
    time.sleep(5)

tfstate_mtime = os.stat(tfstate_file).st_mtime

while True:
    loop+=1

    #now = naive_utcnow()
    new_tfstate_mtime = os.stat(tfstate_file).st_mtime

    if loop == 1 or new_tfstate_mtime > tfstate_mtime:
        try:
            with open(tfstate_file, 'r') as f:
                tfstate = json.load(f)
        except:
            print(f'Failed to load {tfstate_file} tfstate file')
            time.sleep(5)
            pass

        tfstate_mtime = new_tfstate_mtime
        showResources(tfstate)
        time.sleep(1)

sys.exit(0)

