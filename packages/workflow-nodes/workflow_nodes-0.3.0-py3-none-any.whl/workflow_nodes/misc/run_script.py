# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import subprocess
import sys
from pathlib import Path

from xmlhelpy import argument
from xmlhelpy import option

from .main import misc


@misc.command(version="1.0.0")
@argument("arg0", description="Executable shell script", required=True)
@option(
    "arguments",
    char="a",
    description=(
        "Arguments to run the shell script with. Separate multiple arguments with "
        "spaces"
    ),
    required=False,
)
@option(
    "execute-in",
    char="e",
    description="Overrides the path where the script will be executed (CWD)",
    required=False,
)
@option(
    "interpreter",
    char="i",
    description="Use an interpreter command to run the script "
    '(for example: "bash -c")',
    required=False,
)
def run_script(arg0, arguments, execute_in, interpreter):
    """Run a shell script."""

    path = Path(arg0).expanduser()
    # Do not write to stdout to keep output intact for piping.
    print(f"Running script {path}...", file=sys.stderr)
    cmd = [str(path.absolute())]
    if arguments:
        cmd += arguments.split(" ")
    if interpreter:
        cmd = interpreter.split(" ") + cmd
    if execute_in:
        exec_dir = str(Path(execute_in).expanduser())
        subprocess.call(cmd, cwd=exec_dir)
    else:
        subprocess.call(cmd)
