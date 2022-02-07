/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#ifndef MAINWIDGET_H
#define MAINWIDGET_H

#include <QComboBox>
#include <QLineEdit>
#include <QPushButton>
#include <QValidator>
#include <QWidget>

class MainWidget : public QWidget
{
    Q_OBJECT
public:

    explicit MainWidget( double x_pos,
                         double y_pos,
                         uint32_t width,
                         uint32_t height,
                         uint32_t scale,
                         const char *server_url,
                         const char *image_format,
                         const char *outputImageName,
                         bool consoleMode );

    QImage image;

private:
    const bool _consoleMode;
    const char *_outputImageName;
    const char *_server_url;
    const char *_image_format;

    void            process_request();
    void            set_UI_active( bool state );

    bool            request_btn_state;

    QDoubleValidator   *longtitude_validator;
    QDoubleValidator   *latitude_validator;

    QLineEdit       *field_x_pos;
    QLineEdit       *field_y_pos;
    QLineEdit       *field_width;
    QLineEdit       *field_height;
    QLineEdit       *field_scale;
    QLineEdit       *urlEdit;
    QComboBox       *formatBox;
    QPushButton     *request_btn;

signals:
    void request_completed( const QImage &img );
    void request_failed();
public slots:
    
    void    start_processing_request();
    void    request_btn_handler();

    /*
     * Go to the next input field if user pressed Enter in the previous one
     */
    void    go_to_field_height()    { field_height->setFocus( Qt::OtherFocusReason ); }
    void    go_to_field_x_pos()     { field_x_pos->setFocus( Qt::OtherFocusReason ); }
    void    go_to_field_y_pos()     { field_y_pos->setFocus( Qt::OtherFocusReason ); }
    void    go_to_field_scale()     { field_scale->setFocus( Qt::OtherFocusReason ); }
    void    go_to_request_btn()     { request_btn->setFocus( Qt::OtherFocusReason ); }
};

#endif // MAINWIDGET_H
