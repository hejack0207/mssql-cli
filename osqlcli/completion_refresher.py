import logging
import threading
import osqlcli.decorators as decorators

from collections import OrderedDict
from .osqlcompleter import OsqlCompleter

logger = logging.getLogger(u'osqlcli.completion_refresher')


class CompletionRefresher(object):

    refreshers = OrderedDict()

    def __init__(self):
        self._completer_thread = None
        self._restart_refresh = threading.Event()

    def refresh(self, mssqcliclient, callbacks, history=None,
                settings=None):
        """
        Creates a OsqlCompleter object and populates it with the relevant
        completion suggestions in a background thread.

        osqlcliclient - used to extract the credentials to connect
                   to the database.
        settings - dict of settings for completer object
        callbacks - A function or a list of functions to call after the thread
                    has completed the refresh. The newly created completion
                    object will be passed in as an argument to each callback.
        """
        if self.is_refreshing():
            self._restart_refresh.set()
            return [(None, None, None, 'Auto-completion refresh restarted.')]
        else:
            self._completer_thread = threading.Thread(
                target=self._bg_refresh,
                args=(mssqcliclient, callbacks, history, settings),
                name='completion_refresh')
            self._completer_thread.setDaemon(True)
            self._completer_thread.start()
            return [(None, None, None,
                     'Auto-completion refresh started in the background.')]

    def is_refreshing(self):
        return self._completer_thread and self._completer_thread.is_alive()

    def _bg_refresh(self, osqlcliclient, callbacks, history=None,
                    settings=None):
        settings = settings or {}
        completer = OsqlCompleter(smart_completion=True, settings=settings)

        executor = osqlcliclient
        owner_uri, error_messages = executor.connect_to_database()

        if not owner_uri:
            # If we were unable to connect, do not break the experience for the user.
            # Return nothing, smart completion can maintain the keywords and functions completions.
            logger.error(u'Completion refresher connection failure.'.join(error_messages))
            return
        # If callbacks is a single function then push it into a list.
        if callable(callbacks):
            callbacks = [callbacks]

        while 1:
            for refresher in self.refreshers.values():
                refresher(completer, executor)
                if self._restart_refresh.is_set():
                    self._restart_refresh.clear()
                    break
            else:
                # Break out of while loop if the for loop finishes natually
                # without hitting the break statement.
                break

            # Start over the refresh from the beginning if the for loop hit the
            # break statement.
            continue

        # Load history into osqlcompleter so it can learn user preferences
        n_recent = 100
        if history:
            for recent in history[-n_recent:]:
                completer.extend_query_history(recent, is_init=True)

        for callback in callbacks:
            callback(completer)


def refresher(name, refreshers=CompletionRefresher.refreshers):
    """Decorator to populate the dictionary of refreshers with the current
    function.
    """
    def wrapper(wrapped):
        refreshers[name] = wrapped
        return wrapped
    return wrapper


@refresher('schemata')
@decorators.suppress_all_exceptions()
def refresh_schemata(completer, osqlcliclient):
    completer.extend_schemata(osqlcliclient.get_schemas())


@refresher('tables')
@decorators.suppress_all_exceptions()
def refresh_tables(completer, osqlcliclient):
    completer.extend_relations(osqlcliclient.get_tables(), kind='tables')
    completer.extend_columns(osqlcliclient.get_table_columns(), kind='tables')
    completer.extend_foreignkeys(osqlcliclient.get_foreign_keys())


@refresher('views')
@decorators.suppress_all_exceptions()
def refresh_views(completer, osqlcliclient):
    completer.extend_relations(osqlcliclient.get_views(), kind='views')
    completer.extend_columns(osqlcliclient.get_view_columns(), kind='views')


@refresher('databases')
@decorators.suppress_all_exceptions()
def refresh_databases(completer, osqlcliclient):
    completer.extend_database_names(osqlcliclient.get_databases())


@refresher('types')
@decorators.suppress_all_exceptions()
def refresh_types(completer, osqlcliclient):
    completer.extend_datatypes(osqlcliclient.get_user_defined_types())
