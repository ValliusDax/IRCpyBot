# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~

    This module is the middle man for handling/consolidating
    configurations for the IRCpyBot project.

    :copyright: (c) 2012 by Mek, Dippingsauce
    :license: Pending, see LICENSE for more details.
"""

import ConfigParser
import os
import types

def getdef(self, section, option, default_value):
    try:
        return self.get(section, option)
    except:
        return default_value

path = os.path.dirname(__file__)
config = ConfigParser.ConfigParser()
config.read('%s/settings.cfg' % path)

# Add/inject a method to the config object called getdef
config.getdef = types.MethodType(getdef, config)

CONN = {'host': config.getdef("irc", "host", "irc.empornium.me"),
        'port': int(config.getdef("irc", "port", 6667)),
        'channel': '#%s' % config.getdef("irc", "channel", "Dax'sLab")
        }


USER = {'nick': config.getdef("irc", "nick", "Deedee_testing"),
        'ident': config.getdef("irc", "ident", "Deedee"),
        'realname': config.getdef("irc", "", "Deedee"),
        'password': config.getdef("irc", "", "dancingdeedee"),
        'owner': config.getdef("irc", "", "Dax")
        }

FLOOD = {'flood_time': config.getdef("irc", "", 15000),
         'flood_messages': config.getdef("irc", "", 9)
	    }

STAT = {'ping': int(0),
        'ping_time': int(1),
        'irc_messages': int(2)
        }
