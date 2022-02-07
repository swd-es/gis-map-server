ifndef QCONFIG
	QCONFIG=qconfig.mk
endif

include $(QCONFIG)

include $(MKFILES_ROOT)/qmacros.mk

NAME=$(notdir ${PROJECT_ROOT})

INSTALLDIR=/opt/gis/sbin/
RESOURCESDIR=/opt/gis/data/resources/${NAME}
LOGDIR=/opt/gis/data/config

PRE_INSTALL=$(CP_HOST) ${PROJECT_ROOT}/START.sh ${INSTALL_ROOT_nto}/${CPUVARDIR}/${INSTALLDIR}/${NAME}; $(CP_HOST) ${PROJECT_ROOT}/*.py ${INSTALL_ROOT_nto}/${CPUVARDIR}/${RESOURCESDIR}/
POST_INSTALL=$(CP_HOST) -R ${PROJECT_ROOT}/html ${INSTALL_ROOT_nto}/${CPUVARDIR}/${RESOURCESDIR}; $(CP_HOST) ${PROJECT_ROOT}/$(NAME).conf ${INSTALL_ROOT_nto}/${CPUVARDIR}/${LOGDIR}/$(NAME).conf

ALL_DEPENDENCIES=Makefile

include $(MKFILES_ROOT)/qtargets.mk
