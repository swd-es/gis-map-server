/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#include <cstring>
#include <unistd.h>

#include <QApplication>
#include <QDebug>
#include <QTranslator>

#include "mainwidget.h"
#include "mainwindow.h"

int main( int argc, char *argv[] )
{
    double x_pos = -999, y_pos  = -999;
    uint32_t width = 0, height = 0, scale = 0;
    const char *server_url = nullptr;
    const char *image_format = nullptr;
    const char *outputImageName = nullptr;
    bool consoleMode = false;

    QLocale::setDefault(QLocale::C);

    int opt = 0;
    extern char *optarg;
    while ( ( opt = getopt( argc, argv, "x:y:w:h:s:u:f:o:" ) ) != -1 )
    {
        switch ( opt )
        {
            case 'x': x_pos = atof( optarg ); break;
            case 'y': y_pos = atof( optarg ); break;
            case 'w': width = strtoul( optarg, NULL, 0 ); break;
            case 'h': height = strtoul( optarg, NULL, 0 ); break;
            case 's': scale = strtoul( optarg, NULL, 0 ); break;
            case 'u': server_url = strdup( optarg ); break;
            case 'f': image_format = strdup( optarg ); break;
            case 'o':
            {
                consoleMode = true;
                outputImageName = strdup( optarg );
                break;
            }

            case '?': printf( "Error: unknown option\n" ); exit(1); break;
        };
    };

    QApplication app( argc, argv );

    QString ablangStr = getenv( "ABLANG" );
    if ( ablangStr.isEmpty() ) {
        ablangStr = getenv( "LANG" );
    }
    QTranslator myTranslator;
    myTranslator.load( ":/translations/gis-client-render_" +  ablangStr );
    app.installTranslator( &myTranslator );

    MainWindow window( x_pos, y_pos, width, height, scale, server_url, image_format, outputImageName, consoleMode );
    window.show();

    return app.exec();
}
