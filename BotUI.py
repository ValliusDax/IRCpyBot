import curses
import Queue
import threading
import time
import datetime
import sys

from configs.config import FLOOD, STAT

class BotUI(object):

    loadDateTime = datetime.datetime.now()

    def main(self, screen, irc_print_queue, irc_flood_timeout_queue, ui_print_queue, ui_status_queue):
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
            curses.curs_set(0)
            curses.nocbreak()


            screen.bkgd(curses.color_pair(1))
            screen.refresh()
            con_buf = []

            win_size = screen.getmaxyx()
            console_width=(((win_size[1]/2)+(win_size[1]/6)))
            status_position=(((win_size[1]/2)+(win_size[1]/6)))
            status_width=(win_size[1]-status_position)
            
            con_win = curses.newwin(win_size[0], console_width, 0, 0)
            stat_win = curses.newwin((win_size[0]/2), status_width, 0, status_position)
            
            con_win.keypad(0)
            con_win.notimeout(0)
            con_win.bkgd(curses.color_pair(2))
            con_win.move(1,1)
            con_line = 1
            con_max_line_len = (console_width-16)
            con_max_lines = (win_size[0]-2)
        
            PINGS=0
            PING_TIME=datetime.datetime.now()
            IRC_MESSAGES=0
            
            while True:
		
                if curses.is_term_resized(win_size[0], win_size[1]):
                    win_size = screen.getmaxyx()
                    screen.clear()
                    curses.resizeterm(win_size[0], win_size[1])
                    console_width=(((win_size[1]/2)+(win_size[1]/6)))
                    status_position=(((win_size[1]/2)+(win_size[1]/6)))
                    status_width=(win_size[1]-status_position)

                    con_win.resize(win_size[0], console_width)
                    con_win.mvwin(0,0)
                    con_win.redrawwin()
                    con_win.erase()
                    con_win.move(1,1)
                    con_line = 1
                    con_max_line_len = (console_width-16)
                    con_max_lines = (win_size[0]-2)

                    buffer_size = len(con_buf)
                    lines = min(buffer_size, con_max_lines)
                    for line in range(0,lines):
                        con_win.move(1,2)
                        con_win.deleteln()
                        con_win.move(con_max_lines,1)
                        con_win.deleteln()
                        con_win.insstr(con_max_lines, 2, con_buf[(buffer_size-lines)+line])

                    con_win.noutrefresh()

                    stat_win.resize((win_size[0]/2), status_width)
                    stat_win.mvwin(0,status_position)
                    stat_win.redrawwin()
                    stat_win.clear()

                    screen.refresh()

                con_win.box()
                con_win.insstr(0, ((console_width/2)-6), "Bot Console")
                if ui_print_queue.empty() == False:
                    line=ui_print_queue.get()
                    if line is None:
                        break #bad queue item                    
                    con_buf.append(line)
                    if len(con_buf) > 512:
                        con_buf.pop(0)
                    con_win.move(1,2)
                    con_win.deleteln()
                    con_win.move(con_max_lines,1)
                    con_win.deleteln()
                    con_win.insstr(con_max_lines, 2, (line))
                    con_win.noutrefresh()
                else:
                    time.sleep(0.004)

                if ui_status_queue.empty() == False:
                    status=ui_status_queue.get()
                    if status[0] == STAT['ping']:
                        PINGS=status[1]
                    elif status[0] == STAT['ping_time']:
                        PING_TIME=status[1]
                    elif status[0] == STAT['irc_messages']:
                        IRC_MESSAGES=status[1]
                else:                  
                    time.sleep(0.004)
                    
                    
                uptime = (datetime.datetime.now() - self.loadDateTime)
                stat_win.move(1,2)
                stat_win.clrtoeol()
                stat_win.insstr(1,2, ("LoadTime     " + self.loadDateTime.strftime('%d/%m/%Y %H:%M:%S')))
                stat_win.move(2,2)
                stat_win.clrtoeol()
                stat_win.insstr(2,2, ("Uptime       " + str(uptime)))
                stat_win.move(3,2)
                stat_win.clrtoeol()
                stat_win.insstr(3,2,  "IRC Flood    ")
                stat_win.move(3,15)
                flood_bar_len = float(min(((FLOOD['flood_messages']), (status_width-21))))
                for x in range(0,min(int(irc_flood_timeout_queue.qsize()*(float(flood_bar_len)/float(FLOOD['flood_messages']))),flood_bar_len)):
                    if irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
                        stat_win.addch(' ',curses.color_pair(5))
                    elif irc_flood_timeout_queue.qsize() >= (FLOOD['flood_messages']/2):
                        stat_win.addch(' ',curses.color_pair(4))
                    else:
                        stat_win.addch(' ',curses.color_pair(3))

                stat_win.insstr(3, int(15+flood_bar_len), (" : " + str(irc_flood_timeout_queue.qsize())))

                stat_win.move(4,2)
                stat_win.clrtoeol()
                stat_win.insstr(4,2,  "IRC MSG Q    " + str(irc_print_queue.qsize()))

                stat_win.move(5,2)
                stat_win.clrtoeol()
                stat_win.insstr(5,2,  "#IRC MSGS    " + str(IRC_MESSAGES))
                
                stat_win.move(6,2)
                stat_win.clrtoeol()
                stat_win.insstr(6,2,  "PINGs        " + str(PINGS))
                
                stat_win.move(7,2)
                stat_win.clrtoeol()
                if PINGS==0:
                    stat_win.insstr(7,2,  "Last PING    Never")                    
                else:
                    stat_win.insstr(7,2,  "Last PING    " + PING_TIME.strftime('%d/%m/%Y %H:%M:%S'))


                stat_win.vline(1,14,'|',(((win_size[1]/2)+(win_size[1]/6))))
                stat_win.box()
                stat_win.insstr(0, ((status_width/2)-5), "Bot Stats")
                con_win.box()
                con_win.insstr(0, ((console_width/2)-6), "Bot Console")
                curses.doupdate()
                con_win.refresh()
                stat_win.refresh()
        except Exception as e:
            print e
            exit()


    def __init__(self, irc_print_queue, irc_flood_timeout_queue, ui_print_queue, ui_status_queue):
        try:
            curses.wrapper(self.main, irc_print_queue, irc_flood_timeout_queue, ui_print_queue, ui_status_queue)
        except KeyboardInterrupt:
            print "Closing"
            exit()
