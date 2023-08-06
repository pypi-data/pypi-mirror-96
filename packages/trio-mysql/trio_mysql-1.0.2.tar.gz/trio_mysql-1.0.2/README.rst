.. image:: https://readthedocs.org/projects/trio_mysql/badge/?version=latest
    :target: http://trio_mysql.readthedocs.io/
    :alt: Documentation Status


Trio-MySQL
==========

.. contents:: Table of Contents
   :local:

This package contains a pure-Python and Trio-enhanced MySQL client library.
It is a mostly-straightforward clone of PyMySQL, adding async methods
compatible with the Trio framework.

NOTE: Trio-MySQL tries to adhere to (an async version of) the high level
database APIs defined in `PEP 249`_. Some differences, however, are
unavoidable.

.. _`PEP 249`: https://www.python.org/dev/peps/pep-0249/


Requirements
-------------

* Python -- one of the following:

  - CPython_ : 3.6 and newer
  - PyPy_ : Latest 3.x version

* MySQL Server -- one of the following:

  - MySQL_ >= 5.6
  - MariaDB_ >= 10.0

.. _CPython: https://www.python.org/
.. _PyPy: https://pypy.org/
.. _MySQL: https://www.mysql.com/
.. _MariaDB: https://mariadb.org/


Installation
------------

Package is uploaded on `PyPI <https://pypi.org/project/PyMySQL>`_.

You can install it with pip::

    $ python3 -m pip install trio_mysql

To use "sha256_password" or "caching_sha2_password" for authenticate,
you need to install additional dependency::

   $ python3 -m pip install trio_mysql[rsa]

To use MariaDB's "ed25519" authentication method, you need to install
additional dependency::

   $ python3 -m pip install PyMySQL[ed25519]


Documentation
-------------

Documentation is available online: http://trio_mysql.readthedocs.io/

For support, please refer to the `StackOverflow
<https://stackoverflow.com/questions/tagged/trio_mysql>`_.


Example
-------

The following examples make use of a simple table

.. code:: sql

   CREATE TABLE `users` (
       `id` int(11) NOT NULL AUTO_INCREMENT,
       `email` varchar(255) COLLATE utf8_bin NOT NULL,
       `password` varchar(255) COLLATE utf8_bin NOT NULL,
       PRIMARY KEY (`id`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
   AUTO_INCREMENT=1 ;


.. code:: python

    import trio_mysql.cursors

    # Connect to the database
    connection = trio_mysql.connect(host='localhost',
                                 user='user',
                                 password='passwd',
                                 charset='utf8mb4',
                                 database='db',
                                 cursorclass=trio_mysql.cursors.DictCursor)

    async with connection as conn:
        async with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
            await cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        conn.commit()

        # You can set up a transaction:
        async with conn.transaction():
            async with conn.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
                await cursor.execute(sql, ('webmistress@python.org', 'totally-secret'))

        # ... or use a cursor directly, for autocommit:
        async with conn.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            await cursor.execute(sql, ('webmaster@python.org',))
            result = await cursor.fetchone()
            print(result)


This example will print:

.. code:: python

    {'password': 'very-secret', 'id': 1}


Resources
---------

* DB-API 2.0: https://www.python.org/dev/peps/pep-0249/

* MySQL Reference Manuals: https://dev.mysql.com/doc/

* MySQL client/server protocol:
  https://dev.mysql.com/doc/internals/en/client-server-protocol.html

* "Connector" channel in MySQL Community Slack:
  https://lefred.be/mysql-community-on-slack/

Trio chat: https://gitter.im/python-trio/general

License
-------

Trio-MySQL is released under the MIT License. See LICENSE for more information.
