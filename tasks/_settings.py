# -*- encoding: ascii -*-
"""
Project Settings
~~~~~~~~~~~~~~~~

"""


settings = dict(
    package="gensaschema",
    #
    # Dependencies
    #
    deps=dict(no_compat=["sqlalchemy"]),
    #
    # Wheels
    #
    wheels=dict(
        build="universal",
    ),
)
