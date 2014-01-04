import curses
import Queue
import threading
import time
import datetime
import sys

from configs.config import FLOOD

class BotUI(object):

    loadDateTime = datetime.datetime.now()

    def main(self,screen,ui_print_queue, irc_flood_timeout_queue, irc_print_queue):
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
            curses.curs_set(0)


            screen.bkgd(curses.color_pair(1))
            screen.refresh()
            
            win_size = screen.getmaxyx()
            console_width=(((win_size[1]/2)+(win_size[1]/6)))
            status_width=(win_size[1]-(((win_size[1]/2)+(win_size[1]/6))))
            status_position=(((win_size[1]/2)+(win_size[1]/6)))
            
            con_win = curses.newwin(win_size[0], console_width, 0, 0)
            stat_win = curses.newwin((win_size[0]/2), status_width, 0, status_position)
            
            con_win.bkgd(curses.color_pair(2))
            con_win.move(1,1)
            con_line = 1
            con_lines = con_line
            con_max_line_len = (console_width-4)
            con_max_lines = (win_size[0]-2)

            while True:
                con_win.box()
                con_win.insstr(0, ((console_width/2)-6), "Bot Console")
                if ui_print_queue.empty() == False:
                    line=ui_print_queue.get()
                    line=line.strip()
                    line=line.rstrip() #removes trailing 'rn'
                    line=line+' '
                    line_len=len(line)
                    start=0
                    end=0

                    while (end < line_len):
                        # print 'line start: '+str(start)
                        # print 'line end: '+str(end)
                        # print 'message length: '+str(line_len)
                        end=line.rfind(' ',start,(end+con_max_line_len))
                        if end <= start:
                            end=line_len

                        con_win.move(1,2)
                        con_win.insdelln(-1)
                        con_win.move(con_max_lines,1)
                        con_win.clrtoeol()
                        con_win.insstr(con_max_lines, 2, ('#'+line[start:end]+'\n'))
                        curses.doupdate()
                        con_win.refresh()
                        start = end
                else:
                    time.sleep(0.04)

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
                for x in range(0,irc_flood_timeout_queue.qsize()):
                    if irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
                        stat_win.addch(' ',curses.color_pair(5))
                    elif irc_flood_timeout_queue.qsize() >= (FLOOD['flood_messages']/2):
                        stat_win.addch(' ',curses.color_pair(4))
                    else:
                        stat_win.addch(' ',curses.color_pair(3))

                stat_win.insstr(3,(15+FLOOD['flood_messages']), (" : " + str(irc_flood_timeout_queue.qsize())))

                stat_win.move(4,2)
                stat_win.clrtoeol()
                stat_win.insstr(4,2,  "IRC Messages " + str(irc_print_queue.qsize()))

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


    def __init__(self,ui_print_queue,irc_flood_timeout_queue,irc_print_queue):
        try:
            curses.wrapper(self.main,ui_print_queue,irc_flood_timeout_queue,irc_print_queue)
        except KeyboardInterrupt:
            print "Closing"
            exit()