# Template package that stores native sql tools service binaries during wheel compilation.
# Files will be dynamically created here and cleaned up after each run.

import os
import platform


def get_executable_path():
    """
        Find osqltoolsservice executable relative to this package.
    """
    # Debug mode.
    if 'MSSQLTOOLSSERVICE_PATH' in os.environ:
        osqltoolsservice_base_path = os.environ['MSSQLTOOLSSERVICE_PATH']
    else:
        # Retrieve path to program relative to this package.
        osqltoolsservice_base_path = os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                '..',
                'bin'))

    # Format name based on platform.
    osqltoolsservice_name = u'MicrosoftSqlToolsServiceLayer{}'.format(
        u'.exe' if (platform.system() == u'Windows') else u'')

    osqltoolsservice_full_path = os.path.abspath(os.path.join(osqltoolsservice_base_path, osqltoolsservice_name))

    if not os.path.exists(osqltoolsservice_full_path):
        error_message = '{} does not exist. Please re-install the osql-cli package'.format(osqltoolsservice_full_path)
        raise EnvironmentError(error_message)

    return osqltoolsservice_full_path
