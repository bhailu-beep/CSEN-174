"""Tunable limits for the C++ Docker sandbox."""

from pathlib import Path

IMAGE_NAME = "completec-cpp-sandbox"  # Docker image tag built from backend/sandbox
SANDBOX_DIR = Path(__file__).resolve().parent.parent / "sandbox"

# Distinct sandbox exit codes so Python can tell compile failure from a student program.
COMPILE_EXIT = 254  # g++ failed
COMPILE_TIMEOUT_EXIT = 253  # g++ exceeded COMPILE_TIMEOUT_SECONDS
GNU_TIMEOUT_EXIT = 124  # GNU timeout(1) when the student binary exceeds RUN_TIMEOUT

DEFAULT_RUN_TIMEOUT_SECONDS = 2.0  # Max seconds the compiled program may run
COMPILE_TIMEOUT_SECONDS = 10.0  # Max seconds allowed for g++
DOCKER_GRACE_SECONDS = 30.0  # Extra wall-clock time for container start/teardown
MEMORY_MB = 128  # Container memory limit
CPUS = "0.5"  # Fraction of a CPU the sandbox may use
PIDS_LIMIT = 32  # Max processes, to stop fork bombs
OUTPUT_CAP_BYTES = 64 * 1024  # Kill the run if stdout or stderr grows past this
MAX_SOURCE_BYTES = 256 * 1024  # Reject large code
TMPFS_SIZE = "32m"  # Writable /tmp for the compiler and binary (root FS is read-only)
SANDBOX_USER = "65534:65534"  # nobody:nogroup — never run student code as root
