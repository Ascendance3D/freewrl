# Toplevel Makefile.am
#
#
# Defines build subdirectories.
# Defines all files distributed by this package.

# Get global variables for Makefile defined by toplevel Makefile.globals
include $(top_srcdir)/Makefile.globals

# See configure.ac
ACLOCAL_AMFLAGS = -I m4

SUBDIRS = src doc

EXTRA_DIST = ChangeLog \
README \
AUTHORS \
autogen.sh \
COPYING \
INSTALL \
NEWS \
vtempl.in \
Makefile.globals \
spidermonkey.pc \
codegen \
data \
doc/AUTOCONF \
doc/AUTOMAKE \
doc/DEPENDENCY \
doc/LIBTOOL \
doc/VERSION \
versions/FREEWRL \
versions/JAVACLASSES \
versions/LIBFREEWRL \
versions/LIBFREEWRL_LTVERSION \
versions/LIBFREEWRLEAI \
versions/LIBFREEWRLEAI_LTVERSION \
versions/MESSAGEMGR \
versions/PLUGIN \
versions/SOUNDMGR \
versions/template/version.c.in

pixmapdir = $(datadir)/pixmaps
pixmap_DATA = data/freewrl.png

freedesktopdir = $(datadir)/applications
freedesktop_DATA = data/freewrl.desktop

# doc/Makefile.am installs and distributes the freewrl.1 man page.

all: vtempl
