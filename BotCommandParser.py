import Queue
import threading
import time
import threading
import pickle

from random import choice
from configs.config import USER

class BotCommandParser(object):

  def main(self, Bot):
    ParseThread = threading.Thread(target=self.parse_commands, args=(Bot,))
    ParseThread.daemon = True
    ParseThread.start()
  
  def parse_commands(self, Bot):
    ME=USER['nick']+'!'
    while 1:
      if (Bot.irc_raw_received_queue.empty() == False):
        line = Bot.irc_raw_received_queue.get()
      else:
        time.sleep(0.1)
        continue
        
      rline=line.rstrip() #removes trailing 'rn'
      dline=rline.split(':')
      dline=''.join(dline[2:])
      sline=rline.split()
      pline=' '.join(sline[3:])
      pline=pline[1:]
      bline=sline[0][:].split("!")
      user=bline[0][1:]
      command=sline[3][1:]
      if any(user == s for s in Bot.ignore):
        Bot.ui_console_queue.put("I am ignoring " + user)
      if (line.lower().find(USER['nick'].lower()) != -1) and (line.lower().find('bot') != -1):
        Bot.irc_print('No! I\'m a ballerina')
      if len(sline) >= 4:
        arguments=sline[4:]
      if command == ME != -1:
        Bot.ui_console_queue.put("Got Command: " + pline + " from " + user)
        if any(user == s for s in Bot.masters):

          numargs=len(arguments)
          if numargs == 0:
            Bot.irc_print('Yeeees, ' + user + '?')
          elif (arguments[0] == 'add' != -1) and (numargs > 1):
            if (arguments[1] == 'master' != -1) and (numargs > 2):
              Bot.masters.append(arguments[2])
              masters_db=open('masters','w')
              pickle.dump(Bot.masters, masters_db)
              masters_db.close()
              Bot.irc_print(arguments[2] + " is now one of my masters")
            if (arguments[1] == 'insult' != -1) and (numargs > 2):
              Bot.insults.append(' '.join(arguments[2:]))
              insults_db=open('insults','w')
              pickle.dump(Bot.insults, insults_db)
              insults_db.close()
              Bot.confirm()
            if (arguments[1] == 'ignore' != -1) and (numargs > 2):
              if (arguments[2] != USER['owner']  != -1):
                Bot.ignore.append(arguments[2])
                ignore_db=open('ignore','w')
                pickle.dump(Bot.ignore, ignore_db)
                ignore_db.close()
                Bot.confirm()

          elif (arguments[0] == 'list' != -1) and (numargs > 1):
            if (arguments[1] == 'masters' != -1) and (numargs > 1):
              for i , val in enumerate(Bot.masters):
                Bot.irc_notice(user + ' ' + Bot.masters[i])
            if (arguments[1] == 'insults' != -1) and (numargs > 1):
              for i , val in enumerate(Bot.insults):
                Bot.irc_notice(user + ' ' + Bot.insults[i])
            if (arguments[1] == 'ignore' != -1) and (numargs > 1):
              for i , val in enumerate(Bot.ignore):
                Bot.irc_notice(user + ' ' + Bot.ignore[i])

          elif (arguments[0] == 'forget' != -1) and (numargs > 1):
            if (arguments[1] == 'master' != -1) and (numargs > 1):
              if (arguments[2] != USER['owner']  != -1):
                if arguments[2] in Bot.masters:
                  Bot.masters.remove(arguments[2])
                  masters_db=open('masters','w')
                  pickle.dump(Bot.masters, masters_db)
                  masters_db.close()
                  Bot.irc_print(arguments[2] + " is no longer one of my masters")
            if (arguments[1] == 'insult' != -1) and (numargs > 1):
              if arguments[2:] in Bot.insults:
                Bot.insults.remove(arguments[2:])
                insults_db=open('insults','w')
                pickle.dump(Bot.insults, insults_db)
                insults_db.close()
                Bot.irc_print(arguments[2:] + " forgotten")
            if (arguments[1] == 'ignore' != -1) and (numargs > 1):
              if arguments[2] in Bot.ignore:
                Bot.ignore.remove(arguments[2])
                ignore_db=open('ignore','w')
                pickle.dump(Bot.ignore, ignore_db)
                ignore_db.close()
                Bot.irc_print(arguments[2] + " I'm listening")

          elif (arguments[0] == 'insult' != -1) and (numargs > 1):
            if (arguments[1] != USER['owner'] != -1) and (numargs > 1):
              Bot.irc_print(arguments[1] + " " + choice(Bot.insults))

          elif (arguments[0] == 'attack' != -1) and (numargs > 1):
            if (arguments[1] != USER['owner'] != -1) and \
               (arguments[1] != USER['nick']  != -1) and \
               (numargs > 1) and not Bot.nice:
                  Bot.irc_raw_queue.put('KICK %s %s dances on your grave\n' % (CONN['channel'],arguments[1]))

          elif (arguments[0] == 'tldr' != -1) and (numargs > 1):
            if (arguments[1] == 'set' != -1) and (numargs > 2):
              if (arguments[2] == 'status' != -1) and (numargs > 3):
                Bot.site['status'] = ' '.join(arguments[3:])
              elif (arguments[2] == 'eta' != -1) and (numargs > 3):
                Bot.site['eta'] = ' '.join(arguments[3:])
              elif (arguments[2] == 'reason' != -1) and (numargs > 3):
                Bot.site['reason'] = ' '.join(arguments[3:])
              status_db=open('status','w')
              pickle.dump(Bot.site, status_db)
              status_db.close()

          elif (arguments[0] == 'goto' != -1) and (numargs > 1):
            Bot.irc_print('bye bye')
            old_chan = CONN['channel']
            CONN['channel']=arguments[1]
            Bot.irc_raw_queue.put('PART ' + old_chan + '\n')

          elif (arguments[0] == 'dance!' != -1):
            if (user == USER['owner']  != -1):
              if not Bot.waiting_for_response:
                Bot.display_result = False
                Bot.random_kick = True
                Bot.waiting_for_response = True
                Bot.sock.send('NAMES ' + CONN['channel'] + '\n') #Joins default channel
            else:
              Bot.irc_print('Fuck off ' + user +'!')

          elif (arguments[0] == 'mood?' != -1):
            if Bot.nice:
              Bot.irc_notice(user + ' I\'m being nice.')
            elif Bot.annoying:
              Bot.irc_notice(user + ' I\'m being annoying.')
            elif Bot.nasty:
              Bot.irc_notice(user + ' I\'m being nasty.')
            elif Bot.vindictive:
              Bot.irc_notice(user + ' I\'m being vindictive.')
            else:
              Bot.irc_notice(user + ' I\'m being random (aka, mood not known).')

          elif (arguments[0] == 'shutup!' != -1):
            Bot.silent = True

          elif (arguments[0] == 'sing!' != -1):
            Bot.silent = False


          elif (arguments[0] == 'nice!' != -1):
            if user == USER['owner'] != -1:
              Bot.nice       = True
              Bot.annoying   = False
              Bot.nasty      = False
              Bot.vindictive = False
            else:            
              Bot.irc_print('Nuh uh ' + user +'!')


          elif (arguments[0] == 'annoying!' != -1):
            if user == USER['owner'] != -1:
              Bot.nice       = False
              Bot.annoying   = True
              Bot.nasty      = False
              Bot.vindictive = False
            else:            
              Bot.irc_print('Nuh uh ' + user +'!')


          elif (arguments[0] == 'nasty!' != -1):
            if user == USER['owner'] != -1:
              Bot.nice       = False
              Bot.annoying   = False
              Bot.nasty      = True
              Bot.vindictive = False
            else:            
              Bot.irc_print('Nuh uh ' + user +'!')


          elif (arguments[0] == 'vindictive!' != -1):
            if user == USER['owner'] != -1:
              Bot.nice       = False
              Bot.annoying   = False
              Bot.nasty      = False
              Bot.vindictive = True
            else:            
              Bot.irc_print('Nuh uh ' + user +'!')

          elif (arguments[0] == 'commands' != -1):
              Bot.irc_notice(user + ' Commands:')
              Bot.irc_notice(user + '           list {masters|insults|ignore}')
              Bot.irc_notice(user + '           add {master|insult|ignore} <username or insult>')
              Bot.irc_notice(user + '           forget {master|insult|ignore} <username or insult>')
              Bot.irc_notice(user + '           insult <username>')
              Bot.irc_notice(user + '           attack <username>')
              Bot.irc_notice(user + '           tldr{set} {site|status|eta} <info>')
              Bot.irc_notice(user + '           goto <channel>')
              Bot.irc_notice(user + '           shutup!')
              Bot.irc_notice(user + '           sing!')
              Bot.irc_notice(user + '           dance!')
              Bot.irc_notice(user + '           nice!')
              Bot.irc_notice(user + '           annoying!')
              Bot.irc_notice(user + '           nasty!')
              Bot.irc_notice(user + '           vindictive!')
              Bot.irc_notice(user + '           mood?')
              Bot.irc_notice(user + '           commands')

          else:
            Bot.irc_print('Huh?')

        else:
          Bot.irc_print("You're not the Master!")

      elif user.find("Digital")!= -1:

        if user in Bot.cautioned_users and not Bot.nice:
          Bot.ui_console_queue.put('Kicked ' + user)
          Bot.irc_raw_queue.put('KICK %s %s dances on your grave\n' % (CONN['channel'],user))
        if not Bot.vindictive:
          Bot.cautioned_users.remove(user);
        elif user in Bot.warned_users and Bot.nasty:
          Bot.irc_notice(user + ' Hey, ' + user + ' last warning, change your nick! type \"/nick your name\" ')
          Bot.cautioned_users.append(user);
          Bot.warned_users.remove(user);
        elif Bot.annoying:
          Bot.irc_notice(user + ' Hey, ' + user + ' could you use your empornium username please, just type \"/nick your name\" ')
          Bot.warned_users.append(user);

        elif rline.find("prettiest mod")!= -1:
          Bot.irc_print('That would be kchase')
        elif rline.find("sexiest mod")!= -1:
          Bot.irc_print('NellyFrozen... Hands down!')
        # elif pline.lower() == 'hi'!= -1:
            # Bot.irc_print("Well hello there " + user)
        # elif pline.lower() == 'hello'!= -1:
            # Bot.irc_print("Well hello there " + user)
        # elif pline.lower() == 'bye'!= -1:
            # Bot.irc_print("Come back soon " + user + "!")
        # elif pline.lower() == 'good night'!= -1:
            # Bot.irc_print("Sweat dreams " + user + "!")
        # elif pline.lower() == 'night'!= -1:
            # Bot.irc_print("Sweat dreams " + user + "!")

      elif pline == '!users'!= -1:
        if not Bot.waiting_for_response:
          Bot.display_result = True
          Bot.waiting_for_response = True
          Bot.sock.send('NAMES ' + CONN['channel'] + '\n') #Joins default channel

      elif pline == '!peak'!= -1:
        if not Bot.waiting_for_response:
          Bot.display_result = True
          Bot.waiting_for_response = True
          Bot.sock.send('NAMES ' + CONN['channel'] + '\n') #Joins default channel

      elif ((((dline.lower().find('site')    != -1) or \
              (dline.lower().find('emp')     != -1) or \
              (dline.lower().find('tracker') != -1))and \
              (dline.lower().find('?')       != -1))and \
              (dline.lower().find('child')       == -1)):
              if (dline.lower().find('what') != -1) or \
                 (dline.lower().find('why')  != -1):
  #                                      Bot.irc_print(Bot.site['reason'])
                        Bot.irc_notice(user + ' ' + Bot.site['reason'])

              elif (dline.lower().find('when') != -1) or \
                   (dline.lower().find('long') != -1) or \
                   (dline.lower().find('time') != -1) or \
                   (dline.lower().find('estimate') != -1) or \
                   (dline.lower().find('back') != -1):
  #                                      Bot.irc_print(Bot.site['eta'])
                        Bot.irc_notice(user + ' ' + Bot.site['eta'])

              elif (dline.lower().find('up')       != -1) or \
                   (dline.lower().find('down')     != -1) or \
                   (dline.lower().find('broke')    != -1) or \
                   (dline.lower().find('working')  != -1) or \
                   (dline.lower().find('online')   != -1) or \
                   (dline.lower().find('offline')  != -1):
  #                                      Bot.irc_print(Bot.site['status'])
                        Bot.irc_notice(user + ' ' + Bot.site['status'])

        # else:
            # Bot.ui_console_queue.put(pline)
            
  def __init__(self, Bot):
    try:
        self.main(Bot)
    except KeyboardInterrupt:
        print "Closing"
        exit()