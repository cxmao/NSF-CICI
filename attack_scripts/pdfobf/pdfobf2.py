#!/usr/bin/python

import sys
import os
import errno
import argparse
import fcntl
import struct
import signal
import socket
import signal
import threading
from multiprocessing import Lock
from functools import partial

import pdb

DEBUG = 0
VERBOSE = 0
STEALTH_IPD_RST = 0 # Inter-packet delay minimized.
STEALTH_IPD_Q = 0 # Inter-packet delay constant or not.
STEALTH_IPD_TIME = 0.300 # Time between packets.
STEALTH_PS = 0 # Packet size constant or not.
STEALTH_PS_SIZE = 2000 # Size of packets. Minimum 1200 (PDF and base64 adds alot of overhead).
                        # Max 1448 (OS can not send more than that).
STEALTH_PADDING = '0'
#STEALTH_IPD_PAUSE = 0 # Inter-packet delay time prevents service, pause interrupt.

host = None
#ipd_cnt = 0

class ProgArgs():
    def __init__(self):
        self.type = ""
        self.loc = 0
        self.rem = 0

class Obfuscate():
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file

    def obf(self, data):
        self.clear_pdf()
        data = self.encode_base64(data)
        # Insert protocol inside PDF file.
        self.write_fpdf(data)
        # Read PDF file for binary reading.
        with open(self.pdf_file, 'rb') as fp:
            data = fp.read()

        return data

    def deobf(self, data):
        self.clear_pdf()
        if STEALTH_PS: # Or could just do the check no matter what
            data = self.remove_padding(data)
        # Write PDF contents to flat file.
        with open(self.pdf_file, 'wb') as fp:
            fp.write(data)
        # Read PDF file with PDF API for binary reading.
        data = str()
        data = self.read_pypdf()
        data = self.decode_base64(data)

        return data

    def encode_base64(self, data):
        import base64
        return base64.b64encode(data)
    def decode_base64(self, data):
        import base64
        return base64.b64decode(data)

    def pdf_exist(self, data):
        pos = data.find("%PDF-")
        # Ensure PDF is in the data.
        if pos == -1:
            ret = False
        else:
            ret = True

        return ret

    def clear_pdf(self):
        # Check if file exists and clear contents of file.
        if not os.path.isfile(self.pdf_file):
            open(self.pdf_file, 'w+').close()
        if os.stat(self.pdf_file).st_size is 0:
            open(self.pdf_file, 'w').close()

    def write_fpdf(self, data):
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.write(5, data)
        pdf.output(self.pdf_file, 'F')

    def read_pdfminer(self):
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfpage import PDFPage
        from cStringIO import StringIO
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = file(self.pdf_file, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text
    def read_pdftotext(self):
        import pdftotext
        data = str()
        with open(self.pdf_file, 'rb') as fp:
            pdf = pdftotext.PDF(fp)
        for pg in pdf:
            data += pg

        return data
    def read_pypdf(self):
        import PyPDF2
        data = str()
        # Read PDF file using PyPDF2 API to get contents.
        with open(self.pdf_file, 'rb') as fp:
            pdf = PyPDF2.PdfFileReader(fp)
            for pg_num in range(0, pdf.numPages):
                pg = pdf.getPage(pg_num)
                data += pg.extractText()

        return data

class Tunnel():
    def __init__(self, name):
        self.name = name
        self.orig_sh = signal.getsignal(signal.SIGINT)
        self.orig_sh2 = signal.getsignal(signal.SIGALRM)
        self.est = False
        self.init_ipd = True
        self.persistent = True
        self.timeout = 0.3 # Timeout value for non-blocking
        self.buff = str() # In case OS can't read data all at once.
        # Max bytes to read at once.
        if STEALTH_PS:
            self.RECVSIZE = STEALTH_PS_SIZE
        else:
            self.RECVSIZE = 65535
        if STEALTH_IPD_Q:
            self.q = list()
        if STEALTH_IPD_RST or STEALTH_IPD_Q:
            self.ipd_delay = STEALTH_IPD_TIME
            self.ipd = False
            self.start_ipd = 10
            self.cnt_offset = 10
            self.cnt_ipd = 0
            self.cnt_real = 0

    def getname(self):
        return self.name
    def get_sh(self):
        return self.orig_sh

    # States if the client side program will keep running after all connections
    # are closed.
    def is_persistent(self):
        return self.persistent
    def set_persistent(self, data):
        self.persistent = data

    def set_est(self, data):
        self.est = data
    def is_est(self):
        return self.est

    def getsocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Get IP address of interface.
    def getifaddr(self, intf):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ret = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', intf[:15]))[20:24])
        return ret

    def insert_padding(self, len_data):
        padding = str()
        num = STEALTH_PS_SIZE - len_data
        for cnt in xrange(0, num, 1):
            padding += STEALTH_PADDING
        return padding
    def remove_padding(self, data):
        pos = data.rfind("%%EOF")
        # Ensure end of PDF was found.
        if pos != -1:
            # Do not delete "%%EOF\n" part from string.
            pos += 6
            # Check if padding exists at end and if so
            # remove it.
            padding = False
            for cnt in xrange(pos, len(data)):
                if data[cnt] == STEALTH_PADDING:
                    padding = True
                else:
                    padding = False
                    break
            if padding:
                data = data[:pos]
        else:
            cnt = 0
            for cnt in range(len(data), 0, -1):
                if data[cnt-1] != STEALTH_PADDING:
                    break
                cnt += 1
            if DEBUG:
                print('b4 remove padding:', data)
            data = data[:cnt]
            if DEBUG:
                print('af remove padding:', data)
                print

        return data
    def filler(self):
        padding = str()
        for cnt in xrange(0, STEALTH_PS_SIZE, 1):
            padding += STEALTH_PADDING
        return padding
    def filler_exist(self, data):
        padding = False
        for cnt in xrange(0, len(data)):
            if data[cnt] == STEALTH_PADDING:
                padding = True
            else:
                padding = False
                break
        if padding:
            print 'filler exist'
        else:
            print 'filler  does not'
            print data[cnt]
        return padding
    def disSig(self):
        #signal.setitimer(signal.ITIMER_REAL, 0)
        signal.siginterrupt(signal.SIGALRM, False)
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
        print 'dis', signal.getitimer(signal.ITIMER_REAL)
        #alrm = signal.alarm(0)
        #print alrm
    def enSig(self):
        signal.siginterrupt(signal.SIGALRM, True)
        signal.signal(signal.SIGALRM, TIMhandler)
        print 'en', signal.getitimer(signal.ITIMER_REAL)[0], bool(signal.getitimer(signal.ITIMER_REAL)[0])
        if self.ipd and not bool(signal.getitimer(signal.ITIMER_REAL)[0]):#not STEALTH_IPD_PAUSE and 
            print 'rest'
            os.kill(os.getpid(), signal.SIGALRM)
            print 'raised'
        #signal.alarm(alrm)
    def rstIPD(self):
        if DEBUG:
            print 'rstIPD'
        if not self.ipd and self.cnt_real < self.start_ipd:
            return
        else:
            self.ipd = True
        ipd = self.ipd_delay
        if self.init_ipd:
            self.init_ipd = False
            # Need a slight offset of the alarms between the endpoints.
            if STEALTH_IPD_RST and self.getname() is "server":
                ipd = STEALTH_IPD_TIME * 2
            else:
                ipd = STEALTH_IPD_TIME
        else:
            # Swap who will send the next filler packet.
            if STEALTH_IPD_RST and (ipd is STEALTH_IPD_TIME):
                ipd = STEALTH_IPD_TIME * 2
            else:
                ipd = STEALTH_IPD_TIME
            #if self.cnt_ipd > self.cnt_real + self.cnt_offset:
            #    ipd *= (self.cnt_ipd % 2)
            #    self.cnt_ipd = 0
            #    self.cnt_real = 0

        self.ipd_delay = ipd
        signal.setitimer(signal.ITIMER_REAL, ipd)
        print signal.getitimer(signal.ITIMER_REAL)
        #signal.alarm(ipd)
    def q_entry(self):
        data = ""
        ret = self.q
        if ret:
            data = self.q.pop(0)
        return ret, data

    def _get_data(self, recv, tunnel):
        if tunnel and STEALTH_PS and self.buff:
            n = STEALTH_PS_SIZE - len(self.buff)
        else:
            n = self.RECVSIZE

        if tunnel and (STEALTH_IPD_RST or STEALTH_IPD_Q):
            # Disable interrupt, can't interrupt receive function
            # or it will cause the OS to close the connection.
            self.disSig()
        if DEBUG:
            print '---- get ----- start'
        ret, data = self.__get_data(recv, n)
        if DEBUG:
            print '---- get ----- end'
        if tunnel and (STEALTH_IPD_RST or STEALTH_IPD_Q):
            # Re-enable interrupt.
            self.enSig()

        return ret, data

    def __get_data(self, recv, n):
        ret = None
        data = None
        while True:
            try:
                data = recv(n)
            except socket.timeout, errs:
                err = errs.args[0]
                if err == "timed out":
                    # No data available.
                    ret = 0
                    break
                else:
                    # Error occured
                    print "Error: Timeout, receiving data."
                    print errs
                    break
            except socket.error, errs:
                # Error occured
                if STEALTH_IPD_RST or STEALTH_IPD_Q:
                    if errs.args[0] != errno.EINTR:
                        print "Error: Receiving data."
                        print errs
                        break
                    print 'what?', errs, ret
                else:
                    print "Error: Receiving data."
                    print errs
                    break
            else:
                if not data:
                    # Connection closed.
                    if DEBUG:
                        print 'conn closed'
                    ret = -1
                else:
                    # Got data.
                    ret = 1
                break
        return ret, data

    def _send_data(self, send, data, obf):
        if STEALTH_IPD_Q or STEALTH_IPD_RST:
            if STEALTH_IPD_Q and obf is 1:
                self.q.append(data)
            else: #if self.pdf_exist(data):
                if obf is 2:
                    self.cnt_ipd += 1
                if obf is 1:
                    self.cnt_real += 1
                    if DEBUG:
                        print 'gonna disable, obf'
                    # Disable interrupt.
                    self.disSig()
                if obf or (not obf and not self.filler_exist(data)):
                    with open('debug.txt', 'a') as fp:
                        fp.write(data)
                        fp.write('\n\n')
                    if DEBUG:
                        print '---- send ----- start'
                    self.__send_data(send, data, obf)
                    if DEBUG:
                        print '---- send ----- end'
                if obf is 1:
                    # Re-enable interrupt.
                    self.enSig()
        else:
            self.__send_data(send, data, obf)
    def __send_data(self, send, data, obf):
        sent = 0
        tot = len(data)
        if STEALTH_PS:
            buff = data
        while sent < tot:
            if obf:
                if STEALTH_PS:
                    len_data = len(buff)
                    while True:
                        if len_data >= STEALTH_PS_SIZE:
                            len_data = STEALTH_PS_SIZE
                        # Grab limited range of data.
                        data = buff[:len_data]
                        if not DEBUG:
                            # Obfuscate data in PDF.
                            data = self.obf(data)
                        # Ensure were not sending too much data.
                        if len(data) > STEALTH_PS_SIZE:
                            len_data -= 1
                        else:
                            break
                    buff = buff[len_data:]
                    sent += len_data
                    # Ensure were not sending too little data.
                    if len(data) < STEALTH_PS_SIZE:
                        #print('i b4', data)
                        data += self.insert_padding(len(data))
                        #print('i af', data)
                        #print
                else:
                    if not DEBUG:
                        # Obfuscate data in PDF.
                        data = self.obf(data)
                    sent = tot

            else:
                if not DEBUG:
                    data = self.deobf(data)
                elif STEALTH_PS:
                    data = self.remove_padding(data)
                sent = tot
            send(data)
            if (STEALTH_IPD_RST or STEALTH_IPD_Q) and obf:
                # Reset alarm timer.
                self.rstIPD()

    def tunnel(self, tx, rx):
        # Check if client's connection exists.
        if rx.getname() is "client" and not rx.is_est():
            rx.est_conn()
            if VERBOSE:
                print "All connections established. Start sending data."
        tunnel = False
        if (self.getname() is "client" and rx.getname() is "client") or \
        (self.getname() is "server" and rx.getname() is "server"):
            tunnel = True
        if DEBUG:
            print '----------------------- start', tunnel
        ret, data = rx.get_data(tunnel)
        # Check if TCP connection shutdown.
        if ret is None:
            # Error occured. Close connections and exit.
            clean_exit(self, tx, rx)
        elif ret is -1:
            if STEALTH_IPD_RST or STEALTH_IPD_Q:
                # Disable alarm timer.
                self.disSig()
                if VERBOSE:
                    print "Disabled interrupt."
            # Close connections.
            rx.close_conn()
            if tx.getname() is "server" or (tx.getname() is "client" and tx.is_est()):
                tx.close_conn()
            if VERBOSE:
                print "Waiting for new connection..."
            # Keep the program up and waiting for next connection.
            if self.getname() is "server":
                # Keep the victim side up and waiting for next connection
                # from client side.
                self.est_conn()
            elif self.getname() is "client" and self.is_persistent():
                # Keep the attacker side up for convienience.
                if rx.getname() is "server":
                    rx.est_conn()
                elif tx.getname() is "server":
                    tx.est_conn()
            if STEALTH_IPD_Q or STEALTH_IPD_RST:
                # Initialize timer.
                self.init_ipd = True
                self.rstIPD()
        elif ret:
            if DEBUG:
                print 'proc data'
            senddata = False
            #if tunnel:
            #    tunnel = False
            #else:
            #    tunnel = True
            if tunnel:
                if DEBUG:
                    print 'tunnel'
                # Determine if excess data was read before.
                if self.buff:
                    if DEBUG:
                        print 'merge data'
                    data = self.buff + data
                    self.buff = str()
                pos = data.rfind("%%EOF")
                if (STEALTH_PS and len(data) == STEALTH_PS_SIZE) or (not STEALTH_PS and pos != -1) or DEBUG:
                    if DEBUG:
                        print 'send data'
                    # Send data.
                    senddata = True
                    # Determine if excess amount of data was read.
                    pos += 6
                    if not DEBUG and (not STEALTH_PS and pos != len(data)):
                        self.buff += data[pos:]
                else:
                    if DEBUG:
                        print 'old data'
                    # Not enough data was read.
                    self.buff += data
            else:
                # Send data.
                senddata = True

            if senddata:
                if (self.getname() is "client" and tx.getname() is "client") or \
                (self.getname() is "server" and tx.getname() is "server"):
                    obf = 1
                else:
                    obf = 0
                # Check if client's connection exists.
                if tx.getname() is "client" and not tx.is_est():
                    tx.est_conn()
                    if VERBOSE:
                        print "All connections established. Start sending data."
                tx.send_data(data, obf)
        if DEBUG:
            print '----------------------- end', tunnel, ret


class Client(Tunnel, Obfuscate):
    def __init__(self, port, pdf_file, ip = "127.0.0.1"):
        Tunnel.__init__(self, "client")
        Obfuscate.__init__(self, pdf_file)
        self.port = port
        self.dstip = ip

    def set_blocking(self):
        self.sock.settimeout(None)
    def set_nonblocking(self):
        self.sock.settimeout(self.timeout)

    def est_conn(self):
        self.getsocket()
        if VERBOSE:
            print "Attempting a connection as a client."
        self.sock.connect((self.dstip, self.port))
        if VERBOSE:
            print "Established a connection as a client."
        self.set_nonblocking()
        self.set_est(True)
    def send_data(self, data, obf):
        self._send_data(self.sock.send, data, obf)
    def get_data(self, tunnel):
        #return self.sock.recv(self.RECVSIZE)
        return self._get_data(self.sock.recv, tunnel)
    def close_conn(self):
        self.set_est(False)
        self.sock.close()
        if VERBOSE:
            print "Connection shutdown as a client."

class Server(Tunnel, Obfuscate):
    def __init__(self, port, pdf_file, intf = "lo"):
        Tunnel.__init__(self, "server")
        Obfuscate.__init__(self, pdf_file)
        self.port = port
        self.ip = self.getifaddr(intf)
        self.est_conn()

    def set_blocking(self):
        self.sock.settimeout(None)
    def set_nonblocking(self):
        self.conn.settimeout(self.timeout)

    def est_conn(self):
        self.getsocket()
        if VERBOSE:
            print "Attempting a connection as a server."
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        if VERBOSE:
            print "Established a connection as a server."
        self.set_nonblocking()
        self.set_est(True)
    def send_data(self, data, obf):
        self._send_data(self.conn.send, data, obf)
    def get_data(self, tunnel):
        #return self.conn.recv(self.RECVSIZE)
        return self._get_data(self.conn.recv, tunnel)
    def close_conn(self):
        self.set_est(False)
        self.conn.close()
        self.sock.close()
        if VERBOSE:
            print "Connection shutdown as a server."

def parse_args():
    args = None
    if len(sys.argv) is 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print "\nThis program can best be seen as tunneler. The ", sys.argv[0], " needs"
        print "to be executed before the ssh command is executed. \n"
        print "For the ssh command, the user will use a 'username' that's already"
        print "established on the victim server and provide the local port number that's"
        print "used in the ", sys.argv[0] ," command."
        print "\nExample"
        print "client side: ", sys.argv[0], " c 2222 12345"
        print "              ssh <username>@127.0.0.1 -p 2222"
        print "server side: ", sys.argv[0] , " s 12345 22\n"
    elif len(sys.argv) is 4 and ((sys.argv[1] is 'c' or sys.argv[1] is 's') and \
            sys.argv[2].isdigit() and sys.argv[3].isdigit()):
        args = ProgArgs()
        args.type = sys.argv[1]
        args.loc = int(sys.argv[2])
        args.rem = int(sys.argv[3])
    else:
        print "ERROR: User input required."
        print "<c | s> <LOCAL PORT NUMBER> <REMOTE PORT NUMBER>. State 'c' for client and 's' for server"


    return args

def clean_exit(obf, ct, sv):
    signal.signal(signal.SIGINT, obf.get_sh())
    ct.close_conn()
    sv.close_conn()
    exit(1)

def TIMhandler(sig, frame):
    #global ipd_cnt
    #global STEALTH_IPD_PAUSE
    if sig == signal.SIGALRM:
        print "------Alarm----- start"
        #ipd_cnt += 1
        #if ipd_cnt > 2:# or STEALTH_IPD_PAUSE:
            #STEALTH_IPD_PAUSE = 1
            #ipd_cnt -= 1
        #elif ipd_cnt is 0:
            #STEALTH_IPD_PAUSE = 0
        #if not STEALTH_IPD_PAUSE:
            #ipd_cnt += 1
        if STEALTH_IPD_Q:
            ret, data = host.q_entry()
            if not ret:
                #TODO
                data = host.filler()
        else:
            #TODO
            data = host.filler()
        if host.is_est():#not STEALTH_IPD_PAUSE and 
            print 'world'
            host.send_data(data, 2)
        print "------Alarm----- end"

def Main(args):
    global host
    def INThandler(sig, frame):
        obf.set_est(False)
        obf.set_persistent(False)

    if VERBOSE:
        print "Initialize variables."

    port_loc = args.loc
    port_rem = args.rem
    # Start program initiating a connection.
    if args.type is 'c':
        obf = Client(port_rem, "ct.pdf", "192.168.0.2")
        ct = obf
        sv = Server(port_loc, "ct.pdf")
    # Start program waiting for connection.
    else:
        obf = Server(port_loc, "sv.pdf", "eth0")
        sv = obf
        ct = Client(port_rem, "sv.pdf")
    host = obf

    if STEALTH_IPD_Q or STEALTH_IPD_RST:
        # Define Alarm interrupt handler.
        #signal.signal(signal.SIGALRM, partial(TIMhandler, obf))
        signal.signal(signal.SIGINT, INThandler)
        signal.signal(signal.SIGALRM, TIMhandler)

    if VERBOSE:
        print "Servers listening for connection..."
        vbs = 0
    else:
        vbs = 1
    # Finish establishing connections.
    obf.tunnel(ct, sv)
    swp = None
    tx = sv
    rx = ct

    while obf.is_est() or (obf.getname() is "client" and obf.is_persistent()):
        if VERBOSE and vbs is 0:
            if DEBUG:
                print obf.getname()
            vbs = 1
        # Tunnel data.
        obf.tunnel(tx, rx)
        swp = tx
        tx = rx
        rx = swp

    if VERBOSE:
        print "All connections closed."

    signal.signal(signal.SIGINT, obf.get_sh())

if __name__ == "__main__":
    args = parse_args()
    if args is not None:
        Main(args)