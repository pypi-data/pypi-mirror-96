=====
Gadjo
=====

Gadjo is a base template for Django applications, tailored for
management interfaces, built to provide a nice and modern look, while
using progressive enhancement and responsive designs to adapt to
different environments.


Usage
=====

Make your application base template {% extends "gadjo/base.html" %}.


You should add gadjo.finders.XStaticFinder to STATICFILES_FINDERS,

  from django.conf import global_settings

  STATICFILES_FINDERS = global_settings.STATICFILES_FINDERS + \
    ('gadjo.finders.XStaticFinder',)

There is a CDNS settings, that can contain a list of (cdn name, protocol)
tuples; for example:

  CDNS = [('google', 'https')]


Additional static files
------------------------

Additional static files libraries can be added via INSTALLED_APPS,
for example 'xstatic.pkg.jquery_tablesorter'; its static files can
then be referred in a template using the xstatic template tag:

  {% xstatic 'jquery_tablesorter' 'jquery.tablesorter.js' %}


Progressive enhancement -- Dialogs
----------------------------------

Links marked with rel="popup" will be opened into dialog boxes.

The dialog title is extracted from "#appbar h2" (this selector can be
changed with a @data-title-selector attribute on the anchor tag).

The dialog content is extracted from "form" (this selector can be
changed with a @data-selector attribute).

Buttons (both <button> and <a>) are extracted from the content and
converted into proper dialog buttons.  A button with "cancel" as its
class will have its action changed to simply close the dialog, without
server processing.

After loading the dialog content, a gadjo:dialog-loaded event is
triggered on the anchor with the dialog content as argument.

Alternatively the server may notice the ajax request and answer with
an appropriate JSON response. In that case it should have a 'content'
attribute with the HTML content, or a 'location' attribute in case of
a redirect.

In case of such a redirect, a gadjo:dialog-done event is triggered on
the anchor and can be cancelled to prevent the default redirect
behaviour.


Licence
=======

Python, Javascript and CSS files are published under the GNU AFFERO GENERAL
PUBLIC LICENSE (see the COPYING file for the complete text).

gadjo/static/images/info-icon.png and icons/*.svg are derived work of icons
from gnome-icon-theme-symbolic, published under the Creative Commons
Attribution-Share Alike 3.0 United States License by the GNOME Project, see
http://www.gnome.org/.

gadjo/static/css/header-03.jpeg is copied from let's encrypt website, licensed
under Mozilla Public License Version 2.0, see their repository at
https://github.com/letsencrypt/website.git.

The querystring template tag is originally from django-tables2, copyright (c)
2011, Bradley Ayers, copyright (c) 2008, Michael Elsdörfer, published under
the MIT license.
https://raw.githubusercontent.com/jieter/django-tables2/master/LICENSE
