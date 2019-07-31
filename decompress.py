#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# INTERVALS
# 1st = 0
# 2nd minor = 1
# 2nd major = 2
# 3th minor = 3
# 3th major = 4
# 4th = 5
# --- = 6
# 5th = 7
# 6th minor = 8
# 6th major = 9
# 7th minor = 10
# 7th major = 11

# MAYOR SCALE
# 1st = 0
# 2nd major = 2
# 3th major = 4
# 4th = 5
# 5th = 7
# 6th major = 9
# 7th major = 11

# MINOR SCALE
# 1st = 0
# 2nd major = 2
# 3th minor = 3
# 4th = 5
# 5th = 7
# 6th minor = 8
# 7th minor = 10

import re
import random
from midiutil.MidiFile import MIDIFile


def make_tree(ls):
    tree = {}
    last = 0
    cp = list(ls)

    while cp:
        a = cp.pop(0)
        if not cp:
            last = last >> 1
        tree[last] = a
        last = (last + 1) << 1
    return tree


def make_duration_tree(ls):
    tree = {}
    last = 0

    cp = []
    # for x in (0.25, 0.5, 0.75, 1):
    for x in (0.5, 1):
        cp += [(a, x) for a in ls]

    while cp:
        a = cp.pop(0)
        if not cp:
            last = last >> 1
        tree[last] = a
        last = (last + 1) << 1
    return tree


def make_occurence_tree(s):
    import operator
    from collections import Counter
    tree = {}
    last = 0
    counter = Counter(re.sub(r'[\s\.,]', '', s))
    sc = list(sorted(counter.items(), key=operator.itemgetter(1)))
    while sc:
        a, b = sc.pop(0)
        if not sc:
            last = last >> 1
        tree[last] = a
        last = (last + 1) << 1
    return tree


def number_to_bin(string):
    string = re.sub(r'[\s\.,]', '', string)
    number = 0
    for ch in string:
        n = int(ch)
        bits = len(bin(n)) - 2
        number <<= bits
        number += n
        # print('-- ', n, bin(n), bits, number, bin(number))
    return number


def decode(tree, number):
    b = bin(number)[2:]
    s = ''
    while b:
        s += b[0]
        b = b[1:]
        n = int(s, 2)
        if n in tree:
            s = ''
            yield tree[n]


def decode_near(tree, number):
    b = bin(number)[2:]
    s = ''
    previous = 0
    while b:
        s += b[0]
        b = b[1:]
        n = int(s, 2)
        if n in tree:
            s = ''
            note = tree[n]
            # note = tree[n][0]
            options = (note, note - 12, note + 12)
            distances = {abs(o - previous): o for o in options}
            previous = distances[min(distances.keys())]
            yield previous
            # yield (previous, tree[n][1])


INTERVALS = (0, 7, 4, 9, 5, 2, 11)  # MAJOR
# INTERVALS = (0, 7, 3, 2, 5, 8, 10)  # MINOR
# INTERVALS = (0, 10, 1, 6, 5)  # HIRAJOUSI Sachs y Slonimsky

INTERVALS_TREE = make_tree(INTERVALS)
INTERVALS_DUR_TREE = make_duration_tree(INTERVALS)

PI = """
    3.14159265358979323846264338327950288419716939937510582097494459230781640
    6286208998628034825342117067982148086513282306647093844609550582231725359
    4081284811174502841027019385211055596446229489549303819644288109756659334
    4612847564823378678316527120190914564856692346034861045432664821339360726
    """

E = """
2.718281828459045235360287471352662497757247093699959574966967627724076630353
  547594571382178525166427427466391932003059921817413596629043572900334295260
  595630738132328627943490763233829880753195251019011573834187930702154089149
  934884167509244761460668082264800168477411853742345442437107539077744992069
  551702761838606261331384583000752044933826560297606737113200709328709127443
    """
ONE_SEVENTH = ".142857"

C_SCALE = {0: 'C', 2: 'D', 4: 'E', 5: 'F', 7: 'G', 9: 'A', 11: 'B'}


def new_midi_file():
    mf = MIDIFile(1)
    track = 0

    time = 0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, 150)
    return mf, track


def write_direct_midi(number, filename='output.mid'):
    mf, track = new_midi_file()
    channel = 0
    volume = 100
    base_pitch = 60  # C4 (middle C)
    time = 0
    duration = 0.5

    clean = re.sub(r'[\s\.,]', '', str(number))

    for x in clean:
        mf.addNote(track, channel, base_pitch + int(x), time, duration, volume)
        time += duration

    with open(filename, 'wb') as outf:
        mf.writeFile(outf)


def write_distributed_midi(tree, number, filename='output.mid'):
    notes = decode_near(tree, number)

    mf, track = new_midi_file()

    channel = 0
    volume = 100
    base_pitch = 60  # C4 (middle C)
    time = 0
    duration = 0.5

    # for (pitch, duration) in notes:
    for pitch in notes:
        # duration = random.choice((0.5, 1))
        mf.addNote(track, channel, base_pitch + pitch, time, duration, volume)
        time += duration

    with open(filename, 'wb') as outf:
        mf.writeFile(outf)


def write_multitrack_midi(tree, *numbers, filename='output.mid'):
    mf = MIDIFile(len(numbers))

    track = 0
    time = 0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, 140)

    track = 0
    for num in numbers:
        notes = decode_near(tree, num)

        channel = 0
        volume = 100
        # base_pitch = 48  # C3
        base_pitch = 60  # C4 (middle C)
        base_pitch += (track * 24)
        time = 0

        for pitch in notes:
            duration = random.choice((0.5, 1, 1.5))
            mf.addNote(
                track, channel, base_pitch + pitch, time, duration, volume)
            time += duration

        track += 1

    with open(filename, 'wb') as outf:
        mf.writeFile(outf)

# write_direct_midi(PI)
# write_distributed_midi(INTERVALS_TREE, number_to_bin(PI))
# write_distributed_midi(INTERVALS_TREE, number_to_bin(E))
# write_distributed_midi(INTERVALS_DUR_TREE, number_to_bin(PI))
write_multitrack_midi(INTERVALS_TREE, number_to_bin(PI), number_to_bin(E))
