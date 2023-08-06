
django-template-admin-urls
==========================

Micro-package that provides a helping utility for manual tesing. Like for example template block with links for editing current page instance in admin.

Installation
------------

``$ pip install django-template-admin-urls``

Add ``dj_template_admin_urls`` to ``INSTALLED_APPS``

Template blocks
---------------

``admin_links.jinja`` - provides header block with links such as:


* admin dashboard url
* admin's url of object page

Template tags
-------------


* ``object_admin_url`` - returns object's url in admin
* ``admin_url`` - admin dashboard url
