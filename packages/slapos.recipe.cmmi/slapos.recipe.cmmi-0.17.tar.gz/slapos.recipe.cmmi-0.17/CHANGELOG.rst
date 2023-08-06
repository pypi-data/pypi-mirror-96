Changes
=======

0.17 (2021-02-26)
-----------------

* fix_shebang: don't touch symlinks.

0.16 (2020-05-08)
-----------------

* propagate strip_top_level_dir option to slapos.recipe.build:downloadunpacked

0.15 (2020-04-23)
-----------------

* slapos.recipe.build.env.sh improvements/fixes.

0.14 (2020-04-22)
-----------------

* Include part signature inside shared signature.
* Drop 'dependencies' option.
* Remove useless '_profile_base_location_' entry from shared signature.
* Expand environment variables during install (rather than during init).

0.13 (2020-03-31)
-----------------

* set -e for shell commands

0.12 (2019-12-12)
-----------------

* shared: Fix recovery after an interrupted build

0.11 (2019-10-02)
-----------------

* Support multiple directories for shared parts. This now uses
  ``${buildout:shared-part-list}`` as list of directories to use.


0.10 (2018-11-30)
-----------------

* Make sure FDs are closed before spawning subprocesses.

0.9 (2018-10-29)
----------------

* More Py3 fixes.

0.8 (2018-08-27)
----------------

* Add shared feature.

0.7 (2017-06-06)
----------------

* Fix MANIFEST.in: some files were missing.

0.6 (2017-06-05)
----------------

* Add support for Python 3.
* Optimize wrapper to scripts with long shebangs.

0.5 (2017-04-07)
----------------

* Create a wrapper shell script for very long shebang scripts.

0.4 (2017-03-08)
----------------

* Use slapos.recipe.build:downloadunpacked instead of hexagonit.recipe.download.

0.1.1 (2013-04-12)
------------------

* Fix the wrong name 'path_filename'

0.1 (2013-04-12)
----------------

* Initial release, forking from hexagonit.recipe.cmmi (https://github.com/hexagonit/hexagonit.recipe.cmmi)
