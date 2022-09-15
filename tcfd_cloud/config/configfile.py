# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 12:04:41 2018

@author: ymliu
"""

import configparser as config
import os

class ConfigFile:
    def __init__(self, path=None):
        self.dbServer = ""
        self.dbUserName = ""
        self.dbPassWord = ""
        self.dbSchema = ""
        self.dbRDBMS = "mysql"
        self.dbOK = False
        fp = path
        if not path:
            fp = os.path.dirname(__file__) + r"\\config.ini"
        self.readConfigInfo(fp)

    def readConfigInfo(self, path):
        if os.path.exists(path):
            try:
                inifile = config.ConfigParser()
                inifile.read(path, encoding='utf-8')
                self.dbServer = inifile.get('DB', 'server')
                self.dbUserName = inifile.get('DB', 'user')
                self.dbPassWord = inifile.get('DB', 'password')
                self.dbSchema = inifile.get('DB', 'schema')
                self.dbOK = True
            except Exception as e:
                self.dbOK = False
        else:
            self.dbOK = False
    