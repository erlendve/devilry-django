#!/usr/bin/env python

from optparse import OptionParser
import logging

from common import (setup_logging,
    add_quiet_opt, add_settings_option, set_django_settings_module)




p = OptionParser(
        usage = "%prog <add|modify|addormodify|info> " \
                    "[options] <username>",
        description = "*add* and *modify* takes the documented options, "\
            "while *info* only takes a username.")
add_settings_option(p)
p.add_option("--first-name", dest="first_name", default=None,
        help="First name", metavar="FIRSTNAME")
p.add_option("--last-name", dest="last_name", default=None,
        help="Last name", metavar="LASTNAME")
p.add_option("--email", dest="email", default=None,
        help="Email address", metavar="EMAIL")
p.add_option("--superuser", dest="superuser", default=None,
        metavar = 'yes/no',
        help="Make the user a superuser. A superuser has access to " \
            "everything in the system. With *add* this defaults to " \
            "'no', and with *modify* this defaults to no change made.")
p.add_option("--active", dest="active", default=None,
        metavar = 'yes/no',
        help="Activate or deactivate a user. With *add* this defaults to " \
            "'yes', and with *modify* this defaults to no change made.")
add_quiet_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)
set_django_settings_module(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
from django.contrib.auth.models import User

if len(args) != 2:
    p.print_help()
    raise SystemExit()

action = args[0]
username = args[1]

kw = {}
for x in 'first_name', 'last_name', 'email':
    value = getattr(opt, x)
    if value:
        kw[x] = value

if opt.superuser != None:
    kw['is_superuser'] = opt.superuser == 'yes'
    kw['is_staff'] = kw['is_superuser']
if opt.active != None:
    kw['is_active'] = opt.active == 'yes'

if not action in ('info', 'add', 'modify', 'addormodify'):
    raise SystemExit("Invalid action: %s" % action)

if action == "addormodify":
    if User.objects.filter(username=username).count() == 0:
        action = "add"
    else:
        action = "modify"

if action == "info":
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist, e:
        logging.error("User '%s' does not exist." % username)
    else:
        for key, label in (
                ('username', 'Username'),
                ('first_name', 'First name'),
                ('last_name', 'Last name'),
                ('email', 'Email'),
                ('is_active', 'Is active'),
                ('is_staff', 'Has access to superadmin interface'),
                ('is_superuser', 'Is superuser')):
            logging.info('%s: %s' % (label, getattr(u, key)))

elif action == "modify":
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        logging.error('User "%s" does not exist.' % username)
        raise SystemExit()
    for key, value in kw.iteritems():
        setattr(u, key, value)
    u.save()
    logging.info('User "%s" modified successfully.' % username)

elif action == "add":
    if User.objects.filter(username=username).count() == 0:
        u = User(
                username = username,
                **kw)
        u.save()
        logging.info('User "%s" created successfully.' % username)
    else:
        logging.error('User "%s" already exists.' % username)
        raise SystemExit()
