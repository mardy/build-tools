#!/usr/bin/python3

# Copyright (C) 2017 Marius Gripsgard <marius@ubports.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests, os, sys

DEB_SOURCE_TEMPLATE = "deb http://repo.ubports.com/ %s main"

def repo_exist(repo):
    r = requests.get("http://repo.ubports.com/dists/%s/Release" % repo)
    return r.status_code == 200

def get_branch():
    if not os.path.isfile("branch.buildinfo"):
        print("ERROR: branch.buildinfo does not exist!")
        sys.exit(1)
        return;
    with open("branch.buildinfo") as f:
        branch = f.read()
    return branch.strip()

def ubports_depends_exist():
    return os.path.isfile("ubports.depends")

def get_ubports_depends():
    if not ubports_depends_exist():
        return;
    with open("ubports.depends") as f:
        depend = f.readlines()

    # Overflow check
    if len(depend) > 20:
        print("ERROR: depend overflow size %s" % len(depend))
        return;

    depend = [x.strip() for x in depend]
    return depend

def is_extension(branch):
    return "_-_" in branch

def extension_get_base_repo(branch):
    if not is_extension(branch):
        return;
    return branch.split("_-_")[0]

depends_list = []

branch = get_branch()

# Working repo
if repo_exist(branch):
    depends_list.append(branch)
else:
    print("WARNING: branch repo '%s' does not exist, please ignore if this is a new branch" % branch)

# Extension repo
if is_extension(branch):
    base_extension = extension_get_base_repo(branch)
    if repo_exist(base_extension):
        depends_list.append(base_extension)
    else:
        print("ERROR: Extension repo '%s' do not exist" % base_extension)
        sys.exit(1)

# Depends file
if ubports_depends_exist():
    depends_file = get_ubports_depends()
    if not depends_file:
        print("ERROR: get_ubports_depends failed")
        sys.exit(1)
    for _depend in depends_file:
        if repo_exist(_depend):
            depends_list.append(_depend)
        else:
            print("ERROR: ubports.depends repo '%s' do not exist" % _depend)
            sys.exit(1)

deb_sources_list = []
for _depend in depends_list:
    deb_sources_list.append(DEB_SOURCE_TEMPLATE % _depend)

deb_sources = ",".join(deb_sources_list)

with open("ubports.repos_extra", "w") as f:
    f.write(deb_sources)
