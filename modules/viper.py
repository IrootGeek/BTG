#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Conix Cybersecurity
# Copyright (c) 2017 Hicham Megherbi
#
# This file is part of BTG.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import requests

from lib.io import module as mod


class Viper:
    def __init__(self, ioc, type, config):
        self.config = config
        self.module_name = __name__.split(".")[1]
        self.types = ["MD5", "SHA256"]
        self.search_method = "Onpremises"
        self.description = "Search IOC in Viper Database"
        self.author = "Hicham Megherbi"
        self.creation_date = "21-10-2017"
        self.type = type
        self.ioc = ioc

        if type in self.types and mod.allowedToSearch(self.search_method):
            self.Search()
        else:
            mod.display(self.module_name, "", "INFO", "Viper module not activated")

    def viper_api(self):
        """
        Viper API Connection
        """
        server = self.config["viper_server"]+"file/find"
        if self.type == "MD5":
            ioc = "md5=%s" % self.ioc
        if self.type == "SHA256":
            ioc = "sha256=%s" % self.ioc

        respond = requests.post(server, headers=self.config['viper_user_agent'], data= ioc)

        if respond.status_code == 200:
            respond_json = respond.json()
            if respond_json["results"]:
                if "default" in  respond_json["results"]:
                    return respond_json["results"]["default"][0]
                else:
                    return None
            else:
                return None
        else:
            mod.display(self.module_name,
                        message_type="ERROR",
                        string="Viper API connection status %d" % respond.status_code)
            return None

    def Search(self):
        mod.display(self.module_name, "", "INFO", "Search in Viper ...")

        try:
            if "viper_server" in self.config:
                if self.type in self.types:
                    result_json = self.viper_api()
            else:
                mod.display(self.module_name,
                            message_type=":",
                            string="Please check if you have viper field in config.ini")

        except Exception as e:
            mod.display(self.module_name, self.ioc, "ERROR", e)
            return

        try:
            if result_json:
                if self.type in ["MD5", "SHA256"]:
                    result = result_json
                    
                    if "tags" in result and result["tags"]:
                        tags = "Tags: %s |" % ",".join(result["tags"])
                    else:
                        tags = ""

                    if "id" in result:
                        id = " Id: %d |" % result["id"]
                    else:
                        id = ""

                    if "name" in result:
                        name = " %s" % result["name"]
                    else:
                        name = ""

                    mod.display(self.module_name,
                                self.ioc,
                                "FOUND",
                                "%s%s%s" % (tags, id, name))
        except:
            pass
