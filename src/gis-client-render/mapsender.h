/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#ifndef MAPSENDER_H
#define MAPSENDER_H

#include <QNetworkReply>
#include <QNetworkAccessManager>

class MapSender : public QObject
{
    Q_OBJECT
public:
    explicit MapSender( const QString &server_address, const int userId, const uint timeout_ms ) :
        _url( server_address ),
        _orderId( userId ),
        _timeout_ms( timeout_ms )
    {
        manager = new QNetworkAccessManager();
    }

    //Client calls
    int sendRequest(double lat, double lon, int scale, int w, int h, const char* format, uint* userId , char* pinCode);
    int getImageWithWaiting( char *pinCode, QImage *image );

private:
    int getImage( char *pinCode, QImage *image );
    void waitForReplyFinished( QNetworkReply *reply, uint timeout_ms );

    const QString _url;
    const int _orderId;
    const uint _timeout_ms;
    QNetworkAccessManager *manager;
};

#endif // MAPSENDER_H
