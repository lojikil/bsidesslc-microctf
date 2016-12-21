# overview

a tiny, 1-hour CTF written in sleep-dep mode on the plane. Let's make hacking great again.

# levels:

Mission: find the nVisium member who is Santa

## level 0

Brainfuck is mixed into an email, but one digit is off

## level 1

the host is up, but you need to have a name associated with it; name is revealed in source.

## level 2

Santa's API system, run's Kudritza code; Kudritza code has a special mode to dump all UUIDs

## level 3

UUID validator, but there's something wrong with your UUID...

(it's ROT13(base64(uuid)))
