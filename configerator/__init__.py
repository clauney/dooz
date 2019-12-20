#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:20:39 2019

@author: clauney
"""
from os import path as ospath, makedirs as osmakedirs, environ as osenviron
from pickle import dump as pckdump, load as pckload, PickleError
import uuid

class ConfigSource():
    default_store_cfgtypes_in_envvar = []
#    default_store_cfgkeys_in_envvar = [] # NOT YET
    default_config_file_path = './temp/'
    default_persist_configs_in_fs = True
    def __init__(self, **kwargs):
        '''
        GENERIC (SUPERCLASS) KWARGS
            name (str):
                used for cache filename, as well as geenral reference in Configerator.sources
                MUST BE UNIQUE ACROSS ALL SOURCES!

            type (str):
                type type of config source. various types have different handling. Supported types include:
                    * local_config
                    * cli_params
                    * aztable_config
                    * restapi_config

            store_cfgtypes_in_envvar (list[type]=[str]):
                if provided, configs with val matching a type in the list will be converted to str and stored in environment variables
                if not provided or if empty, will not store any configs in env vars

            persist_configs_in_fs (bool=True):
                if provided and truthy, will cache configs of various types in the filesystem to be locally persistent qcross restarts, tolerate failures of config data stores, etc.

            config_file_path (str='./temp/'):
                A string containing a relative or absolute reference to a directory to store the config cache file.
                The path defaults to ./temp (inside submod directory).
                This default location IS INCLUDED IN SUPPLIED GITIGNORE. STRONGLY SUGGEST doing the same if you change the cache location.

        SUBCLASS-SPECIFIC KWARGS
            LocalConfigSource (type='local_config')
                data (dict):
                    a data dict to store as the config data
            CLIParamsConfigSource (type='cli_params')
                sysargv (list):
                    the contents of sys.argv. Parsed according to:
                        * any kwarg-like args (str containing '=') will be split at the first = and stored as k:v pairs in the config dict
                        * remaining args will be stored as a list of args, referenceable as a list under keyword "args" in the config dict

        '''
        self.name = kwargs['name']
        self._persist_configs_in_fs = kwargs.pop('persist_configs_in_fs', self.default_persist_configs_in_fs)
        self._config_cachefile = self._init_cfg_file_path(kwargs.pop('config_file_path', ''))
        self._store_cfgtypes_in_envvar = kwargs.pop('store_cfgtypes_in_envvar', self.default_store_cfgtypes_in_envvar)
        self._internal_cfg = kwargs
        self.reinit_configs()

    def _init_cfg_file_path(self, cache_path):
        cache_path = cache_path if cache_path else self.default_config_file_path
        abs_cp = ospath.abspath(cache_path) # abspath also strips out trailing slash in addition to doing its absolute action
        osmakedirs(abs_cp, exist_ok=True)
        return '{}/{}._pf'.format(abs_cp, self.name)

    def reinit_configs(self):
        if self._persist_configs_in_fs:
            cfg_data = self._get_configs_filesystem(self._config_cachefile)
        else:
            cfg_data = {}
        
        cfg_data = cfg_data if cfg_data and type(cfg_data) == dict else {}
        
        cfg_data.update(self.fetch_configs())
        
        if self._persist_configs_in_fs:
            self._put_configs_filesystem(cfg_data, self._config_cachefile)

        if self._store_cfgtypes_in_envvar:
            self._put_configs_osenv(cfg_data, self._store_cfgtypes_in_envvar)

        self.config_data = cfg_data

    def _put_configs_filesystem(self, data, absfilename):
        if ospath.exists(absfilename):
            with open(absfilename, 'wb') as existpfw:
                pckdump(data, existpfw)
        else:
            with open(absfilename, 'xb') as newpfw:
                pckdump(data, newpfw)
    
    def _get_configs_filesystem(self, absfilename):
        rd = {}
        if self._persist_configs_in_fs and ospath.exists(absfilename):
            try:
                with open(absfilename, 'rb') as pf:
                    rd = pckload(pf)
            except (IOError) as oops:
                self.lj.exception('THROW reading file %s, details: %s', absfilename, oops)
            except (TypeError) as oops:
                self.lj.exception('THROW need bytes unpickling file %s, details: %s', absfilename, oops)
            except (EOFError, PickleError) as oops:
                self.lj.exception('THROW need bytes unpickling file %s, details: %s', absfilename, oops)
        return rd

    def _put_configs_osenv(self, data, type_list):
        if type_list and type(type_list) == list:
            for k, v in data.items():
                if type(v) in type_list:
                    osenviron[k] = v

    def fetch_configs(self):
        raise NotImplementedError # this must be overridden by subclasses

class AzTableConfigSource(ConfigSource):
    cfg_type='aztable_config'
    def client(self):
        return self._internal_cfg.get('tablesvc')
    def fetch_configs(self):
        datas = self.client.query_entities(self._internal_cfg.get('tablename'))
        #!!!! put in thing to fetch more if at 1000 / marker
        
        #!!!! THEN:
#                    * table_hierarchy (list[str]=['PartitionKey', 'RowKey']):
#                        a list of column names to use as the config hierarchy.


class LocalConfigSource(ConfigSource):
    cfg_type='local_config'
    def fetch_configs(self):
        return self._internal_cfg.get('data', {})

class CLIParamsConfigSource(ConfigSource):
    cfg_type='cli_params'
    translate_bool = True #translates boolean-ish kwarg values
    translate_int = False #translates integer-ish kwarg values
    bool_translate = {'true': True, 'false': False}

    def fetch_configs(self):
        args = self._internal_cfg.get('sysargv', {})
        ret_kwargs = {}
        ret_args = []
        if args and type(args) == list:
            for arg in args:
                if type(arg) == str:
                    if '=' in arg:
                        k, v = str(arg).split('=')
                        if self.translate_bool and v.lower() in self.bool_translate:
                            v = self.bool_translate[v.lower()]
                        elif self.translate_int and v.isdigit():
                            v = int(v)
                        ret_kwargs[k] = v
                    else:
                        ret_args.append(arg)
        if ret_args:
            ret_kwargs['args'] = ret_args
        return ret_kwargs

class Configerator():
    supported_sources = {
            'local_config': LocalConfigSource,
            'cli_params': CLIParamsConfigSource,
            'aztable_config': AzTableConfigSource,
            }
    def __init__(self, **kwargs):
        '''
        KWARGS:
            config_sources (list[dict]):
                a list of config sources to init. See #!!!!SOMEWHERE for more info
        
        For config_sources dict settings, see ConfigSource class.
        
        On instancing the class, the instance will init a source for every source in the list,
        adding that source's config_data to its running_config.
        
        Two elements are important to note about collisions between config names (config dict keys):
            * Configs from sources LATER IN THE LIST will OVERWRITE ones from EARLIER IN THE LIST
            * Configs configs from the main fetch_config method will OVERWRITE persisted in the FILESYSTEM 
        
        This allows you a very flexible way of establishing a hierarchy. For example, items in 

        SOURCE SETTINGS DICT INFO
            GENERIC (SUPERCLASS)
                name (str):
                    used for cache filename, as well as geenral reference in Configerator.sources
                    MUST BE UNIQUE ACROSS ALL SOURCES!
    
                type (str):
                    type type of config source. various types have different handling. Supported types include:
                        * local_config
                        * cli_params
                        * aztable_config
                        * restapi_config
    
                store_cfgtypes_in_envvar (list[type]=[str]):
                    if provided, configs with val matching a type in the list will be converted to str and stored in environment variables
                    if not provided or if empty, will not store any configs in env vars
    
                persist_configs_in_fs (bool=True):
                    if provided and truthy, will cache configs of various types in the filesystem to be locally persistent qcross restarts, tolerate failures of config data stores, etc.
    
                config_file_path (str='./temp/'):
                    A string containing a relative or absolute reference to a directory to store the config cache file.
                    The path defaults to ./temp (inside submod directory).
                    This default location IS INCLUDED IN SUPPLIED GITIGNORE. STRONGLY SUGGEST doing the same if you change the cache location.
    
            SUBCLASS-SPECIFIC
                LocalConfigSource (type='local_config')
                    * data (dict):
                        a data dict to store as the config data
                CLIParamsConfigSource (type='cli_params')
                    * sysargv (list):
                        the contents of sys.argv. Parsed according to:
                            * any kwarg-like args (str containing '=') will be split at the first = and stored as k:v pairs in the config dict
                            * remaining args will be stored as a list of args, referenceable as a list under keyword "args" in the config dict
                AzTableConfigSource (type='aztable_config')
                    * tablesvc (azure.cosmosdb.table.TableService):
                        an instance of Azure TableService (created with account_name / account_key params)
                    * tablename (str):
                        a string indicating the name of a table to fetch to use as configs
                    * table_hierarchy (list[str]=['PartitionKey', 'RowKey']):
                        a list of column names to use as the config hierarchy.

        '''
        sources = kwargs.get('config_sources', [])
        self.cfg_source_list = []
        self.cfg_source_dict = {}
        self.running_config = {}
        
        for d in sources:
            if d and type(d) == dict and d.get('type') in self.supported_sources:
                if not d.get('name'):
                    d['name'] = '{}|{}'.format(d.get('type'), uuid.uuid4())
                srcobj = self.supported_sources[d['type']](**d)
                self.cfg_source_list.append(srcobj)
                self.cfg_source_dict[d['name']] = srcobj
                self.running_config.update(srcobj.config_data)



#%%
localconfig = {
        'name': 'local_config',
        'type': 'local_config',
        'data': {
                'alltasks': [
                        ['1000','Riley','AMPM','Teeth','Brush, use waterpik, use brush thingies'],
                        ['1001','Riley','PM','Shower','Shower, making sure that you wash your hair at least every other day'],
                        ['1002','Riley','AM','Breakfast','eat something with protein!'],
                        ['2001','Chris','AM','Pill','Take your meds'],
                        ['2002','Chris','AM','Vitamins','Take your vitamins'],
                        ['2003','Chris','AMPM','Check calendar','Take a look at the coming day'],
                        ['2004','Chris','PM','Shower','Take a shower!'],
                        ['2005','Chris','PM','Shoulder exercises','Do your shoulder exercises!'],
                        ['2006','Chris','AMPM','Teeth','Brush and floss!'],
                        ['2007','Chris','PM','Set out clothes','Set out your clothes for tomorrow']
                        ],
                'weather_loc_meteo': {
                        '98117': 'seattle_united-states-of-america_5809844',
                        },
                'who_data': {
                        'default': {
                                'zip': '98117',
                                },
                        'chris': {
                                },
                        },
                'unused_weatherwidget': '''<a class="weatherwidget-io" href="https://forecast7.com/en/47d69n122d38/98117/?unit=us" data-label_1="BALLARD" data-label_2="WEATHER" data-theme="weather_one" >BALLARD WEATHER</a>
                        <script>
                        !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
                        </script>''',
                'meteo': '''<iframe src="https://www.meteoblue.com/en/weather/widget/three/seattle_united-states-of-america_5809844"  frameborder="0" scrolling="NO" allowtransparency="true" sandbox="allow-same-origin allow-scripts" style="width: 460px;height: 525px"></iframe>''',
                'craptraffic': '''<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d172152.17919202129!2d-122.32018107603865!3d47.60906576366696!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sus!4v1520124306339" width="600" height="450" frameborder="0" style="border:0" allowfullscreen></iframe>''',
                },
        }

import sys
cliconfig = {'name': 'cli_params', 'type': 'cli_params', 'sysargv': sys.argv}

#%%

lcfg = LocalConfigSource(**localconfig)
scfg = CLIParamsConfigSource(**cliconfig)
cfg = Configerator(config_sources=[localconfig, cliconfig])
