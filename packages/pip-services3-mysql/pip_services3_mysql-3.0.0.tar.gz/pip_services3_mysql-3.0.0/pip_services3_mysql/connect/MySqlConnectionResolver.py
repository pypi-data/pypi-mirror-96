# -*- coding: utf-8 -*-
from typing import List

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import IReferenceable
from pip_services3_components.auth import CredentialResolver
from pip_services3_components.connect import ConnectionResolver, ConnectionParams


class MySqlConnectionResolver(IReferenceable, IConfigurable):
    """
    Helper class that resolves MySQL connection and credential parameters,
    validates them and generates a connection URI.

    It is able to process multiple connections to MySQL cluster nodes.

    ### Configuration parameters ###
        - connection(s):
            - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - host:                        host name or IP address
            - port:                        port number (default: 27017)
            - database:                    database name
            - uri:                         resource URI or connection string with all parameters in it
        - credential(s):
            - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - username:                    user name
            - password:                    user password

    ### References ###
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services
        - `*:credential-store:*:*:1.0` (optional) :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>` stores to resolve credentials
    """

    def __init__(self):
        # The connections resolver.
        self._connection_resolver = ConnectionResolver()
        # The credentials resolver.
        self._credential_resolver = CredentialResolver()

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._connection_resolver.configure(config)
        self._credential_resolver.configure(config)

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._credential_resolver.set_references(references)
        self._connection_resolver.set_references(references)

    def __validate_connection(self, correlation_id, connection: ConnectionParams):
        uri = connection.get_uri()
        if uri:
            return

        host = connection.get_host()
        if not host:
            raise ConfigException(correlation_id, "NO_HOST", "Connection host is not set")

        port = connection.get_port()
        if port == 0:
            raise ConfigException(correlation_id, "NO_PORT", "Connection port is not set")

        database = connection.get_as_nullable_string('database')
        if not database:
            raise ConfigException(correlation_id, "NO_DATABASE", "Connection database is not set")

        return None

    def __validate_connections(self, correlation_id, connections: List[ConnectionParams]):
        if not connections or len(connections) == 0:
            raise ConfigException(correlation_id, "NO_CONNECTION", "Database connection is not set")

        for connection in connections:
            self.__validate_connection(correlation_id, connection)

        return None

    def __compose_uri(self, connections: List[ConnectionParams], credential):
        # If there is a uri then return it immediately
        for connection in connections:
            uri = connection.get_uri()
            if uri:
                return uri

        # Define hosts
        hosts = ''
        for connection in connections:
            host = connection.get_host()
            port = connection.get_port()

            if len(hosts) > 0:
                hosts += ','
            hosts += host + ('' if port is None else ':' + str(port))

        # Define database
        database = ''
        for connection in connections:
            database = database or connection.get_as_nullable_string('database')

        if len(database) > 0:
            database = '/' + database

        # Define authentication part
        auth = ''
        if credential:
            username = credential.get_username()
            if username:
                password = credential.get_password()
                if password:
                    auth = username + ':' + password + '@'
                else:
                    auth = username + '@'

        # Define additional parameters parameters
        options = ConfigParams.merge_configs(*connections).override(credential)
        options.remove('uri')
        options.remove('host')
        options.remove('port')
        options.remove('database')
        options.remove('username')
        options.remove('password')
        params = ''
        keys = options.get_key_names()
        for key in keys:
            if len(params) > 0:
                params += '&'

            params += key

            value = options.get_as_string(key)
            if value:
                params += '=' + value

        if len(params) > 0:
            params = '?' + params

        # Composer uri
        uri = "mysql://" + auth + hosts + database + params

        return uri

    def resolve(self, correlation_id):
        """
        Resolves MySQL connection URI from connection and credential parameters.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :return: resolved URI or raise error.
        """

        connections = self._connection_resolver.resolve_all(correlation_id)
        # Validate connections
        self.__validate_connections(correlation_id, connections)

        credential = self._credential_resolver.lookup(correlation_id)
        # Credentials are not validated right now

        return self.__compose_uri(connections, credential)
