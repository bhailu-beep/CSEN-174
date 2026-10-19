#!/bin/sh
set -u

COMPILE_TIMEOUT="${COMPILE_TIMEOUT:-10}"
RUN_TIMEOUT="${RUN_TIMEOUT:-2}"

export HOME="${HOME:-/tmp}"
export TMPDIR="${TMPDIR:-/tmp}"

if [ ! -f /src/main.cpp ]; then
    echo "No source file found." >&2
    exit 254
fi

timeout -k 1s "$COMPILE_TIMEOUT" g++ -std=c++17 -O0 -pipe -o /tmp/a.out /src/main.cpp
compile_status=$?

if [ "$compile_status" -eq 124 ] || [ "$compile_status" -eq 137 ]; then
    echo "Compilation timed out." >&2
    exit 253
fi

if [ "$compile_status" -ne 0 ]; then
    exit 254
fi

INPUT=/src/input.txt
if [ ! -f "$INPUT" ]; then
    INPUT=/dev/null
fi

timeout -k 1s "$RUN_TIMEOUT" /tmp/a.out < "$INPUT"
exit $?
