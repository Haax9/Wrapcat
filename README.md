# Wrapcat

## :speech_balloon: Description

Wrapcat is a small and dirty hashcat Python wrapper.
The main idea behind this script is to run several hashcat commands you would run manually when trying to crack hashes. It does not uses pure bruteforce (well, a litte bit) that would takes ages but focuses on wordlits, rules and charsets.
I originally made it for myself but thought it could help people.

3 running modes depending on your power and available time (see benchmark section) : 
- Default (faster)
- Extended 
- Full (can be VERY long)

The script has been originally developped for NTLM cracking, using my own hardware for cracking reference (time) and in order to not exceed several hours, even for the full mode. However, it can be used for many other hash formats (I used it for MD5, SHA-1...) but in that case, it would take more time.

The code is probably dirty and could be optimized, feel free to use and modify it with your own commands.

<br/>

## :memo: Install & Configuration

This tool was initially developped for Python3.
Nothing fancy here, it uses the following modules :

```python
import os
import subprocess
import time
import argparse, textwrap
from pathlib import *
```

You can directly install them using `pip`.
<br/>

It is then necessary to configure all the paths for your hashcat, wordlists, rules and charsets.

I currently use popular wordlists (Rockyou, Kaonashi) as well as personal wordlists. So, feel free to update the code to your needs (Well, you'll have to because I don't provide them).

Following rules are also used : 
- best64.rule (default hashcat embedded)
- leetpspeak.rule (default hashcat embedded)
- OneRuleToRuleThemAll.rule (https://notsosecure.com/one-rule-to-rule-them-all/)
- Kaonashi rules (https://github.com/kaonashi-passwords/Kaonashi)

Finally I use three custom charsets, mainly to avoid using `?a` :

- custom_alpha_special.chr
```
abcdefghijklmnopqrstuvwxyzABCEDFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;=@?_
```

- custom_special_digit_char.chr
```
0123456789!"#$%&'()*+,-./:;=@?_
```

- custom_special_char.chr
```
?!%$&# -_@+=*
```
<br/>

## :book: Usage

```
$ python wrapcat.py --help
usage: wrapcat.py [-h] -m HASHTYPE -f HASHFILE -p POTFILE [--extended] [--full] [--show] [--show-user] [--find FIND]
                  [--save] [--just-save] [--skip]

Hashcat mini-wrap v1.0 - Hashcat Wrapper for cracking large files

optional arguments:
  -h, --help            show this help message and exit
  -m HASHTYPE, --hashtype HASHTYPE
                        The hash type to crack. See hashcat documentation
                        for reference (NTLM : 1000)
  -f HASHFILE, --hashfile HASHFILE
                        The path of the hash file to crack
  -p POTFILE, --potfile POTFILE
                        The path of the potfile.
                        Can be an existing one or not
  --extended            Extended tests
                        Go for additionnal attacks on top of the default ones
                        Check the source code for details
  --full                Maximum power !
                        Go for additionnal attacks on top of the default ones
                        Check the source code for details
  --show                Show cracked hashes for the given potfile
  --show-user           Show cracked hashes and users for the given potfile
  --find FIND           Search for a given string in cracked users or hashes
  --save                After having run all attacks, save the current potfile passwords
                        into the global password list in a sorted and unique way
  --just-save           Only save the current potfile passwords into the global wordlist
                        No cracking commands
  --skip                In full mode, skip previous tests
```
<br/>

## :computer: Examples

Default and minimal commands. Intented to do basic cracking and to be quite fast.

```bash
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt
```

Extended/Full commands.
Check the code for executed hashcat commands.

```bash
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --extended
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --full
```

Show cracked hashs.
You can also use the `--show-user` (same as hashcat) but its currently only working with NTLM formated hashes (domain.com\user:rid:hash).

```bash
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --show
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --show-user
```

Search for a specific string. It currently uses the `--show --user` hashcat option so it also only works with NTLM hashes (see format below).

```bash
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --find "adminlol"
```

This option can be used to save cracked hashes into a personal wordlist.
It can be usefull when cracking lots of hashes to have a unique wordlist.

```bash
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --save
```

The `just-save` option will only take the given pot file, parse it and save hashes to your personal wordlist.
No cracking here.

```bash
$ python wrapcat.py -m 1000 -f HASH_FILE.txt -p POT_FILE.txt --just-save
```
<br/>

## :hourglass: Benchmarks

This section could be updated later.
For the moment, here is a small NTLM benchmark.

Hardware used : RTX 2070 Super

Cracking 2150 NTLM Hashes :

- Default mode (\~3min30)
```bash
[-] Phase 1 (Wordlist / Simple masks) - 59.61 sec
[-] Phase 2 (Wordlist + Rules) - 279.53 sec
[-] Phase 3 (Wordlist + Masks) - 306.44 sec
[-] Phase X (Wordlist + Cracked) - 332.31 sec

[+] Total execution time : 334.50 sec
```

- Extended mode (\~35min)
```bash
[-] Phase 1 (Wordlist / Simple masks) - 61.26 sec
[-] Phase 2 (Wordlist + Rules) - 291.57 sec
[-] Phase 3 (Wordlist + Masks) - 318.62 sec
[-] Phase 4 (EXTENDED MODE) - 2024.03 sec
[-] Phase X (Wordlist + Cracked) - 2052.72 sec

[+] Total execution time : 2055.02 sec
```

- Full mode (\~1h55)
```bash
[-] Phase 1 (Wordlist / Simple masks) - 68.05 sec
[-] Phase 2 (Wordlist + Rules) - 291.04 sec
[-] Phase 3 (Wordlist + Masks) - 314.79 sec
[-] Phase 4 (EXTENDED MODE) - 1983.49 sec
[-] Phase 5 (FULL MODE) - 6989.67 sec
[-] Phase X (Wordlist + Cracked) - 7017.81 sec

[+] Total execution time : 7019.91 sec
```
<br/>

### Extra tip

If you're not afraid by getting rickrolled, I heard that listening this song while cracking hashes produces better results ¯\\\_(ツ)\_/¯ (thanks to <a href="https://twitter.com/h_nu11" target="_blank" rel="noopener">h_null1</a>)

https://www.youtube.com/watch?app=desktop&v=BjfbS_Kj-J0