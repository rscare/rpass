#!/usr/bin/python

def PrintAccountInfo(raccount, keys, color, pfull = False, batch = False):
    fgnescape = '\x1b[0;38;5;{0}m'
    bgnescape = '\x1b[0;48;5;{0}m'
    fgbescape = '\x1b[1;38;5;{0}m'

    ac_color = ''
    user_color = ''
    pass_color = ''
    txtreset = ''

    if color:
        ac_color = fgbescape.format(7)
        user_color = fgnescape.format(6)
        pass_color = fgnescape.format(9)
        txtreset = '\x1b[0m'

    if batch:
        if ('acname' in keys):
            print(raccount.name)
        for (k, v) in raccount.fields.items():
            if k in keys:
                print(v)

    else:
        if ('user' in keys) and ('user' in raccount.fields):
            print("{0}{1} - {2}{3}".format(ac_color, raccount.name, user_color, raccount.fields['user']))
        else: print("{0}{1}".format(ac_color, raccount.name))

        if ('pass' in keys) and ('pass' in raccount.fields):
            print("\t{0}{1}".format(pass_color, raccount.fields['pass']))

        print(txtreset, end='')

        if ('user' in keys): keys.remove('user')
        if ('pass' in keys): keys.remove('pass')

        if len(keys) > 0:
            for (k, v) in raccount.fields.items():
                if (k not in ['user', 'pass']) and (k in keys):
                    print("\t{0}: {1}".format(k, v))
                elif pfull:
                    for (k, v) in raccount.fields.items():
                        if k not in ['user', 'pass']:
                            print("\t{0}: {1}".format(k, v))

def CreateEntry(acname = None):
    from .rpass import rpass_account
    raccount = rpass_account()

    if not(acname): acname = input("Account name: ")

    raccount.name = acname

    usr = input("{0}: User - leave blank to remove field: ".format(acname))

    from getpass import getpass as gp
    pwrd = gp("{0}: Password - leave blank to remove field (typed letters do not appear): ".format(acname))

    if usr.strip():
        raccount.fields['user'] = usr
    if pwrd.strip():
        raccount.fields['pass'] = pwrd

    response = input("Would you like to add additional fields to the entry? [N/y] ")
    if response != '' and response.lower()[0] == 'y':
        print("Please type field and hit enter - blank field cancels.")
        field = input("{0}: Field: ".format(acname))
        while(field):
            if field in ["username", "u"]: field = "user"
            if field in ["password", "p", "pass"]:
                from getpass import getpass as gp
                field = "pass"
                raccount.fields[field] = gp("{0}: ".format(field))
            else:
                raccount.fields[field] = input("{0}: ".format(field))
            field = input("{0}: Field: ".format(acname))
    return raccount

def GetOptions():
    """Gets options from user through configuration file and commandline."""
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-b", "--batch", dest="batch_mode",
            action="store_true", default=False,
            help="Option to print in batch mode: no colors, no copying, no field labels, no formatting.")

    parser.add_option("-u", "--users", dest="print_users",
            action="store_true", default=False,
            help="Add users to printed fields.")

    parser.add_option("-p", "--passwords", dest="print_pass",
            action="store_true", default=False,
            help="Add passwords to printed fields.")

    parser.add_option("-n", "--no-copy", dest="no_xclip",
            action="count", default = 0,
            help="Don't copy alphabetically first matching password to clipboard.")

    parser.add_option("--copy", dest="xclip",
            action="count", default = 0,
            help="Copy alphabetically first matching password to clipboard [default].")

    parser.add_option("-l", "--login", dest="login",
            action="store_true", default=False,
            help="Just login, don't show anything.")

    parser.add_option("-a", "--add-entry", dest="new_entry",
            action="store_true", default=False,
            help = "Add account(s). Optionally list new account names on the commandline.")

    parser.add_option("-d", "--delete-entry", dest="delete_entry",
            action = "store_true", default=False,
            help = "Specify account(s) to delete on commandline. Must match exactly.")

    parser.add_option("-k", "--keys", dest="print_keys",
            action = "store", type = "string",
            help = "Specify, in a comma-separated list (no spaces), which fields to print: i.e., custom1,custom2.\nUse --users and --passwords for non-custom fields.")

    parser.add_option('-f', '--password-file', dest = 'pass_file',
            action = 'store', type = 'string',
            help = "Specify a password file other than the default [~/.rpasswords].")

    parser.add_option("-C", "--config-file", dest="conf_file",
            action = "store", type = "string",
            help = "Specify a configuration file other than the default [~/.rpass.conf].")

    parser.add_option("-c", "--color", dest='color',
            action = "count", default = 0,
            help = "Enable color printing.")

    parser.add_option('--no-color', dest='no_color',
            action = "count", default = 0,
            help = "Disable color printing [default].")

    parser.add_option('-F', '--forgetcipher', dest='forget_cipher',
                      action='store_true', default=False,
                      help='Causes daemon to forget cipher, asking to retype password.')

    parser.add_option('-P', '--change-passphrase', dest='change_pass',
                      action='store_true', default=False,
                      help='Changes passphrase for current password file.')

    (options, args) = parser.parse_args()

    fops = {}
    if options.conf_file: fops['conf_file'] = options.conf_file
    else: fops['conf_file'] = '~/.rpass.conf'
    fops['batch'] = options.batch_mode
    if options.xclip > 0: fops['copy'] = True
    if options.no_xclip > 0: fops['copy'] = False
    if 'copy' not in fops: fops['copy'] = True
    fops['login'] = options.login
    fops['new_entry'] = options.new_entry
    fops['del_entry'] = options.delete_entry
    if options.color > 0: fops['color'] = True
    if options.no_color > 0: fops['color'] = False

    if options.print_keys == None: fops['fields'] = []
    elif options.print_keys.strip() == "": fops['fields'] = [None]
    else: fops['fields'] = [f.strip() for f in options.print_keys.split(',') if f.strip()]
    if options.print_users: fops['fields'].append('user')
    if options.print_pass: fops['fields'].extend(["pass"])

    if options.pass_file:
        from os.path import expanduser
        fops['passfile'] = expanduser(options.pass_file)
    if 'passfile' not in fops: fops['passfile'] = None

    fops['forget_cipher'] = options.forget_cipher;
    fops['change_pass'] = options.change_pass;

    return (fops, args)

def run():
    from .rpass import rpass_password_manager
    from os.path import isfile

    (options, args) = GetOptions()

    account = rpass_password_manager(conf_file = options['conf_file'], passfile = options['passfile'])

    if 'color' not in options:
        if 'color' in account.options:
            options['color'] = account.options['color']
        else: options['color'] = False

    if not(options['fields']):
        if 'fields' in account.options:
            options['fields'] = account.options['fields']
        else: options['fields'] = []

    if options['fields'] == [None]: options['fields'] = []

    if not(isfile(account.passfile)):
        response = input("No password file at {0} found. Would you like to create it (note: please don't create this file manually)? [Y/n] ".format(account.passfile))

        if response != '' and response.lower()[0] == 'n':
            print("No password file created...Exiting.")
            exit()
        else:
            f = open(account.passfile, 'w')
            f.close()

        if options['new_entry'] and len(args) > 0:
            for arg in args: account.AddEntry(CreateEntry(arg))
        else: account.AddEntry(CreateEntry())

        exit()

    if options['new_entry']:
        if len(args) > 0:
            for arg in args: account.AddEntry(CreateEntry(arg))
        else: account.AddEntry(CreateEntry())
        exit()

    elif options['del_entry']:
        if len(args) > 0:
            for arg in args: account.DeleteEntry(sstring = arg)
        else: print ("Please specify entry or entries to delete.")
        exit()

    elif options['change_pass']:
        account.ChangePass()
        exit()

    elif options['forget_cipher']:
        account.ForgetCipher()
        exit()

    else:
        aclist = []
        pfull = False

        if len(args) > 0:
            pfull = True
            for arg in args:
                flags = 0
                if (not(options['batch'])):
                    flags = rpass_password_manager.REGEX|rpass_password_manager.CASE_INSENSITIVE
                aclist.extend(account.GetAccounts(sstring = arg, flags = flags))
            # Copy passwords...
            if not(options['batch']) and options['copy']:
                try:
                    for ac in aclist:
                        if (account.CopyPass(ac)): break
                except OSError:
                    print("'xclip' not found. Please install xclip to automatically copy first matched password to clipboard (avoid printing passwords).")
                    print("To see passwords, run rpass with the --passwords option.\n")
        else:
            aclist = account.GetAccounts(sstring = '', flags = rpass_password_manager.ALL_ACCOUNTS)

        for ac in aclist:
            PrintAccountInfo(raccount=ac, pfull = pfull, color = options['color'], keys = options['fields'], batch = options['batch'])
