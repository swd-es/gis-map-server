/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#include "image_viewport.h"

#include <QGraphicsPixmapItem>
#include <QLabel>
#include <QMovie>

#include <QDebug>

ImageViewport::ImageViewport() : QGraphicsView(),
    currentMapItem( nullptr )
{
    /*
     * Animated earth's GIF setup
     * Runs until user performs a request
     *
     * See: https://forum.qt.io/topic/15658/solved-how-to-play-gif-animation-in-qgraphicsview-widget
     */
    graphics_scene = new QGraphicsScene();
    graphics_scene->setBackgroundBrush( QColor( 239, 239, 239 ) );
    QLabel *animation = new QLabel();
    QMovie *earth_gif = new QMovie( ":/images/earth.gif" );
    animation->setMovie( earth_gif );
    earth_gif->setSpeed( 90 );
    earth_gif->start();
    proxy = graphics_scene->addWidget( animation );

    /*
     * Placing a circle around GIF to hide its low resolution
     */
    QPen earth_bound( (QColor( Qt::black )) );
    earth_bound.setWidth( 5 );
    graphics_scene->addEllipse( QRectF( 0, 0, 257, 257 ),
                                QPen( earth_bound ),
                                QBrush( QColor( 0, 0, 0, 0 ) ) );
        
    setScene( graphics_scene );
    setDragMode( QGraphicsView::ScrollHandDrag );
    setHorizontalScrollBarPolicy( Qt::ScrollBarAlwaysOff );
    setVerticalScrollBarPolicy( Qt::ScrollBarAlwaysOff );
}  

void ImageViewport::fit_image()
{
    /*
     * Place the center of the image at the center of the viewport
     */
    centerOn( graphics_scene->width() / 2, 
              graphics_scene->height() / 2 );

    /*
     * Keep the whole image inside the viewport, saving the aspect ratio
     */
    fitInView( QRectF( 0, 0, 
                       graphics_scene->width(), 
                       graphics_scene->height() ), 
                       Qt::KeepAspectRatio );
}

void ImageViewport::wheelEvent( QWheelEvent *event )
{
    if ( event->delta() > 0 )
        scale( scroll_step, scroll_step );

    if ( event->delta() < 0 )
        scale( 1 / scroll_step, 1 / scroll_step );
}

void ImageViewport::show_map_image( const QImage &image )
{
    proxy->hide();
    if ( currentMapItem )
        graphics_scene->removeItem( currentMapItem );

    currentMapItem = new QGraphicsPixmapItem( QPixmap::fromImage( image ) );
    graphics_scene->addItem( currentMapItem );
    fit_image();
}

void ImageViewport::clean_map_image()
{
    proxy->show();
    if ( currentMapItem ) {
        graphics_scene->removeItem( currentMapItem );
        currentMapItem = nullptr;
    }

    fit_image();
}
