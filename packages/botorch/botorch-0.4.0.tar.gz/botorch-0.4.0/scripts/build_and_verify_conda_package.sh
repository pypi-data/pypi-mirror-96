#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

cd .conda || exit

# Get version number (created dynamically via setuptools-scm)
BOTORCH_VERSION=$(python ../setup.py --version)
# Export env var (this is used in .conda/meta.yaml)
export BOTORCH_VERSION

# build package
cur_dir="$(pwd)"
build_dir="${cur_dir}/conda_build"
mkdir "${build_dir}"
conda build -c pytorch -c gpytorch --output-folder "${build_dir}" .

# name of package file (assuming first build)
path="${build_dir}/noarch/botorch-${BOTORCH_VERSION}-0.tar.bz2"

# verify that package installs correctly
conda install --offline "${path}"

# verify import works and version is correct
conda_version=$(python -c "import botorch; print(botorch.__version__)" | tail -n 1)
if [[ $conda_version != "$BOTORCH_VERSION" ]]; then
  echo "Incorrect version. Expected: ${BOTORCH_VERSION}, Actual: ${conda_version}"
  exit 1
fi

cd .. || exit
