#!/usr/bin/env python3
import re
import sys
import subprocess

class REMatcher(object):
    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self,regexp):
        self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self,i):
        return self.rematch.group(i)


def get_texcount_output(dir, file):
    res = subprocess.run(['texcount', '-freq', '-merge', '-stat', '-dir=' + dir, file], stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8')


def parse_preamble(preamble):
    print('### Overall statistics')
    print('|   | Count |')
    print('| - | ----- |')

    for line in preamble.splitlines()[2:]:
        parts = line.split(": ")
        print('| ' + parts[0] + ' | ' + parts[1] + ' |')

    print('\n')


def parse_headers(headers):
    indent_unit = "&nbsp;&nbsp;&nbsp;&nbsp;"
    r = re.compile('  (\\d+)\\+\\d+\\+\\d+ \\(\\d+/(\\d+)/(\\d+)/(\\d+)\\) (\\w+): (.*)', re.DOTALL)
    print('### Statistics grouped by header')
    print("| Header | Word count | Floats | Math (inline) | Math (displayed) |")
    print("| - | - | - | - | - |")
    for line in headers.splitlines():
        header_indent = ""
        m = REMatcher(line)
        if m.match(r):
            word_count = m.group(1)
            float_count = m.group(2)
            inline_math = m.group(3)
            displayed_math = m.group(4)
            header_type = m.group(5)
            header_title = m.group(6)

            if header_type == "Chapter":
                header_indent = indent_unit
            elif header_type == "Section":
                header_indent = indent_unit * 2
            elif header_type == "Subsection":
                header_indent = indent_unit * 3

            print('| ' + header_indent + header_title + ' | ' + word_count + ' | ' + float_count + ' | ' + inline_math + ' | ' + displayed_math + ' |')
    print('\n')


def parse_word_frequency(word_frequency):
    print('### Top 10 words')
    print('|   | Count |')
    print('| - | ----- |')
    for word in word_frequency.splitlines()[:10]:
        parts = word.split(": ")
        print('| ' + parts[0] + ' | ' + parts[1] + '|')

    print('\n')


def process_texcount_output(output):
    m = REMatcher(output)
    r = re.compile('(.*)Subcounts:\\n  text\\+headers\\+captions \\(#headers\\/#floats\\/#inlines\\/#displayed\\)\\n(.*)\\nWord: Freq\\n---\\n(.*)\\n---\\n(.*)\\nSum of subset:', re.DOTALL)
    if m.match(r):
        # Group 1: Preamble (Overall stats, Encoding)
        # Group 2: Headers and their individual stats
        # Group 3: Word statistics
        # Group 4: Word frequency table
        parse_preamble(m.group(1))
        parse_headers(m.group(2))
        # parse_word_stats(m.group(3))
        parse_word_frequency(m.group(4))


process_texcount_output(get_texcount_output(sys.argv[1], sys.argv[2]))
