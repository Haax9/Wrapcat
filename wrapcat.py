#!/usr/bin/env python3
# coding: utf-8

import os
import subprocess
import time
import argparse, textwrap
from pathlib import *

# Directories
HASHCAT_DIR = Path("path/to/hashcat-6.1.1")
WORDLIST_DIR = Path("path/to/Passwords")

# Wordlists
L_ROCKYOU = WORDLIST_DIR / "path/to/rockyou.txt"
L_KAONASHI = WORDLIST_DIR / "path/to/kaonashi14M.txt"
L_KAONASHI_FULL = WORDLIST_DIR / "path/to/kaonashi.txt"
L_FRENCH = WORDLIST_DIR / "path/to/french.txt"
L_GLOBAL_REAL = Path("path/to/PERSONNAL.txt")
L_SMALL_ALL = WORDLIST_DIR / "all_uniq_small.txt"
L_CUSTOM_LEAKS = WORDLIST_DIR / "CUSTOM.txt"

# Rules
R_BEST64 =  HASHCAT_DIR / "rules/best64.rule"
R_LEET = HASHCAT_DIR / "rules/leetspeak.rule"
R_ONEALL = HASHCAT_DIR / "rules/OneRuleToRuleThemAll.rule"
R_KAO = HASHCAT_DIR / "rules/kaonashi_rules/*"

# Charsets
C_CUSTOM_ALL = HASHCAT_DIR / "charsets/custom_alpha_special.chr"
C_CUSTOM_SPECIAL = HASHCAT_DIR / "charsets/custom_special.chr"
C_CUSTOM_SPEDIGIT = HASHCAT_DIR / "charsets/custom_special_digit_char.chr"

PHASE_TIMER = dict()


def parse_arguments():
    desc = ('Wrapcat v1.0 - Hashcat Wrapper for cracking large files')
    parser = argparse.ArgumentParser(description=desc,formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-m', '--hashtype', type=str, action='store',
                        required=True, help=textwrap.dedent('''\
                        The hash type to crack. See hashcat documentation
                        for reference (NTLM : 1000)'''))
    parser.add_argument('-f', '--hashfile', type=str, action='store',
                        required=True,
                        help='The path of the hash file to crack')
    parser.add_argument('-p', '--potfile', type=str, action='store',
                        required=True, help=textwrap.dedent('''\
                        The path of the potfile.
                        Can be an existing one or not'''))
    parser.add_argument('--extended', action='store_true',
                        required=False, help=textwrap.dedent('''\
                        Extended tests
                        Go for additionnal attacks on top of the default ones
                        Check the source code for details'''))
    parser.add_argument('--full', action='store_true',
                        required=False, help=textwrap.dedent('''\
                        Maximum power !
                        Go for additionnal attacks on top of the default ones
                        Check the source code for details'''))
    parser.add_argument('--show', action='store_true',
                        required=False, help='Show cracked hashes for the given potfile')
    parser.add_argument('--show-user', action='store_true',
                        required=False, help='Show cracked hashes and users for the given potfile')
    parser.add_argument('--find', type=str, action='store',
                        required=False, help='Search for a given string in cracked users or hashes')
    parser.add_argument('--save', action='store_true',
                        required=False, help=textwrap.dedent('''\
                        After having run all attacks, save the current potfile passwords
                        into the global password list in a sorted and unique way'''))
    parser.add_argument('--just-save', action='store_true',
                        required=False, help=textwrap.dedent('''\
                        Only save the current potfile passwords into the global wordlist
                        No cracking commands'''))
    parser.add_argument('--skip', action='store_true',
                        required=False, help=textwrap.dedent('''\
                        In full mode, skip previous tests'''))

    args = parser.parse_args()

    return args


def show(HASH_TYPE, HASH_FILE, POT_FILE):
    cmd = "hashcat.exe -m {} {} --potfile-path {} --show".format(HASH_TYPE, HASH_FILE, POT_FILE)
    subprocess.run(cmd)


def showuser(HASH_TYPE, HASH_FILE, POT_FILE):
    cmd = "hashcat.exe -m {}  {} --potfile-path {} --show --user".format(HASH_TYPE, HASH_FILE, POT_FILE)
    subprocess.run(cmd)


def findString(HASH_TYPE, HASH_FILE, POT_FILE, SEARCH):
    cmd = "hashcat.exe -m {}  {} --potfile-path {} --show --user | findstr.exe -i \"{}\"".format(HASH_TYPE, HASH_FILE, POT_FILE, SEARCH)
    subprocess.run(cmd, shell=True)


def dict_attack(HASH_TYPE, HASH_FILE, POT_FILE, WORDLIST_FILE):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 0 {} -O".format(HASH_TYPE, HASH_FILE, POT_FILE, WORDLIST_FILE)
    subprocess.run(cmd)


def dict_rules_attack(HASH_TYPE, HASH_FILE, POT_FILE, WORDLIST_FILE, RULES_FILE):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 0 {} -r {} -O".format(HASH_TYPE, HASH_FILE, POT_FILE, WORDLIST_FILE, RULES_FILE)
    subprocess.run(cmd)


def dict_mask_attack(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, WORDLIST_FILE, MASK):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 6 -1 {} {} {} -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, WORDLIST_FILE, MASK)
    subprocess.run(cmd)


def dict_mask_incmaj_attack(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, WORDLIST_FILE, MASK):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 6 -1 {} {} {} --increment -j c -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, WORDLIST_FILE, MASK)
    subprocess.run(cmd)


def mask_dict_attack(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, MASK, WORDLIST_FILE):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 7 -1 {} {} {} -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, MASK, WORDLIST_FILE)
    subprocess.run(cmd)


def dict_random_rules_attack(HASH_TYPE, HASH_FILE, POT_FILE, WORDLIST_FILE, RULES_NUMBER):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 0 {} -g {} -O".format(HASH_TYPE, HASH_FILE, POT_FILE, WORDLIST_FILE, RULES_NUMBER)
    subprocess.run(cmd)


def pure_mask_attack(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, MASK):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 3 -1 {} {} -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, MASK)
    subprocess.run(cmd)


def pure_mask_attack_increment(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, MASK):
    cmd = "hashcat.exe -m {} {} --potfile-path {} -a 3 -1 {} {} --increment -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE, MASK)
    subprocess.run(cmd)

def admin_quick_win(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE):
	cmd = "hashcat.exe -m {} {} --potfile-path {} -a 3 \"admin?1?1?1?1\" -1 {} --increment -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE)
	subprocess.run(cmd)
	cmd = "hashcat.exe -m {} {} --potfile-path {} -a 3 \"Admin?1?1?1?1\" -1 {} --increment -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE)
	subprocess.run(cmd)
	cmd = "hashcat.exe -m {} {} --potfile-path {} -a 3 \"?1?1?1?1Admin\" -1 {} --increment -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE)
	subprocess.run(cmd)
	cmd = "hashcat.exe -m {} {} --potfile-path {} -a 3 \"?1?1?1?1admin\" -1 {} --increment -O".format(HASH_TYPE, HASH_FILE, POT_FILE, CHARSET_FILE)
	subprocess.run(cmd)

def get_pass_from_pot(POT_FILE):
    # Read the specified pot file
    with open(POT_FILE,'r', encoding='utf-8') as f:
        potfile = f.readlines()

    # Create and populate the password file
    # from the pot file
    pass_from_pot = POT_FILE + ".passonly.txt"
    with open(pass_from_pot,'w',encoding="utf-8") as passfile:
        for line in potfile:
            # Strip to get only passwords (no NTLM hashes)
            line = line.strip('\n')[33:]
            if not "$[HEX]" in line:
                p = line
            else:
                endhex = line.find("]")
                # Try to decode the HEX passwords
                try:
                    p = (bytes.fromhex(line[5:endhex]).decode("utf-8"))
                except:
                    p = (bytes.fromhex(line[5:endhex]).decode("cp1252"))
            passfile.write(p + '\n')
            #print(p)

    f.close()
    passfile.close()

    # Return the password file path
    return pass_from_pot


def save_to_global_wordlist(POT_FILE):
    cracked = get_pass_from_pot(POT_FILE)

    # Read pot file extracted passwords
    with open(cracked,'r') as c:
        passwords = c.read().split('\n')
    
    # Append the pot file passwords to the global wordlist
    with open(L_GLOBAL_REAL,'a') as g:
        for line in passwords:
            g.write(line + '\n')
    g.close()
    c.close()

    # Read the content of the global wordlist
    # Sort it and remove duplicates
    with open(L_GLOBAL_REAL,'r') as g:
        passFile = g.read().split('\n')
        passFile = list(filter(None,sorted(set(passFile))))
    g.close()

    # Override the global wordlist
    # With the new clean list
    with open(L_GLOBAL_REAL,'w') as g:
        for line in passFile:
            g.write(line + '\n')
    g.close()


def extended_tests(hashType,hashFile,potFile,start_time):
    # Pure bruteforce attacks
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?l?l?d?d ")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?l?l?l?d ")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?l?l?l?l?l?d?d ")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?l?l?l?l?l?l?d ")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?1"*7)

    # Large wordlists and big rules
    dict_rules_attack(hashType,hashFile,potFile,L_KAONASHI,R_KAO)
    dict_rules_attack(hashType,hashFile,potFile,L_FRENCH,R_KAO)

    # French + masks
    dict_mask_incmaj_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_FRENCH,"?1?1?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_FRENCH,"?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_FRENCH,"?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_FRENCH,"?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_FRENCH,"?1?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPEDIGIT,L_FRENCH,"?1?1?1?1?1")
    dict_mask_incmaj_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_SMALL_ALL,"?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_SMALL_ALL,"?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_SMALL_ALL,"?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_SMALL_ALL,"?1?1?1")
    PHASE_TIMER["Phase 4 (EXTENDED MODE)"] = time.time() - start_time


def full_tests(hashType,hashFile,potFile,start_time):
    # Apply random rules on wordlists
    dict_random_rules_attack(hashType,hashFile,potFile,L_ROCKYOU,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_ROCKYOU,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_KAONASHI,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_KAONASHI,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_GLOBAL_REAL,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_GLOBAL_REAL,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_CUSTOM_LEAKS,30000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_CUSTOM_LEAKS,30000)

    # Larger masks and custom charsets
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_KAONASHI,"?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_KAONASHI,"?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_KAONASHI,"?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_FRENCH,"?1?1?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_SMALL_ALL,"?1?1?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_CUSTOM_LEAKS,"?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_CUSTOM_LEAKS,"?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_CUSTOM_LEAKS,"?1?1?1")

    # Pure bruteforce using masks
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?1?1")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?1?1?1")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?1?1?1")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?l?l?1?1")
    pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?u?l?l?l?l?1?1?1")
    #pure_mask_attack(hashType,hashFile,potFile,C_CUSTOM_ALL,"?1"*8)

    # Long Kaonashi + Rules
    dict_rules_attack(hashType,hashFile,potFile,L_KAONASHI_FULL,R_KAO)
    PHASE_TIMER["Phase 5 (FULL MODE)"] = time.time() - start_time



def useAlreadyCracked(hashType,hashFile,potFile,start_time):
    # Reuse cracked hashs as wordlist + rules
    L_CRACKED = get_pass_from_pot(potFile)
    dict_rules_attack(hashType,hashFile,potFile,L_CRACKED,R_ONEALL)
    dict_random_rules_attack(hashType,hashFile,potFile,L_CRACKED,100000)
    dict_random_rules_attack(hashType,hashFile,potFile,L_CRACKED,100000)
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_CRACKED,"?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_CRACKED,"?1?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_CRACKED,"?1?1?1")
    mask_dict_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,"?1",L_CRACKED)
    mask_dict_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,"?1?1",L_CRACKED)
    mask_dict_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,"?1?1?1",L_CRACKED)
    PHASE_TIMER["Phase 4 (Wordlist+Cracked)"] = time.time() - start_time


def crack(args, start_time):
    hashType = args.hashtype
    hashFile = args.hashfile
    potFile = args.potfile

    # Skip classical and extended tests
    if args.full and args.skip:
        full_tests(hashType,hashFile,potFile,start_time)
        useAlreadyCracked(hashType,hashFile,potFile,start_time)
        return

    # Admin Quick Win
    admin_quick_win(hashType,hashFile,potFile,C_CUSTOM_ALL)

    # Only wordlists
    dict_attack(hashType,hashFile,potFile,L_ROCKYOU)
    dict_attack(hashType,hashFile,potFile,L_KAONASHI)
    dict_attack(hashType,hashFile,potFile,L_GLOBAL_REAL)
    dict_attack(hashType,hashFile,potFile,L_CUSTOM_LEAKS)

    # Quick pure bruteforce using masks
    pure_mask_attack_increment(hashType,hashFile,potFile,C_CUSTOM_ALL,"?1"*6)
    pure_mask_attack_increment(hashType,hashFile,potFile,C_CUSTOM_ALL,"?d"*10)
    PHASE_TIMER["Phase 1 (Wordlist / Simple masks)"] = time.time() - start_time

    # Wordlists + Rules
    dict_rules_attack(hashType,hashFile,potFile,L_ROCKYOU,R_BEST64)
    dict_rules_attack(hashType,hashFile,potFile,L_ROCKYOU,R_LEET)
    dict_rules_attack(hashType,hashFile,potFile,L_ROCKYOU,R_ONEALL)
    dict_rules_attack(hashType,hashFile,potFile,L_KAONASHI,R_BEST64)
    dict_rules_attack(hashType,hashFile,potFile,L_KAONASHI,R_LEET)
    dict_rules_attack(hashType,hashFile,potFile,L_KAONASHI,R_ONEALL)
    dict_rules_attack(hashType,hashFile,potFile,L_GLOBAL_REAL,R_BEST64)
    dict_rules_attack(hashType,hashFile,potFile,L_GLOBAL_REAL,R_LEET)
    dict_rules_attack(hashType,hashFile,potFile,L_GLOBAL_REAL,R_ONEALL)
    dict_rules_attack(hashType,hashFile,potFile,L_CUSTOM_LEAKS,R_BEST64)
    dict_rules_attack(hashType,hashFile,potFile,L_CUSTOM_LEAKS,R_LEET)
    dict_rules_attack(hashType,hashFile,potFile,L_CUSTOM_LEAKS,R_ONEALL)
    PHASE_TIMER["Phase 2 (Wordlist + Rules)"] = time.time() - start_time

    # Wordlist + small masks
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_KAONASHI,"?d?1")
    dict_mask_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,L_KAONASHI,"?d?d?1")
    mask_dict_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,"?d",L_KAONASHI)
    mask_dict_attack(hashType,hashFile,potFile,C_CUSTOM_SPECIAL,"?d?d",L_KAONASHI)
    PHASE_TIMER["Phase 3 (Wordlist + Masks)"] = time.time() - start_time

    # Check for the selected mode
    if args.extended:
        extended_tests(hashType,hashFile,potFile,start_time)
        useAlreadyCracked(hashType,hashFile,potFile,start_time)
    elif args.full:
        extended_tests(hashType,hashFile,potFile,start_time)
        full_tests(hashType,hashFile,potFile,start_time)
        useAlreadyCracked(hashType,hashFile,potFile,start_time)
    else:
        useAlreadyCracked(hashType,hashFile,potFile,start_time)

    # Check if need to save passwords
    if args.save:
        save_to_global_wordlist(args.potfile)


def main():
    """Main Function"""
    args = parse_arguments()

    # Move to the hascat dir
    os.chdir(HASHCAT_DIR)

    # Check for all optionnals arguments
    if args.find:
        findString(args.hashtype, args.hashfile, args.potfile, args.find)
        exit()

    if args.show_user:
        showuser(args.hashtype, args.hashfile, args.potfile)
        exit()

    if args.show:
        show(args.hashtype, args.hashfile, args.potfile)
        exit()

    if args.just_save:
        save_to_global_wordlist(args.potfile)
        exit()

    start_time = time.time()
    crack(args, start_time)

    # Create a passfile from the finished potfile
    L_CRACKED = get_pass_from_pot(args.potfile)
    dict_random_rules_attack(args.hashtype,args.hashfile,args.potfile,L_CRACKED,10000)
    get_pass_from_pot(args.potfile)

    print("\n\n[+] FINISHED !\n")
    for key, value in PHASE_TIMER.items():
        print("[-] {} - {:.2f} sec".format(key,value))

    print("\n[+] Total execution time : {:.2f} sec\n".format(time.time() - start_time))
    
if __name__ == "__main__":
    main()