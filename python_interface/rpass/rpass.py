#!/usr/bin/python

SOCKET_NAME = "/tmp/rpassdsocket"

class rpass:
    """Class to manage encryption/decryption/fetching data."""

    REGEX = 1
    CASE_INSENSITIVE = 2
    ALL_ACCOUNTS = 4

    def __talkToDaemon(self, message):
        """Send a message to daemon and return the response."""
        import socket
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCKET_NAME)

        if (type(message) == str):
            message = message.encode()

        if (type(message) != bytes):
            raise TypeError("Invalid message type")

        s.send(message)

        result = b''
        tmp = s.recv(4096)
        while (len(tmp) > 0):
            result += tmp
            tmp = s.recv(4096)

        return result

    def DecryptFile(self, filename):
        from os.path import isfile,expanduser
        filename = expanduser(filename)
        if not isfile(filename): raise IOError("File not found.")

        return self.__talkToDaemon("DECRYPTFILE {0}".format(filename))

    def EncryptFile(self, infile, outfile = None):
        from os.path import isfile,expanduser
        infile = expanduser(infile)
        if not isfile(infile): raise IOError("File not found.")
        message = "ENCRYPTFILE {0}".format(infile)
        if (outfile):
            outfile = expanduser(outfile)
            message += " {0}".format(outfile)

        self.__talkToDaemon(message)

    def EncryptDataToFile(self, data, outfile):
        from os.path import expanduser
        message = "ENCRYPTDATATOFILE {0} ".format(expanduser(outfile))
        if (type(data) == str):
            data = data.encode()

        message = message.encode() + data

        self.__talkToDaemon(message)

    def GetRpassAccounts(self, filename, sstring, flags):
        from os.path import isfile,expanduser
        import struct
        import re

        filename = expanduser(filename)
        if not isfile(filename): raise IOError("File not found.")

        message = "GETACCOUNTS {0} RPASSACSTART {1} RPASSACSTART ".format(filename,
                                                                         sstring)

        message = message.encode() + struct.pack('i', int(flags))
        accounts = str(self.__talkToDaemon(message), 'utf-8')

        if (len(accounts) == 0): return []

        tmp = ""
        result = []
        for line in accounts.split('\n'):
            if (re.match(r'^\[.+\]$', line)):
                if (len(tmp) > 0):
                    result.append(rpass_account(tmp))
                tmp = line + '\n'
            else:
                tmp += line + '\n'

        if (len(tmp) > 0):
            result.append(rpass_account(tmp))

        return result

    def AddRpassAccount(self, filename, account):
        from os.path import isfile,expanduser
        filename = expanduser(filename)
        if not isfile(filename): raise IOError("File not found.")

        message = "ADDACCOUNT {0} {1}".format(filename, str(account))

        self.__talkToDaemon(message)

    def DeleteRpassAccount(self, filename, account):
        from os.path import isfile,expanduser
        filename = expanduser(filename)
        if not(isfile(filename)): raise IOError("File not found.")

        message = "DELETEACCOUNT {0} {1}".format(filename, account)

        self.__talkToDaemon(message)

    def ForgetCipher(self):
        self.__talkToDaemon("FORGETCIPHER")

    def ChangePassphrase(self, filename):
        from os.path import isfile, expanduser
        filename = expanduser(filename)
        if not(isfile(filename)): raise IOError("File not found.")

        message = "CHANGEPASSPHRASE {0}".format(filename)
        self.__talkToDaemon(message)

class rpass_password_manager(rpass):
    """Class to manage preferences."""

    def __init__(self, conf_file = '~/.rpass.conf', passfile = None):
        """Initialized rpass from an optional configuration file and arguments."""
        from os.path import isfile,expanduser

        self.conf_file = conf_file
        (self.options, self.copyerror) = self.ReadConfigFile(filename = self.conf_file)

        if passfile != None: self.options['passfile'] = passfile
        if ('passfile' not in self.options) or not(self.options['passfile']):
            self.options['passfile'] = '~/.rpasswords'

        self.passfile = expanduser(self.options['passfile'])

    def CopyPass(self, raccount):
        from subprocess import Popen,PIPE

        if 'pass' in raccount.fields:
            echoproc = Popen(['echo', raccount.fields['pass']], shell=False, stdout=PIPE)
            copyproc = Popen(['xclip'], shell=False, stdin=echoproc.stdout)
            return True
        return False


    def AddEntry(self, raccount):
        return rpass.AddRpassAccount(self, self.passfile, raccount)

    def GetAccounts(self, sstring, flags):
        return rpass.GetRpassAccounts(self, self.passfile, sstring, flags)

    def DeleteEntry(self, sstring):
        return rpass.DeleteRpassAccount(self, self.passfile, sstring)

    def ChangePass(self):
        return rpass.ChangePassphrase(self, self.passfile)

    def ReadConfigFile(self, filename, info = {}):
        """When passed a filename, reads the config file for rpass information.

        Returns a dictionary of useful values."""
        import configparser
        from os.path import expanduser,isfile

        if not(isfile(expanduser(filename))):

            # Try to copy the default configuration
            from sys import path

            paths = ["{0}/../share/rpass/", "/usr/share/rpass/", "/usr/local/share/rpass/", "{0}/"]
            paths = [p.format(path[0]) + 'rpass.example.conf' for p in paths]

            try:
                self.CopyDefaultConf(expanduser(filename), paths)
            except IOError as e:
                info['fields'] = []
                return (info, str(e))

        config = configparser.ConfigParser()
        config.read(expanduser(filename))

        if config.has_option('display', 'fields'):
            info['fields'] = [field.strip() for field in
                    config.get('display', 'fields').split(',') if field.strip()]
            if len([f for f in info['fields'] if f.strip()]) == 0: info['fields'] = [None]
        if config.has_option('display', 'color'):
            if config.get('display', 'color').lower()[0] == 'y': info['color'] = True
            else: info['color'] = False

        if config.has_option('general', 'passfile'):
            from os.path import expanduser
            info['passfile'] = expanduser(config.get('general', 'passfile'))

        return (info, None)

    def CopyDefaultConf(self, location, conf_locs):
        """Attempts to copy the default configuration to the specified location."""

        from os.path import expanduser,isfile
        fexample = None
        for p in conf_locs:
            if isfile(p):
                fexample = p
                break

        if not(fexample):
            raise IOError(
                "Could not find default configuration file in any of the following locations: {0}"
                .format(','.join(conf_locs)))
        else:
            from shutil import copyfile
            copyfile(fexample, expanduser(location))

class rpass_account:
    def __init__(self, account_string = None):
        """Initialize an rpass account, optionally from an account string."""
        self.fields = {}
        if (account_string):
            self.ParseAccountString(account_string)

    def ParseAccountString(self, account_string):
        import re

        match = re.search("^\[(.+)\]$", account_string, re.MULTILINE)
        self.name = match.group(1)
        account_lines = (account_string[:match.span()[0]]
                         + account_string[match.span()[1]:]).strip().split('\n')

        fieldpatt = re.compile("^\s*(.*)\s*=\s*(.*)\s*$", re.MULTILINE)
        for line in account_lines:
            self.fields.update([fieldpatt.match(line).groups()])

    def __str__(self):
        if not(hasattr(self, 'name')):
            return ""

        retstring = "[{0}]".format(self.name)
        for (k, v) in self.fields.items():
            retstring += "\n{0}={1}".format(k, v)

        return retstring
