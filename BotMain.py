import BotClass
import Queue
import string
import getopt
import sys
from BotClass import *
from BotUI import *
from BotCommandParser import *

UI=True

class Bot(BotClass):

    def __init__(self):
        BotClass.__init__(self)

        try:
           IRC_THREAD = threading.Thread(target=self.connect)
           IRC_THREAD.daemon = True
           IRC_THREAD.start()
        except NicknameInUseError as e:
            IRC_THREAD.stop()
            IRC_THREAD.join()
            del ui
            print e.value
            sys.exit(2)
        except KeyboardInterrupt:
            print "Closing"


    def connect(self):
        super(Bot,self).connect()

def command_line(ui_print_queue, ui_status_queue):
    while True:
        if ui_print_queue.empty() == False:
            msg=ui_print_queue.get()
            print msg

        if ui_status_queue.empty() == False:
            dummy=ui_status_queue.get()
        
        if (ui_status_queue.empty() == True) and (ui_print_queue.empty() == True):
            time.sleep(0.1)

if __name__ == "__main__":
    irc = Bot()
    parser = BotCommandParser(irc)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["no_ui",])
    except getopt.GetoptError:
        print 'Unknown option'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print "help!"
        elif opt in ("--no_ui"):
            print "not using the UI"
            UI=False

    if UI:
        ui = BotUI(irc.irc_print_queue, \
                   irc.irc_flood_timeout_queue, \
                   irc.ui_console_queue, \
                   irc.ui_status_queue)
    else:
        command_line(irc.ui_console_queue, \
                     irc.ui_status_queue)
                     
        # CmdLineThread = threading.Thread(target=command_line, args=(irc.ui_console_queue, \
                                                                    # irc.ui_status_queue))
        # CmdLineThread.daemon = True
        # CmdLineThread.start()
