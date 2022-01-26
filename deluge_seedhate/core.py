#
# core.py
#
# Copyright (C) 2022 Adam Mravnik
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#     The Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor
#     Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
from __future__ import unicode_literals

import logging
import re
import threading
import time
import twisted
from datetime import datetime
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase


log = logging.getLogger(__name__)
logging.getLogger()

CONFIG_DEFAULT = {

}


class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager(
            "seedhate.conf", CONFIG_DEFAULT
        )       

        component.get("EventManager").register_event_handler(
            "TorrentAddedEvent", self.post_torrent_add
        )
        component.get("EventManager").register_event_handler(
            "TorrentRemovedEvent", self.post_torrent_remove
        )

        component.get("EventManager").register_event_handler(
            "TorrentFileCompletedEvent", self.update_checker
        )
        self.lc = None
        if not self.lc:
            log.debug("seedhate loop starting")
            self.lc = LoopingCall(self.update_checker)
            self.lc.start(5).addErrback(twisted.python.log.err)
            if not reactor.running:
                reactor.run()
            log.debug("seedhate loop started")

    def disable(self):
        self.lc = None

    def update(self):
        try:
            self.lc
        except NameError:
            self.lc = None

        if self.lc:
            if not self.lc.running:
                self.lc.start(5).addErrback(twisted.python.log.err)
                if not reactor.running:
                    reactor.run()
        else:
            self.lc = LoopingCall(self.update_checker)
            self.lc.start(5).addErrback(twisted.python.log.err)
            if not reactor.running:
                reactor.run()
        pass

    def update_checker(self):
        time.sleep(1)
        torrentmanager = component.get("TorrentManager")

        log.debug("update_checker in")
        for torrent_id in torrentmanager.get_torrent_list():
            torrent = torrentmanager.torrents.get(torrent_id, None)
            finished = torrent.is_finished

            if torrent.state == "Seeding" or finished:
                torrentmanager.remove(torrent_id)

    # Plugin hooks #
    def post_torrent_add(self, torrent_id, from_state=None):
        torrentmanager = component.get("TorrentManager")
        if from_state or (
                from_state is None and not torrentmanager.session_started
        ):
            return
        log.debug("seedhate post_torrent_add")

    def apply_filter(self, torrent_id):
        return

    def post_torrent_remove(self, torrent_id):
        log.debug("seedhate post_torrent_remove")
        if torrent_id in self.torrent_stop_times:
            del self.torrent_stop_times[torrent_id]

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config:
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
