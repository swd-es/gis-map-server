/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QDockWidget>
#include <QMainWindow>
#include <QWheelEvent>

#include "image_viewport.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow( double x_pos, 
                         double y_pos,
                         uint32_t width,
                         uint32_t height,
                         uint32_t scale,
                         const char *server_url,
                         const char *image_format,
                         const char *outputImageName,
                         bool consoleMode );

private:
    ImageViewport *viewport;
protected:
    virtual void resizeEvent( QResizeEvent *event );
};

#endif // MAINWINDOW_H
