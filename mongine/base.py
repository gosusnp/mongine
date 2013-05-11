#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8 :

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DEFAULT_DB_ALIAS
from django.db.backends.creation import TEST_DATABASE_PREFIX

try:
    from pymongo import MongoClient
except ImportError as e:
    raise ImproperlyConfigured("Error loading pymongo module: %s" % e)

class DatabaseOperations(object):
    def __init__(self, connection):
        self.connection = connection
    def set_time_zone_sql(self):
        return ''

class DatabaseCreation(object):
    def __init__(self, connection):
        self.connection = connection

    def _get_test_database_name(self):
        if self.connection.settings_dict['TEST_NAME']:
            return self.connection.settings_dict['TEST_NAME']
        return TEST_DATABASE_PREFIX + self.connection.database

    def create_test_db(self, verbosity=1, autoclobber=False):
        test_database_name = self._get_test_database_name()

        if verbosity >= 1:
            test_db_repr = ''
            if verbosity >= 2:
                test_db_repr = " ('%s')" % test_database_name
            print "Creating test database for alias '%s'%s..." % (
                self.connection.alias, test_db_repr)

        # Since databases are dynamically created the only thing we
        # have to do to ensure having a clean database is to drop it.
        self.connection.ensure_connection()
        self.connection.connection.drop_database(test_database_name)

        settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
        self.connection.settings_dict["NAME"] = test_database_name
        self.connection.database = test_database_name

        return test_database_name

    def destroy_test_db(self, old_database_name, verbosity=1):
        test_database_name = self.connection.settings_dict['NAME']
        if verbosity >= 1:
            test_db_repr = ''
            if verbosity >= 2:
                test_db_repr = " ('%s')" % test_database_name
            print "Destroying test database for alias '%s'%s..." % (
                self.connection.alias, test_db_repr)

        self.connection.ensure_connection()
        self.connection.connection.drop_database(test_database_name)

    def test_db_signature(self):
        """

        Returns a tuple with elements of self.connection.settings_dict (a
        DATABASES setting value) that uniquely identify a database
        accordingly to the RDBMS particularities.

        """
        settings_dict = self.connection.settings_dict
        return (
            settings_dict['HOST'],
            settings_dict['REPLICASET'],
            settings_dict['ENGINE'],
            settings_dict['NAME']
        )

class DatabaseFeatures(object):
    def __init__(self, connection):
        self.connection = connection

    supports_transactions = False

class DatabaseWrapper(object):
    def __init__(self, settings_dict, alias=DEFAULT_DB_ALIAS,
                 allow_thread_sharing=False):
        # `settings_dict` should be a dictionary containing keys such as
        # NAME, USER, etc. It's called `settings_dict` instead of `settings`
        # to disambiguate it from Django settings modules.
        self.connection = None
        self.settings_dict = settings_dict
        self.alias = alias

        if not self.settings_dict['NAME']:
            raise ImproperlyConfigured(
                    "settings.DATABASES is improperly configured. "
                    "Please supply the NAME value.")
        self.database = self.settings_dict['NAME']

        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.creation = DatabaseCreation(self)


    def __eq__(self, other):
        return self.alias == other.alias

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.alias)

    def get_connection_params(self):
        conn_params = {}
        for k1, k2 in (('HOST', 'host'), ('REPLICASET', 'replicaSet')):
            if self.settings_dict[k1]:
                conn_params[k2] = self.settings_dict[k1]
        return conn_params

    def get_new_connection(self, conn_params):
        return MongoClient(**conn_params)

    def connect(self):
        """Connect to the database. Assume connection is closed."""
        conn_params = self.get_connection_params()
        self.connection = self.get_new_connection(conn_params)

    def ensure_connection(self):
        if self.connection is None:
            self.connect()

    def close(self):
        try:
            self._close()
        finally:
            self.connection = None

    def _close(self):
        if self.connection is not None:
            self.connection.close()

    def cursor(self):
        self.ensure_connection()
        return self.connection[self.database]

    def abort(self):
        pass
    def rollback_unless_managed(self):
        pass

