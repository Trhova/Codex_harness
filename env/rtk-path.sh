#!/usr/bin/env sh
RTK_PATH_SCRIPT=${BASH_SOURCE:-$0}
RTK_PATH_SCRIPT_DIR=$(CDPATH= cd "$(dirname "$RTK_PATH_SCRIPT")" && pwd)
export PATH="${RTK_PATH_SCRIPT_DIR}/../bin:$PATH"
