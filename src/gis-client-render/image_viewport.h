/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#ifndef IMAGE_VIEWPORT_H
#define IMAGE_VIEWPORT_H

#include <QEvent>
#include <QGraphicsScene>
#include <QGraphicsView>
#include <QWheelEvent>
#include <QGraphicsProxyWidget>

class ImageViewport : public QGraphicsView
{
    Q_OBJECT

public:
    explicit ImageViewport();
     
    void fit_image();
protected:
    virtual void wheelEvent( QWheelEvent *event );
private:
    const double scroll_step = 1.3;
    QGraphicsScene *graphics_scene;
    QGraphicsProxyWidget *proxy;
    QGraphicsPixmapItem *currentMapItem;
public slots:
    void show_map_image( const QImage &img );
    void clean_map_image();
};

#endif // IMAGE_VIEWPORT_H
