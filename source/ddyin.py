#!/usr/bin/env python
import yaml
import json
import sys
import ansible.inventory
from collections import defaultdict
import os
import copy
import logging as log

log.basicConfig(stream=sys.stderr, level=log.DEBUG)

data={}

def load(fname):
    results=yaml.load(file(fname).read())
    if results is None:
        return {}
    else:
        return results

config=load('ddyin-config.yml')

def output(data):
    sys.stdout.write(json.dumps(data, indent=2))

def load_raw(baseinventory):
    results={}
    raw=load(baseinventory)
    for key in raw.keys():
        if isinstance(raw[key], list):
            results.setdefault(key, {'hosts': raw[key]})
        else:
            results.setdefault(key, raw[key])
    return results

def load_gbh(groups_by_host):
    results=defaultdict(dict)
    if isinstance(groups_by_host, str):
        gbh=load(groups_by_host)
    elif isinstance(groups_by_host, dict):
        gbh=groups_by_host_file
    else:
        assert (isinstance(groups_by_host, str) or isinstance(groups_by_host, dict)), "load_gbh: groups_by_host must be a filename or a dictionary"
    for hostname in gbh:
        for groupname in gbh[hostname]:
            if 'hosts' not in results[groupname].keys():
                results[groupname].setdefault('hosts', [hostname])
            else:
                results[groupname]['hosts'].append(hostname)
    return dict(results)

def load_vardir(vars_dir):
    vars={}
    for name in os.listdir(vars_dir):
        vars.setdefault(name, load(os.path.join(vars_dir, name)))
    return vars

def merge_gbh(inventory_data, gbh):
    """SIDE EFFECTS: the hosts in gbh will be merged into inventory_data"""
    for gname in gbh.keys():
        if gname not in inventory_data.keys():
            inventory_data.setdefault(gname, copy.deepcopy(gbh[gname]))
        else:
            for hostname in gbh[gname]['hosts']:
                if hostname not in inventory_data[gname]['hosts']:
                    inventory_data[gname]['hosts'].append(hostname)

def listmerge(lst1, lst2):
    '''Merge two unsorted lists without including duplicates, with consistent ordering.
    Order will always be lst1 + lst2'''
    for item in lst2:
        if item not in lst1:
            lst1.append(item)
    return lst1

def deepmerge(destination, source, path=None):
    "merges source into destination"
    if path is None: path = []
    for key in source:
        if key in destination:
            if isinstance(destination[key], dict) and isinstance(source[key], dict):
                deepmerge(destination[key], source[key], path + [str(key)])
            elif isinstance(destination[key], list) and isinstance(source[key], list):
                destination[key] = listmerge(destination[key], source[key])
            elif destination[key] == source[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            destination[key] = source[key]
    return destination

def merge(destination, source):
    if isinstance(destination, list) and isinstance(source, list):
        listmerge(destination, source)
    elif isinstance(destination, dict) and isinstance(source, dict):
        deepmerge(destination, source)
    else:
        raise Exception("Cannot merge %s and %s (%s, %s)" % (type(destination), type(source), destination, source))

def host_identity_group(hname):
    return { 'hosts': [hname],
             'vars': {} }

def merge_vars(inventory_data, gvdata):
    for groupname in gvdata.keys():
        if groupname not in inventory_data.keys():
            pass
        else:
            if len(gvdata[groupname].keys()) > 0:
                if 'vars' not in inventory_data[groupname].keys():
                    inventory_data[groupname].setdefault('vars', {})
            for vvv in gvdata[groupname].keys():
                if vvv != 'SHARED':
                    inventory_data[groupname]['vars'].setdefault(vvv, gvdata[groupname][vvv])
                elif vvv == 'SHARED':
                    # For shared values, add the values to a host-specific group
                    for shared_var in gvdata[groupname]['SHARED'].keys():
                        log.debug("(%s) Updating shared var: %s" % (groupname, shared_var))
                        log.debug("(%s) For hosts: %s" % (groupname, ','.join(inventory_data[groupname].get('hosts', []))))
                        for hname in inventory_data[groupname].get('hosts', []):
                            if hname not in inventory_data.keys():
                                inventory_data.setdefault(hname, host_identity_group(hname))
                            if shared_var not in inventory_data[hname]['vars'].keys():
                                inventory_data[hname]['vars'].setdefault(shared_var, gvdata[groupname]['SHARED'][shared_var])
                            else:
                                log.debug('Merging %s' % shared_var)
                                merge(inventory_data[hname]['vars'][shared_var], gvdata[groupname]['SHARED'][shared_var])

def dir_loader(load_function):
    def load_and_merge(dirname):
        results={}
        for name in os.listdir(dirname):
            merge(results, load_function(os.path.join(dirname, name)))
        return results
    return load_and_merge

def getpathtype(url_or_path):
    if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
        return 'web'
    elif os.path.isfile(url_or_path):
        return 'file'
    elif os.path.isdir(url_or_path):
        return 'dir'
    else:
        raise TypeError, "%s is not a url or a path" % url_or_path

def listify(lst_or_string):
    if isinstance(lst_or_string, str):
        return [lst_or_string]
    elif isinstance(lst_or_string, list):
        return lst_or_string
    else:
        raise TypeError, "Must be a list or a string"

gbh_dispatch = { 'web' : lambda x: {},
                 'file' : load_gbh,
                 'dir' : dir_loader(load_gbh) }

vars_dispatch = { 'web' : lambda x : {},
                  'file': load,
                  'dir': load_vardir }

base_dispatch = { 'web': lambda x : {},
                  'file': load_raw,
                  'dir': dir_loader(load_raw) }

if 'base' in config.keys():
    data={}
    for item in listify(config['base']):
        log.debug('Loading base inventory file: %s (%s)' %  (item, getpathtype(item)))
        merge(data, base_dispatch[getpathtype(item)](item))
else:
    data={}

if 'groups_by_host' in config.keys():
    log.debug('Loading groups by host')
    for item in listify(config['groups_by_host']):
        log.debug('Loading %s, type %s, and merging with inventory data using merge_gbh' % (item, getpathtype(item)))
        merge_gbh(data, gbh_dispatch[getpathtype(item)](item))

if 'vars' in config.keys():
    log.debug('Loading and merging vars')
    for item in listify(config['vars']):
        log.debug('Loading %s, type %s, and merging with inventory data using merge_vars' % (item, getpathtype(item)))
        merge_vars(data, vars_dispatch[getpathtype(item)](item))

output(data)
