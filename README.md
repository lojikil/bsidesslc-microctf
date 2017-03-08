# overview

a tiny, 1-hour CTF written in sleep-dep mode on the plane. Let's make hacking great again.

## BSides SLC mods

[Seth](https://github.com/sethlaw) asked for some help for a BSides SLC version. so here we go

# levels:

Mission: You mission is to win

## level 0

Challenge: Location is hard, without it you won't get very far.

Brainfuck is mixed into an clue, but one digit is off

KEY: IP given in clue (must use brainfuck to decode).

## level 1

Challenge: Names are the thing. Hosts to be found.

the host is up, but you need to have a name associated with it; name is revealed in source.

KEY: slc.punk

## level 2

Challenge: Can you access the system?

create a login (no actual vuln), but people will waste time I'm sure.

KEY: AccessRequestedAccessGranted (in html source)

## level 3

Challenge: Find the key! <picture of a fluffy bunny>

SysOp's API system, run's Kudritza code; Kudritza code has a special mode to dump all UUIDs

KEY: ZGZ4AmAuBJDmLJZlATZ0L2RlZwOwZQD1ZmHmMQH2AJD=

## level 4

IDOR key system

Challenge: What's the admin password?

UUID validator, but there's something wrong with your UUID...

(it's ROT13(base64(uuid)))

KEY: 41b28e17133a45088c8c5781ecb6204d

## level 5

Challenge text: It's time for admin win. Access the admin section.

Use key from key system to access "/win", force browse to the same URL for the key

KEY: IamtheBSidesSLCWINRAR
