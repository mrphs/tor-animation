#!/usr/bin/env python
import argparse
import codecs
import datetime
import os
import sys
import re


def main():
    args = parse_options_and_args()
    load_file(args.in_file, args.start_earlier, args.last_longer,
              args.out_file)

def parse_options_and_args():
    parser = argparse.ArgumentParser(
             description='Validate format of a .srt file and rewrite '
                         'timestamps for recording voice-overs.')
    parser.add_argument('in_file', metavar='IN',
                        help='an .srt file containing subtitles')
    parser.add_argument('out_file', metavar='OUT',
                        help='path where .srt file should be written '
                             'with improved subtitle timings for '
                             'recording voice-overs')
    parser.add_argument('--start-earlier', type=float,
                        default='0.5', metavar='SEC',
                        help='start subtitles earlier in output file for '
                             'recording voice-overs (default: '
                             '%(default)s)')
    parser.add_argument('--last-longer', type=float,
                        default='2.0', metavar='SEC',
                        help='make subtitles last longer in output file '
                             'for recording voice-overs')
    args = parser.parse_args()
    return args

def load_file(in_file, start_earlier, last_longer, out_file):
    linenum = 0
    # 0: group number, 1: timing, 2: text line, 3: text line or newline
    expected_next_line = 0
    expected_group_number = 1
    with codecs.open(in_file, "r", "utf-8-sig") as f:
        with codecs.open(out_file, "w", "utf-8-sig") as out:
            for line in f:
                stripped_line = line.rstrip()
                linenum += 1
                if expected_next_line == 0:
                    match = re.search(r"(\d+)", stripped_line)
                    if not match:
                        print "Line {0:d} must contain a number.".format(
                              linenum)
                        sys.exit(1)
                    if int(stripped_line) != expected_group_number:
                        print "Expected group number {0:d}.".format(
                              expected_group_number)
                        sys.exit(1)
                    out.write(line)
                    expected_group_number += 1
                    expected_next_line = 1
                elif expected_next_line == 1:
                    match = re.search(r"^(\d{2}:\d{2}:\d{2},\d{3}) --> "
                                        "(\d{2}:\d{2}:\d{2},\d{3})$",
                                      stripped_line)
                    if not match:
                        print "Line {0:d} should contain timing " \
                              "information.".format(linenum)
                        sys.exit(1)
                    new_start = datetime.datetime.strptime(match.group(1),
                                '%H:%M:%S,%f') \
                                - datetime.timedelta(
                                  seconds=start_earlier)
                    new_end = datetime.datetime.strptime(match.group(2),
                              '%H:%M:%S,%f') \
                              + datetime.timedelta(seconds=last_longer)
                    out.write("{0:s} --> {1:s}\n".format(
                              new_start.strftime('%H:%M:%S,%f')[:-3],
                              new_end.strftime('%H:%M:%S,%f')[:-3]))
                    expected_next_line = 2
                elif stripped_line != '':
                    out.write(line)
                    expected_next_line = 3
                else:
                    out.write(line)
                    expected_next_line = 0

if '__main__' == __name__:
    main()

