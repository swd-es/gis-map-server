/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#include "mainwindow.h"
#include "mainwidget.h"

MainWindow::MainWindow( double x_pos,
                        double y_pos,
                        uint32_t width,
                        uint32_t height,
                        uint32_t scale,
                        const char *server_url,
                        const char *image_format,
                        const char *outputImageName,
                        bool consoleMode ) : QMainWindow()
{
    /*
     * Left dock menu panel widget with request parameters
     */
    QDockWidget *dock_widget = new QDockWidget( tr( "Request parameters" ), this );
    dock_widget->setAllowedAreas( Qt::LeftDockWidgetArea );
    dock_widget->setFeatures( QDockWidget::NoDockWidgetFeatures );

    MainWidget *menu = new MainWidget( x_pos,
                                       y_pos,
                                       width,
                                       height,
                                       scale,
                                       server_url,
                                       image_format,
                                       outputImageName,
                                       consoleMode );
    dock_widget->setWidget( menu );
    addDockWidget( Qt::LeftDockWidgetArea, dock_widget );

    /*
     * Resulting image viewport widget
     */
    viewport = new ImageViewport();
    viewport->show();

    connect( menu, SIGNAL( request_completed( const QImage&) ),
            viewport, SLOT( show_map_image( const QImage&) ) );

    connect( menu, SIGNAL( request_failed() ),
            viewport, SLOT( clean_map_image() ) );


    setMinimumSize( 700, 400 );
    setWindowTitle( tr( "Cartographic client" ) );
    setCentralWidget( viewport );
}

/*
 * Reimplementation of Qt's resizeEvent() for image fitting 
 * in the viewport after each change of the window's size.
 */
void MainWindow::resizeEvent( QResizeEvent *event )
{
    Q_UNUSED( event );
    viewport->fit_image();
}
