RPM Packaging
================

Building the RPM package
------------------------

On a build machine (e.g. new CentOS 7 VM) run the following.

Install dependencies required to build:
Required for rpm build tools & required to build osql-cli.
```
sudo yum install -y gcc git rpm-build rpm-devel rpmlint make bash coreutils diffutils patch rpmdevtools python libffi-devel python-devel openssl-devel
```

Build example:
Note: use the full path to the repo path, not a relative path.
```
git clone https://github.com/dbcli/osql-cli
cd osql-cli
build_scripts/rpm/build.sh $(pwd)
```

Verification
------------

```
sudo rpm -i RPMS/*/osql-cli-0.10.0.dev-1.el7.x86_64.rpm
osql-cli --version
```

Check the file permissions of the package:  
```
rpmlint RPMS/*/osql-cli-0.10.0.dev-1.el7.x86_64.rpm
```

Check the file permissions of the package:  
```
rpm -qlvp RPMS/*/osql-cli-0.10.0.dev-1.el7.x86_64.rpm
```

To remove:  
```
sudo rpm -e osql-cli
```

Links
-----

https://fedoraproject.org/wiki/How_to_create_an_RPM_package

https://fedoraproject.org/wiki/Packaging:RPMMacros?rd=Packaging/RPMMacros
