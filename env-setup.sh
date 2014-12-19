#!/bin/bash
# Set environment to allow running without installation.
# Usage: source ./env-setup.sh

export PYTHONPATH=$(readlink -e $(pwd))
export PATH=$PATH:$(readlink -e $(pwd))

# vim: set ts=4 sts=4 sw=4 noet:
