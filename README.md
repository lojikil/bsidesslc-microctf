# overview

a tiny, 1-hour CTF written in sleep-dep mode on the plane. Let's make hacking great again.

## BSides SLC mods

[Seth](https://github.com/sethlaw) asked for some help for a BSides SLC version. so here we go

# levels:

Mission: get the sysop key

## level 0

Brainfuck is mixed into an email, but one digit is off

## level 1

the host is up, but you need to have a name associated with it; name is revealed in source.

## level 2

create a login (no actual vuln), but people will waste time I'm sure.

## level 3

SysOp's API system, run's Kudritza code; Kudritza code has a special mode to dump all UUIDs

## level 4

IDOR key system

UUID validator, but there's something wrong with your UUID...

(it's ROT13(base64(uuid)))

## level 5

use key from key system to access "admin panel"
