"""Bounded execution for locally written Python solutions.

This catches accidental infinite loops and excessive output. It is not a
security sandbox: arbitrary user code still runs with the user's permissions.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import time


@dataclass(frozen=True)
class ExecutionResult:
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    timed_out: bool = False
    too_much_output: bool = False


def execute_python(command: list[str], stdin: str = "", *,
                   timeout: float = 3.0, max_output_bytes: int = 131072,
                   cwd: str | Path | None = None) -> ExecutionResult:
    """Run a child process with time and captured-output limits."""
    if timeout <= 0 or max_output_bytes < 1024:
        raise ValueError("Invalid execution limits")
    if len(stdin.encode("utf-8")) > 65536:
        raise ValueError("Input is too long")

    with tempfile.TemporaryDirectory(prefix="coderise_io_") as directory:
        out_path = Path(directory) / "stdout.txt"
        err_path = Path(directory) / "stderr.txt"
        with out_path.open("wb", buffering=0) as out, err_path.open("wb", buffering=0) as err:
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                cwd=cwd, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            started = time.monotonic()
            first = True
            timed_out = False
            too_much_output = False
            try:
                while True:
                    remaining = timeout - (time.monotonic() - started)
                    if remaining <= 0:
                        timed_out = True
                        break
                    try:
                        if first:
                            process.communicate(
                                input=stdin.encode("utf-8"), timeout=min(0.1, remaining)
                            )
                            first = False
                        else:
                            process.communicate(timeout=min(0.1, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        first = False
                        if out_path.stat().st_size + err_path.stat().st_size > max_output_bytes:
                            too_much_output = True
                            break
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate()

        with out_path.open("rb") as stdout_file:
            stdout = stdout_file.read(max_output_bytes).decode("utf-8", errors="replace")
        with err_path.open("rb") as stderr_file:
            stderr = stderr_file.read(max_output_bytes).decode("utf-8", errors="replace")
        if out_path.stat().st_size + err_path.stat().st_size > max_output_bytes:
            too_much_output = True
        return ExecutionResult(
            stdout=stdout, stderr=stderr, returncode=process.returncode,
            timed_out=timed_out, too_much_output=too_much_output,
        )
