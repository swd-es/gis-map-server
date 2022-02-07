QT += core gui network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

qnx {
    # Get install directory for defining command to run
    INSTALLDIRECTORY=$$(INSTALLDIR)

    !isEmpty(INSTALLDIRECTORY) {
        target.path = $$(INSTALLDIR)
    }

    isEmpty(INSTALLDIRECTORY) {
        INSTALLDIRECTORY = "/opt/gis/bin"
        target.path = $$INSTALLDIRECTORY
        message(Manual path setting $$INSTALLDIRECTORY)
    }
}

TEMPLATE = app

INSTALLS += target

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

SOURCES += main.cpp\
           mainwidget.cpp \
           mainwindow.cpp \
           image_viewport.cpp \
           gismapserver.cpp \
           mapsender.cpp

HEADERS += mainwidget.h \
           mainwindow.h \
           image_viewport.h \
           gismapserver.h \
           mapsender.h
           
# If: Cannot find file 'translations/gis-client-render_ru.qm'
# then run lupdate, lrelease manually
TRANSLATIONS += $$_PRO_FILE_PWD_/translations/$$join(TARGET,,,_ru.ts)

RESOURCES += \
    images.qrc \
    translations.qrc

QMAKE_CXXFLAGS += -std=gnu++11
