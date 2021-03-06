#!/usr/bin/env bash

set -ex

# Create the debian/ directory for building the osql-cli Debian package

# This script takes an argument of the empty directory where the files will be placed.

if [ -z "$1" ]
  then
    echo "No argument supplied for debian directory."
    exit 1
fi

if [ -z "$2" ]
  then
    echo "No argument supplied for source directory."
    exit 1
fi

if [ -z "$3" ]
  then
    echo "No argument supplied for cli version."
    exit 1
fi

TAB=$'\t'

debian_dir=$1
source_dir=$2
cli_version=$3
mkdir $debian_dir/source

echo '1.0' > $debian_dir/source/format
echo '9' > $debian_dir/compat

cat > $debian_dir/changelog <<- EOM
osql-cli ($cli_version-${CLI_VERSION_REVISION:=1}) unstable; urgency=low

  * Debian package release.

 -- Microsft SQL Server CLI Team <sqlcli@microsoft.com>  $(date -R)

EOM

cat > $debian_dir/control <<- EOM
Source: osql-cli
Section: python
Priority: extra
Maintainer: Microsoft SQL Server CLI Team <sqlcli@microsoft.com>
Build-Depends: debhelper (>= 9), libssl-dev, libffi-dev, python3-dev
Standards-Version: 3.9.5
Homepage: https://github.com/dbcli/osql-cli

Package: osql-cli
Architecture: all
Depends: libunwind8, libicu52 | libicu55 | libicu57
Description: osql-cli
    We’re excited to introduce osql-cli, a new and interactive command line query tool for SQL Server.
    This open source tool works cross-platform and proud to be a part of the dbcli.org community.
EOM

cat > $debian_dir/copyright <<- EOM
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: osql-cli
Upstream-Contact: Microsoft SQL Server CLI Team <sqlcli@microsoft.com>
Source: https://github.com/dbcli/osql-cli

Files: *
License: BSD-3
EOM

cat > $debian_dir/rules << EOM
#!/usr/bin/make -f

# Uncomment this to turn on verbose mode.
#export DH_VERBOSE=1
#export DH_OPTIONS=-v

%:
${TAB}dh \$@ --sourcedirectory $source_dir

override_dh_auto_build:
override_dh_auto_install:
override_dh_install:
${TAB}mkdir -p debian/osql-cli/osql-cli
${TAB}cp -a python_env/* debian/osql-cli/osql-cli
${TAB}mkdir -p debian/osql-cli/usr/bin/
${TAB}echo "if [ -z ${PYTHONIOENCODING+x} ]; then export PYTHONIOENCODING=utf8; fi" > debian/osql-cli/usr/bin/osql-cli
${TAB}echo "\043!/usr/bin/env bash\n/osql-cli/bin/python3 -Im osqlcli.main \"\044\100\"" > debian/osql-cli/usr/bin/osql-cli
${TAB}chmod 0755 debian/osql-cli/usr/bin/osql-cli

override_dh_strip:
${TAB}dh_strip --exclude=_cffi_backend

EOM

cat $debian_dir/rules

# debian/rules should be executable
chmod 0755 $debian_dir/rules
