/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#include "mainwidget.h"

#include <QApplication>
#include <QDebug>
#include <QLabel>
#include <QHBoxLayout>
#include <QVBoxLayout>

#include <QMutex>
#include <QWaitCondition>
#include <QDir>

#include "gismapserver.h"

MainWidget::MainWidget( double x_pos,
                        double y_pos,
                        uint32_t width,
                        uint32_t height,
                        uint32_t scale,
                        const char *server_url,
                        const char *image_format,
                        const char *outputImageName,
                        bool consoleMode ) : QWidget(),
    _consoleMode( consoleMode ),
    _outputImageName( outputImageName ),
    _server_url( server_url ),
    _image_format( image_format ),
    request_btn_state( true ),
    field_x_pos(  new QLineEdit() ),
    field_y_pos(  new QLineEdit() ),
    field_width(  new QLineEdit() ),
    field_height( new QLineEdit() ),
    field_scale(  new QLineEdit() ),
    urlEdit(new QLineEdit()),
    formatBox(new QComboBox()),
    request_btn(  new QPushButton( tr( "Request map" ) ) )
{   
    /* 
     * Do not rescale left dock panel's widgets and contents.
     */
    QSizePolicy size_policy;
    size_policy.setVerticalPolicy( QSizePolicy::Fixed );
    size_policy.setHorizontalPolicy( QSizePolicy::Fixed );
    setSizePolicy( size_policy );

    /*
     * Placing console parameters into fields, if they are present
     * If they are not present, use placeholders with input hints.
     */
    if ( width != 0 )     
        field_width->setText( QString::number( width, 10 ) );

    if ( height != 0 )    
        field_height->setText( QString::number( height, 10 ) );

    if ( x_pos != -999 )    
        field_x_pos->setText( QString::number( x_pos, 'f', 6 ) );
    else                  
        field_x_pos->setPlaceholderText( QString( "[-180...180]" ) );

    if ( y_pos != -999 )    
        field_y_pos->setText( QString::number( y_pos, 'f', 6 ) );
    else                  
        field_y_pos->setPlaceholderText( QString( "[-90...90]" ) );

    if ( scale != 0 )    
        field_scale->setText( QString::number( scale, 10 ) );
    else
        field_scale->setText( "1000000" );

    QStringList acceptedFormats;
    acceptedFormats << "bmp" << "png" << "jpg";
    formatBox->addItems(acceptedFormats);

    int idx = formatBox->findText(image_format);
    if (idx >= 0)
        formatBox->setCurrentIndex(idx);

    urlEdit->setText( server_url );

    /* 
     * Acceptable longtitude range: [ -180 ... 180 ]. 
     */
    longtitude_validator = new QDoubleValidator();
    longtitude_validator->setRange( -180.0, 180.0 );
    longtitude_validator->setDecimals( 8 );
    longtitude_validator->setNotation( QDoubleValidator::StandardNotation );
    field_x_pos->setValidator( longtitude_validator );

    /* 
     * Acceptable latitude range: [ -90 ... 90 ].
     */
    latitude_validator = new QDoubleValidator();
    latitude_validator->setRange( -90.0, 90.0 );
    latitude_validator->setDecimals( 8 );
    latitude_validator->setNotation( QDoubleValidator::StandardNotation );
    field_y_pos->setValidator( latitude_validator );

    /* 
     * Acceptable width and height of resulting image in pixels: positive values.
     */
    QIntValidator *pixel_validator = new QIntValidator();
    pixel_validator->setBottom( 1 );
    field_width->setValidator( pixel_validator );
    field_height->setValidator( pixel_validator );

    /* 
     * Setting up the left dock panel's vertical layout order.
     */
    QVBoxLayout *vlayout = new QVBoxLayout();
    QHBoxLayout *hlayout = new QHBoxLayout();
    vlayout->addWidget( new QLabel( tr( "Image width (px):" ) ) );
    vlayout->addWidget( field_width );
    vlayout->addWidget( new QLabel( tr( "Image height (px):" ) ) );
    vlayout->addWidget( field_height );
    vlayout->addWidget( new QLabel( tr( "Longtitude:" ) ) );
    vlayout->addWidget( field_x_pos );
    vlayout->addWidget( new QLabel( tr( "Latitude:" ) ) );
    vlayout->addWidget( field_y_pos );
    vlayout->addWidget( new QLabel( tr( "Scale:" ) ) );
    hlayout->addWidget( new QLabel( "1:" ) );
    hlayout->addWidget( field_scale );
    vlayout->addLayout( hlayout );
    vlayout->addWidget( new QLabel( tr( "URL:" ) ) );
    vlayout->addWidget( urlEdit );
    vlayout->addWidget( new QLabel( tr( "Format:" ) ) );
    vlayout->addWidget(formatBox);
    vlayout->addWidget( request_btn );
    setLayout( vlayout );

    connect( request_btn, SIGNAL( released() ), 
             this, SLOT( request_btn_handler() ) );

    /*
     * Go to the next input field if user pressed Enter in the previous one
     */
    connect( field_width, SIGNAL( returnPressed() ), 
                    this, SLOT( go_to_field_height() ) ); 
    connect( field_height, SIGNAL( returnPressed() ), 
                    this, SLOT( go_to_field_x_pos() ) ); 
    connect( field_x_pos, SIGNAL( returnPressed() ), 
                    this, SLOT( go_to_field_y_pos() ) ); 
    connect( field_y_pos, SIGNAL( returnPressed() ), 
                    this, SLOT( go_to_field_scale() ) ); 
    connect( field_scale, SIGNAL( returnPressed() ), 
                    this, SLOT( go_to_request_btn() ) ); 
    request_btn->setDefault( true );

    /*
     * Trying to imitate click
     */
    if ( _consoleMode ) {
        request_btn_handler();
    }
}

void MainWidget::start_processing_request()
{
    /*
     * Latitudes and longtitudes may have "Intermediate" validation state,
     * which means that if 180 is the greatest value that is acceptable,
     * user can't type in 1800, but he can type in 184, which is out of range.
     * This check prohibits invalid input.
     * 
     * Width and height validation is omitted due to the fact that only
     * positive numbers are allowed.
     * 
     * See: https://doc.qt.io/qt-5/qintvalidator.html#validate
     */
    int cursor = 0;
    QString temp_x_pos = field_x_pos->text();
    QString temp_y_pos = field_y_pos->text();
    if ( longtitude_validator->validate( temp_x_pos, cursor ) != QValidator::Acceptable ) 
    {
        field_x_pos->clear();
        return;
    }

    if ( latitude_validator->validate( temp_y_pos, cursor ) != QValidator::Acceptable )
    {
        field_y_pos->clear();
        return;
    }

    /*
     * Request map rendering from server and wait for reply.
     */
    process_request();
}

void MainWidget::process_request()
{
    double lon = field_x_pos->text().toDouble();
    double lat = field_y_pos->text().toDouble();
    uint w = field_width->text().toUInt();
    uint h = field_height->text().toUInt();
    uint scale = field_scale->text().toUInt();

    QString format = formatBox->currentText();
    QString url = urlEdit->text();

    qDebug() << "Sending request: ";
    qDebug() << "X:" << lon
             << "Y:" << lat
             << "Width:" << w
             << "Height:" << h
             << "Scale: 1 :" << scale
             << "Format:" << format;

    uint orderId = 0;
    char pinCode[128];
    int status = gis_map_server_request_map( url.toStdString().c_str(), lat, lon, scale, w, h, format.toStdString().c_str(), &orderId, pinCode );
    if ( status != 0 ) {
        qDebug() << "Failed to make request" << status;
        if ( _consoleMode ) {
            exit(1);
        }
        return;
    }

    qDebug() << "Client got id:" << orderId;
    qDebug() << "Client got pincode:" << pinCode;

    status = gis_map_server_get_image( url.toStdString().c_str(), orderId, pinCode, &image );
    if ( status != 0 ) {
        qDebug() << "Failed to get image" << status;
        if ( _consoleMode ) {
            exit(1);
        }
        return;
    }
    qDebug() << "Got image";

    if ( _consoleMode ) {
        if ( image.save( _outputImageName ) )
            qDebug() << "Image was saved to current directory as " << _outputImageName;
        else
            qDebug() << "Failed to save image as " << _outputImageName;

        exit(0);
    }

    emit request_completed( image );
}

void MainWidget::set_UI_active( bool state )
{
    field_x_pos->setEnabled( state );
    field_y_pos->setEnabled( state );
    field_width->setEnabled( state );
    field_height->setEnabled( state );
    field_scale->setEnabled( state );
}

void MainWidget::request_btn_handler()
{
    set_UI_active( false );
    start_processing_request();
    set_UI_active( true );
}
