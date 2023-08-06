
.. contents::

Supported options
=================

Attention: Python3 only version! If you're using Python2 you have to pin
this package version to <2.0.0.

This recipe supports the following options:

url
    URL pointing to the ``haproxy`` compressed archive. By default it uses:
    http://www.haproxy.org/download/2.1/src/haproxy-2.1.3.tar.gz

target
    Target can be one of the following:
    linux22, linux24, linux24e linux24eold, linux26, solaris, freebsd,
    openbsd, generic.

cpu
    CPU can be one of the following: i686, i586, ultrasparc, generic.

pcre
    Set to ``1`` to enable the use of the PCRE library.


Example usage
=============

To use this recipe, just create a part for it and define the ``recipe``
parameter::

    [buildout]
    parts =
        ...
        haproxy

    [haproxy]
    recipe = plone.recipe.haproxy

This will configure the default options for ``url``, ``target``, ``pcre``, and
``cpu``. If you like or need to you can override these parameters, e.g.::

    [haproxy]
    recipe = plone.recipe.haproxy
    url = http://my.dist.server/haproxy-1.x.y.zip
    target = linux26
    cpu = i686
    pcre = 1


Reporting bugs or asking questions
==================================

https://github.com/plone/plone.recipe.haproxy/issues


Code repository
===============

https://github.com/plone/plone.recipe.haproxy
