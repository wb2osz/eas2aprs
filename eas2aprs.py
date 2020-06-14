#!/usr/bin/python3

# AES SAME to APRS message translator.
# This is just a simple proof of concept which needs more work
# before putting it into general service.
# WB2OSZ, June 2020

import datetime
import time
import os
#import str
import re

# Source address for APRS packets.
# You should put your own callsign here.
# Yeah, I know it should be a command line option, but like I said,
# this is just a quick minimal proof of concept that needs more work.

mycall = 'HAM123'

# APRS generally uses the destination field for a product id.
# APZxxx is experimental so we will pick something in that name range.

product_id = 'APZEAS'

# Here is something interesting you might want to try.
# When direwolf sees "SPEECH" in the destination field, it will send the
# information part to a speech synthesizer rather than transmitting an
# AX.25 frame.  In this case, you would want to omit the addressee part.

#product_id = 'SPEECH'

# Receive and transmit Queue directories for communication with kissutil.
# Modern versions of Linux have a predefined RAM disk at /dev/shm.

# kisssutil puts received APRS packets into the receive queue directory.
# Here we remove those packets and process them.

rq_dir = '/dev/shm/RQ'

# For transmitting, we simply put a file in the transmit queue.
# kissutil will send it to direwolf to be sent over the radio.
# A transmit channel can optionaally...

tq_dir = '/dev/shm/TQ'

# Transmit channel number.

xmit_chan = 0




#----- aprs_msg -----

# Just glue all of the pieces together.
# The only interesting part is ensuring that the addresee is exactly 9 characters.

def aprs_msg(src,dst,via,addr,msgtext):
    """Create APRS 'message' from given components."""

    to = addr.ljust(9)[:9]
    msg = src + '>' + dst
    if via:
        msg += ',' + via
    msg += '::' + to + ':' + msgtext
    return msg




#----- send_msg -----

# Write the given packet to the transmit queue directory.
# If channel is not 0, the packet text is preceded by [chan].

def send_msg (chan, msg):
    """ Add message to transmit queue directory."""

    if not os.path.isdir(tq_dir):
        os.mkdir(tq_dir)
    if not os.path.isdir(rq_dir):
        os.mkdir(rq_dir)

    t = datetime.datetime.now()
    fname = tq_dir + '/' + t.strftime("%y%m%d.%H%M%S.%f")[:17]

    try:
        f = open(fname, 'w')
    except:
        print ("Failed to open " + fname + " for write")
    else:
        if chan > 0:
            f.write('[' + str(chan) + '] ' + msg + '\n')
        else:
            f.write(msg + '\n')
        f.close()
    time.sleep (0.005)	# Ensure unique names



#----- process_eas -----

# Given an EAS SAME message, this calls an external application to 
# convert it to human understandable text.
# The text can exceed the maximum size of an AX.25 frame.
# Luckily, dsame splits it into multiple reasonably sized lines.
# Each of these is transmitted as an APRS "message."

def process_eas (chan, eas):
    """Convert an EAS SAME message to text and transmit."""

    text = os.popen('./dsame.py --msg "' + eas + '"').read().split("\n")
    text2 = list(filter(None, text))
    n = len(text2)
    if n:
        print ("Transmitting...");
        for i in range(0,n):
            msg = aprs_msg (mycall, product_id, '', 'NWS', "[" + str(i+1) + "/" + str(n) + "] " + text2[i])
            print (msg)
            send_msg (xmit_chan, msg)
        #print ("---")
        


#----- parse_aprs -----

def parse_aprs (packet):
    """Parse and APRS packet, possibly prefixed by channel number."""

    print (packet)
    if len(packet) == 0:
        return

    chan = ''
    # Split into address and information parts.
    # There could be a leading '[n]' with a channel number.
    m = re.search (r'^(\[.+\] *)?([^:]+):(.+)$', packet)
    if m:
        chan = m.group(1)	# Still enclosed in [].
        addrs = m.group(2)
        info = m.group(3)
        #print ('<>'+addrs+'<>'+info+'<>')

        if info[0] == '}':
            # Unwrap third party traffic format
            # Preserve any channel.
            if chan:
                parse_aprs (chan + info[1:])
            else:
                parse_aprs (info[1:])
        elif info[0:3] == '{DE':
            # APRS "user defined data" format for EAS.
            #print ('Process "message" - ' + info)
            process_eas (chan, info[3:])
        else:
            print ('Not APRS "user defined data" format - ' + info)
    else:
        print ('Could not split into address & info parts - ' + packet)


#----- recv_loop -----

def recv_loop():
    """Poll the receive queue directory and call parse_aprs when something found."""

    if not os.path.isdir(tq_dir):
        os.mkdir(tq_dir)
    if not os.path.isdir(rq_dir):
        os.mkdir(rq_dir)

    while True:
        time.sleep(1)
        #print ('polling')
        try:
            files = os.listdir(rq_dir)
        except:
            print ('Could not get listing of directory ' + rq_dir + '\n')
            quit()

        files.sort()
        for f in files:
            fname = rq_dir + '/' + f
            #print (fname)
            if os.path.isfile(fname):
                print ('---')
                print ('Processing ' + fname + ' ...')
                with open (fname, 'r') as h:
                    for m in h:
                        m.rstrip('\n')
                        parse_aprs (m.rstrip('\n'))
                os.remove(fname)
            else:
 		#print (fname + ' is not an ordinary file - ignore')
                pass



#----- start here -----

recv_loop()
