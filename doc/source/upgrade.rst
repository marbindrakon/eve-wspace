Upgrading EWS
=============

Here are the general instructions for upgrading your Eve W-Space instance to a new release.

Upgrade Files
-------------
If you are tracking the Github repository (release verisons are in the master branch), you can simply use git to update your files:

As a user that can write to your instance directory:

:command:`$ git pull`

If you installed from the tarball, then simply overwrite the old files with the new version.

Upgrade Requirements
--------------------
A new version may introduce new requirements. As root if you installed without a virtualenv, or with your virtualenv active:

:command:`(eve-wspace) $ pip install --upgrade -r requirements.txt`

Note: requirements.txt is located in the repository root

Upgrade Database
----------------
Eve W-Space uses South for database schema and data migrations. To migrate to the new version, simply run:

:command:`(eve-wspace) $ ./manage.py migrate`

Simply say 'yes' to any tables being removed unless they are yours.

Note: manage.py is located in the evewspace directory from the repository root

Note: If you installed into a virtualenv, it should be active

Upgrade Static Files
--------------------
With your virtualenv active (if applicable):

:command:`(eve-wspace) $ ./manage.py collectstatic ---noinput`

Reset Settings
--------------
A new version may introduce new settings that need to be initialized, to do so, reset your settings to defaults.

With your virtualenv active (if applicable):

:command:`(eve-wspace) $ ./manage.py defaultsettings`

Reset Services
--------------
Now that the instance is up to the new version, you will need to restart celery and your application server for the changes to fully take effect:

How this works will vary based on your enviornment. The instructions below are for the environments set up with the install guides.

As root:

:command:`# supervisorctl restart celeryd`

For Nginx / gunicorn based installs:

:command:`# supervisorctl restart gunicorn`

For Apache installs on Ubuntu / Debian:

:command:`# service apache2 reload`


Done!
-----
If everything went okay, you should now be upgraded to the new version. You may need to refresh some pages to get updated javascript if your browser has cached the old data.

If you have trouble or questions, please join us on Coldfront IRC in #eve-wspace, in game at Eve W-Space, or via e-mail at marbin@evewspace.com.
