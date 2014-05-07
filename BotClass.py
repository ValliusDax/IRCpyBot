import sys
import socket
import string
import errno
import os
import threading
import time
import datetime
import Queue
import pickle

from configs.config import CONN, USER, FLOOD, STAT

class BotClass(object):

    masters = [USER['owner']]
    insults = ['fuck you', 'you are a cum guzzling slut', 'is a fishbot', 'takes it in the ass']
    ignore  = ['drew86']
    attacks = ['slaps with fish']
    confirm_messages = ['Of course master!', 'Your will is my command master!', 'I shall obey, master!']
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_messages = Queue.Queue(0)
    irc_print_queue = Queue.Queue(0)
    irc_notice_queue = Queue.Queue(0)
    irc_raw_queue = Queue.Queue(0)
    irc_flood_timeout_queue = Queue.Queue(0)
    irc_raw_received_queue = Queue.Queue(0)
    ui_console_queue = Queue.Queue(0)
    ui_status_queue = Queue.Queue(0)
    warned_users = []
    cautioned_users = []
    irc_chan_list = ""
    waiting_for_response = False;
    channel_count=0
    names_list = ""
    expect_chan_list = False
    silent     = False
    nice       = True
    annoying   = False
    nasty      = False
    vindictive = False
    display_result = True
    random_kick = False
    verbose_console = True
    site = { 'status': "blah",
             'eta'   : "blah",
             'reason': "blah"
             }

    def __init__(self):
        irc_print_commit = threading.Thread(target=self.irc_print_commit)
        irc_print_commit.daemon = True
        irc_print_commit.start()

        try:
          masters_db=open('masters','r')
          self.masters=pickle.load(masters_db)
          masters_db.close()
        except IOError:
          masters_db=open('masters','w')
          pickle.dump(self.masters, masters_db)
          masters_db.close()

        try:
          insults_db=open('insults','r')
          self.insults=pickle.load(insults_db)
          insults_db.close()
        except IOError:
          insults_db=open('insults','w')
          pickle.dump(self.insults, insults_db)
          insults_db.close()

        try:
          ignore_db=open('ignore','r')
          self.ignore=pickle.load(ignore_db)
          ignore_db.close()
        except IOError:
          ignore_db=open('ignore','w')
          pickle.dump(self.ignore, ignore_db)
          ignore_db.close()

        try:
          status_db=open('status','r')
          self.site=pickle.load(status_db)
          status_db.close()
        except IOError:
          status_db=open('status','w')
          pickle.dump(self.site, status_db)
          status_db.close()

        self.ui_console_queue.put("Bot starting")
        self.conn = (CONN['host'], CONN['port'])

    def parsemsg(self,msg):
        complete=msg[1:].split(':',1) #Parse the message into useful data
        info=complete[0].split(' ')
        msgpart=complete[1]
        sender=info[0].split('!')
        # using '.' as the command trigger
        if msgpart[0] == '.' and sender[0] == USER['owner']:
            cmd = msgpart[1:].split(' ')

    def join(self):
        time.sleep(10)
        while True:
          self.ui_console_queue.put("Joining " + CONN['channel'])
          self.sock.send('JOIN ' + CONN['channel'] + '\n') #Joins default channel
          while True:
            self.sock.send('WHOIS '+USER['nick']+'\n')
            time.sleep(3)
            if not CONN['channel'] in self.irc_chan_list:
              break

    def irc_print(self,line):
      if not self.silent:
        self.irc_print_queue.put(line)

    def irc_notice(self,line):
      self.irc_notice_queue.put(line)

    def now_ms(self):
        return int(round(time.time() * 1000))

    def get_flood_timeout(self):
        return (float(FLOOD['flood_time'] + self.now_ms()))

    def irc_print_commit(self):
      IRC_MESSAGES=0
      try:
        while True:
          if self.irc_flood_timeout_queue.empty() == False:
            timeout=self.irc_flood_timeout_queue.queue[0]
            if self.now_ms() >= timeout:
              timeout = self.irc_flood_timeout_queue.get()
              #self.ui_console_queue.put("Timeout expired: " + str(int(timeout)))
              continue

          if self.irc_notice_queue.empty() == False:
            while self.irc_notice_queue.empty() == False:
              line = self.irc_notice_queue.get()
              # if self.irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
                # timeout=((self.get_flood_timeout()-self.now_ms())/1000)
                # if timeout < 0:
                  # self.ui_console_queue.put('Invalid timeout: ' + str(int(timeout)))
                  # break
                # self.ui_console_queue.put("anti flood triggered")
                # self.ui_console_queue.put("message queue size: " + str(self.irc_print_queue.qsize() + self.irc_notice_queue.qsize()))
                # self.ui_console_queue.put("waiting for " + str(timeout) +"s")
                # time.sleep(timeout)
              # else:
              IRC_MESSAGES+=1
              self.ui_status_queue.put((STAT['irc_messages'],IRC_MESSAGES))
              self.sock.send("NOTICE " + line + "\n")
#                self.irc_flood_timeout_queue.put(self.get_flood_timeout())

          if self.irc_print_queue.empty() == False:
            line = self.irc_print_queue.get()
            if self.irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
              timeout=((self.get_flood_timeout()-self.now_ms())/1000)
              if timeout < 0:
                self.ui_console_queue.put('Invalid timeout: ' + str(int(timeout)))
                break
              self.ui_console_queue.put("anti flood triggered")
              self.ui_console_queue.put("message queue size: " + str(self.irc_print_queue.qsize() + self.irc_notice_queue.qsize()))
              self.ui_console_queue.put("waiting for " + str(timeout) +"s")
              time.sleep(timeout)
            else:
              IRC_MESSAGES+=1
              self.ui_status_queue.put((STAT['irc_messages'],IRC_MESSAGES))
              self.sock.send("PRIVMSG " + CONN['channel'] + " :" + line + "\n")
              self.irc_flood_timeout_queue.put(self.get_flood_timeout())

          if self.irc_raw_queue.empty() == False:
            line = self.irc_raw_queue.get()
            self.sock.send(line + '\n')
            
          if (self.irc_flood_timeout_queue.empty() != False) and \
             (self.irc_notice_queue.empty()        != False) and \
             (self.irc_print_queue.empty()         != False) and \
             (self.irc_raw_queue.empty()           != False):
                time.sleep(1)

      except KeyboardInterrupt:
        exit()

    def confirm(self):
      self.irc_print(choice(self.confirm_messages))

    def listen(self):
      while 1:
        line = self.sock.recv(8192)
        self.irc_messages.put(line)

    def connect(self):
      self.ui_console_queue.put("Connecting to " + str(self.conn))
      self.sock.connect(self.conn) #connects to the server
      PINGS=0

      ListenThread = threading.Thread(target=self.listen)
      ListenThread.daemon = True
      ListenThread.start()

      while 1:
        if self.irc_messages.empty() == True:
          time.sleep(0.5)
          continue
        msg = self.irc_messages.get() # recieves server messages
        msg=msg.split('\n')
        for line in msg:
          line=line.rstrip() # removes trailing 'rn'
          if line: # only print meaningful stuff
            if self.verbose_console:
              if (line.find('PRIVMSG') != -1) or \
                 (line.find('NOTICE') != -1):
                message = line.split(':')
                self.ui_console_queue.put(''.join(message[2:])) #server message output
            if line.find('PRIVMSG') == -1:
              if line.find('Found your hostname')!= -1:
                self.ui_console_queue.put('Sending IDENT')
                self.irc_raw_queue.put('NICK ' + USER['nick'] + '\n') #sends nick to the server
                self.irc_raw_queue.put('USER %s 0 0 :%s\n' % (USER['ident'], USER['realname'])) #identify with the server
                JoinThread = threading.Thread(target=self.join)
                JoinThread.daemon = True
                JoinThread.start()
              elif line.find('identify to your nickname')!= -1:
                self.irc_raw_queue.put('IDENTIFY %s\n' % (USER['password'],))
              elif line.find('PING')!= -1:
 #               if self.verbose_console:
                self.ui_console_queue.put('Got PING')
                PINGS = PINGS + 1
                self.ui_status_queue.put((STAT['ping'],PINGS))
                self.ui_status_queue.put((STAT['ping_time'],datetime.datetime.now()))
#                if self.verbose_console:
                self.ui_console_queue.put('Sending PONG')
                self.sock.send('PONG '+line[1]+'\n')
              elif line.find('Nickname is already in use') != -1:
                self.irc_raw_queue.put('GHOST %s %s\n' % (USER['nick'],USER['password']))#doesn't work :(
                self.irc_raw_queue.put('NICK ' + USER['nick'] + '\n')
              elif line.find('ERROR')!= -1:
                self.ui_console_queue.put("That's an error")
                rline=line.rstrip()
                self.ui_console_queue.put(rline)
#                self.sock.close()
#                sys.exit() #Die on errors
              elif line.find('KICK') != -1:
                line=line.rstrip() #removes trailing 'rn'
                line=line.split()
                msg = line[3] + " got kicked"
                self.ui_console_queue.put(msg)
#                self.ui_console_queue.put(line)
                if line[3] == USER['nick']:
                    self.ui_console_queue.put("Hey, That's me!")
#                    JoinThread = threading.Thread(target=self.join)
#                    JoinThread.daemon = True
#                    JoinThread.start()

              elif line.find("%s = %s" % (USER['nick'], CONN['channel'])) != -1: #channel names
                if self.waiting_for_response:
                  rline=line.rstrip('\n') #removes trailing 'rn'
                  self.names_list=self.names_list+rline

                  if line.find(':End of /NAMES list.')!= -1:
                    sline=self.names_list.split()
                    kline=self.names_list.split(':')
                    kline=kline[2].split()
                    self.names_list=""
                    self.waiting_for_response = False

                    if self.random_kick:
                      while True:
                        victim = choice(kline[1:])
                        if victim == USER['owner']:
                          continue
                        elif victim == USER['nick']:
                          continue
                        else:
                          break

                      if any(victim[0] == s for s in ['~', '@', '&', '%', '+']):
                        victim = victim[1:]
                        self.irc_raw_queue.put('KICK %s %s dances on your grave\n' % (CONN['channel'],victim))
                        self.random_kick = False
                      else:
                        self.irc_print('No kicking!')


                    if self.display_result:
                      self.channel_count = self.channel_count + len(sline)
                      self.channel_count = self.channel_count + sum(-5 for i in sline if i == '=')

                      self.irc_print("Current users in channel: " + str(self.channel_count-8))
                      self.channel_count = 0

              elif line.find("378 %s %s" % (USER['nick'], USER['nick'])) != -1:
                if not self.expect_chan_list:
                  self.expect_chan_list=True

              elif line.find("319 %s %s" % (USER['nick'], USER['nick'])) != -1:
                rline=line.rstrip('\n') #removes trailing 'rn'
                rline=line.split(':')
                self.irc_chan_list=rline[2]
                self.expect_chan_list=False
                
              elif line.find("312 %s %s" % (USER['nick'], USER['nick'])) != -1:
                if self.expect_chan_list:
                  self.irc_chan_list=""
              
            elif line.find('PRIVMSG') != -1: #channel joined now parse messages
              self.irc_raw_received_queue.put(line)

class NicknameInUseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

