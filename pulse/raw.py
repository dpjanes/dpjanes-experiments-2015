## read LIRC.conf files that are in RAW

import sys
import re
import pprint
import json

import pulse

begin_re = "begin +(.*)"
begin_rex = re.compile(begin_re)

end_re = "end +(.*)"
end_rex = re.compile(end_re)

name_re = "name +(.*)"
name_rex = re.compile(name_re)

pulses_re = "(\d+) +(\d+) +(\d+) +(\d+) +(\d+) +(\d+)"
pulses_rex = re.compile(pulses_re)

remoted = {}

def emit(remote_name, command_name, pulses):
    if not pulses:
        return

    ## print remote_name, command_name, pulses
    resultd = {
        "raw": pulses
    }

    pulse.trim(resultd["raw"])
    pulse.cluster(resultd["raw"])
    pulse.onoffs(resultd)
    pulse.bigrams(resultd)

    del resultd["raw"]
    resultd["remote"] = remote_name
    resultd["command"] = command_name

    remoted.setdefault(remote_name, []).append(resultd)

def load(fin):
    state = "expect-begin-remote"

    in_remote = False
    in_codes = False

    remote_name = None
    code_name = None
    command_name = None
    command_pulses = None

    for line in fin:
        end = None
        end_match = end_rex.search(line)
        if end_match:
            end = end_match.group(1)

        begin = None
        begin_match = begin_rex.search(line)
        if begin_match:
            begin = begin_match.group(1)

        name = None
        name_match = name_rex.search(line)
        if name_match:
            name = name_match.group(1)

        pulses = None
        pulses_match = pulses_rex.search(line)
        if pulses_match:
            pulses = [
                {
                    "command": "pulse",
                    "length": int(pulses_match.group(1)),
                },
                {
                    "command": "space",
                    "length": int(pulses_match.group(2)),
                },
                {
                    "command": "pulse",
                    "length": int(pulses_match.group(3)),
                },
                {
                    "command": "space",
                    "length": int(pulses_match.group(4)),
                },
                {
                    "command": "pulse",
                    "length": int(pulses_match.group(5)),
                },
                {
                    "command": "space",
                    "length": int(pulses_match.group(6)),
                },
            ]

        if state == "expect-begin-remote":
            if begin == "remote":
                state = "pre-codes"
        elif state == "pre-codes":
            if name:
                remote_name = name
            elif begin == "raw_codes":
                state = "in-codes"
        elif state == "in-codes":
            if name:
                emit(remote_name, command_name, command_pulses)
                command_name = name
                command_pulses = []
            elif pulses:
                command_pulses.extend(pulses)

        if end == "raw_codes":
            emit(remote_name, command_name, command_pulses)
            end = "pre-codes"
        elif end == "remote":
            end = "expect-begin-remote"


if __name__ == '__main__':
    if len(sys.argv) == 1:
        load(sys.stdin)
    else:
        for filename in sys.argv[1:]:
            load(open(filename))

    print json.dumps(remoted, indent=4, sort_keys=True)
