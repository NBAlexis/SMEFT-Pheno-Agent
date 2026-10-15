#!/usr/bin/env python3
"""
Normalize an MG5 process name for use in folder/file names.

Replaces special characters per the skill convention:
  space → _, + → p, - → m, > → to, others removed

Usage:
    python normalize_process_name.py "e+ e- > a a"

Output:
    ep_em_to_a_a
"""
import sys


def normalize_process_name(process_name):
    """Normalize MG5 process name for folder/file naming.

    Rules:
        space ' ' → '_'
        '+'       → 'p'
        '-'       → 'm'
        '>'       → 'to'
        other special chars → removed

    Example:
        "e+ e- > a a" → "ep_em_to_a_a"
    """
    result = []
    for ch in process_name:
        if ch == ' ':
            result.append('_')
        elif ch == '+':
            result.append('p')
        elif ch == '-':
            result.append('m')
        elif ch == '>':
            result.append('to')
        elif ch.isalnum() or ch == '_':
            result.append(ch)
        # else: skip other special characters
    return ''.join(result)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} '<process_name>'", file=sys.stderr)
        sys.exit(1)

    process_name = sys.argv[1]
    normalized = normalize_process_name(process_name)
    print(normalized)


if __name__ == "__main__":
    main()
