import errno
import shutil
import os
import platform
from os.path import expanduser, exists, dirname
from configobj import ConfigObj


def config_location():
    if platform.system() == 'Windows':
        return os.getenv('LOCALAPPDATA') + '\\dbcli\\osqlcli\\'
    elif 'XDG_CONFIG_HOME' in os.environ:
        return '%s/osqlcli/' % expanduser(os.environ['XDG_CONFIG_HOME'])
    else:
        return expanduser('~/.config/osqlcli/')


def load_config(usr_cfg, def_cfg=None):
    cfg = ConfigObj()
    cfg.merge(ConfigObj(def_cfg, interpolation=False))
    cfg.merge(ConfigObj(expanduser(usr_cfg), interpolation=False, encoding='utf-8'))
    cfg.filename = expanduser(usr_cfg)

    return cfg


def ensure_dir_exists(path):
    parent_dir = expanduser(dirname(path))
    try:
        os.makedirs(parent_dir)
    except OSError as exc:
        # ignore existing destination (py2 has no exist_ok arg to makedirs)
        if exc.errno != errno.EEXIST:
            raise


def write_default_config(source, destination, overwrite=False):
    destination = expanduser(destination)
    if not overwrite and exists(destination):
        return

    ensure_dir_exists(destination)

    shutil.copyfile(source, destination)


def upgrade_config(config, def_config):
    cfg = load_config(config, def_config)
    cfg.write()


def get_config(config_file=None):
    from osqlcli import __file__ as package_root
    package_root = os.path.dirname(package_root)

    config_file = config_file or '%sconfig' % config_location()

    default_config = os.path.join(package_root, 'osqlclirc')
    write_default_config(default_config, config_file)

    return load_config(config_file, default_config)


def get_casing_file(config):
    casing_file = config['main']['casing_file']
    if casing_file == 'default':
        casing_file = config_location() + 'casing'
    return casing_file
