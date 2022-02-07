ifndef QCONFIG
QCONFIG=qconfig.mk
endif
include $(QCONFIG)

COMPILER_DRIVER:=
include $(MKFILES_ROOT)/buildlist.mk
ifndef OS
include $(MKFILES_ROOT)/qmacros.mk
endif

USEFILE=

# GIS package options
ifneq ( $(GIS_INSTALL_ROOT), )
	DESTDIR:=$(GIS_INSTALL_ROOT)
endif
export GIS_INSTALL_ROOT=$(DESTDIR)

include $(MKFILES_ROOT)/qmake.mk
include $(MKFILES_ROOT)/qtargets.mk
