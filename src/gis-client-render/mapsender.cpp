/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#include "mapsender.h"

#include <QApplication>
#include <QBuffer>
#include <QDateTime>
#include <QDebug>
#include <QImage>

#include "gismapserver.h"

int MapSender::sendRequest( double lat,
                            double lon,
                            int scale,
                            int w,
                            int h,
                            const char* format,
                            uint *orderId,
                            char *pinCode )
{
    QString requestUrl = _url + "/?";
    requestUrl += "&lat=" + QString::number(lat);
    requestUrl += "&lon=" + QString::number(lon);
    requestUrl += "&scale=" + QString::number(scale);
    requestUrl += "&w=" + QString::number(w);
    requestUrl += "&h=" + QString::number(h);
    requestUrl += "&format=" + QString(format);

    QUrl url( requestUrl );
    QNetworkRequest request(url);
    request.setRawHeader( QByteArray("agent"), QByteArray("gis") );

    QNetworkReply *reply = manager->get(request);
    waitForReplyFinished( reply, _timeout_ms );

    QVariant statusCodeAttribute = reply->attribute(QNetworkRequest::HttpStatusCodeAttribute);
    bool ok = false;
    GisHttpCodes statusCode = static_cast<GisHttpCodes>(statusCodeAttribute.toInt(&ok));
    if ( !ok || statusCode != GisHttpCodes::Ok ) {
        qDebug() << gis_map_server_get_error_message( statusCode );
        return EFAULT;
    }

    QString orderId_tag = "orderId=";
    QString pinCode_tag = "pincode=";

    QByteArray rawData = reply->readAll();
    QList<QByteArray> rawLines = rawData.split(',');

    QString orderStr( rawLines[0] );
    if (orderStr.contains( orderId_tag )) {
        orderStr.remove(orderId_tag);
        *orderId = orderStr.toUInt( &ok );
        if ( !ok ) {
            qDebug() << "Invalid <orderId>";
            return EFAULT;
        }
    }

    QString pinCodeStr( rawLines[1] );
    if (pinCodeStr.contains( pinCode_tag )) {
        pinCodeStr.remove(pinCode_tag);
        pinCodeStr.remove( " " );
        strcpy( pinCode, pinCodeStr.toStdString().c_str() );
    }

    return 0;
}

int MapSender::getImageWithWaiting( char *pinCode, QImage *image )
{
    uint waitMs = 100;
    QDateTime start = QDateTime::currentDateTimeUtc();
    QDateTime prevRequestTime = QDateTime::currentDateTimeUtc();
    QDateTime currentRequestTime = prevRequestTime;

    int status = getImage( pinCode, image );
    while ( status == EAGAIN ) {
        qApp->processEvents( QEventLoop::AllEvents, waitMs );

        currentRequestTime = QDateTime::currentDateTimeUtc();
        qint64 requestdeltaMs = prevRequestTime.msecsTo( currentRequestTime );
        if ( requestdeltaMs > 500 ) {
            prevRequestTime = currentRequestTime;
            status = getImage( pinCode, image );
        }

        QDateTime current = QDateTime::currentDateTimeUtc();
        auto totalDeltaMs = start.msecsTo( current );
        if ( totalDeltaMs > _timeout_ms )
            return ETIMEDOUT;
    }

    return status;
}

int MapSender::getImage( char *pinCode, QImage *image )
{
    QString requestUrl = _url + "/?&orderId=" + QString::number(_orderId) + "&pincode=" + QString(pinCode);
    QUrl url( requestUrl );
    QNetworkRequest request(url);

    QNetworkReply *reply = manager->get(request);
    waitForReplyFinished( reply, _timeout_ms );

    QVariant statusCodeAttribute = reply->attribute(QNetworkRequest::HttpStatusCodeAttribute);
    bool ok = false;
    int statusCode = statusCodeAttribute.toInt(&ok);
    if ( !ok || statusCode != GisHttpCodes::Ok ) {
        if ( statusCode == GisHttpCodes::IsProcessing ) {
            return EAGAIN;
        }

        qDebug() << "statusCode" << statusCode;
        return EFAULT;
    }

    if ( !reply->isFinished() )
        return EFAULT;

    QVariant format_hdr = reply->header( QNetworkRequest::ContentTypeHeader );
    QString format_str = format_hdr.toString();
    QString image_format = format_str.remove( "image/" );

    QByteArray ba = reply->readAll();
    image->loadFromData( ba, image_format.toLocal8Bit().data() );
    return 0;
}

void MapSender::waitForReplyFinished( QNetworkReply *reply, uint timeout_ms )
{
    uint waitMs = 100;
    bool isTimeoutEnabled = false;
    if ( timeout_ms > 0 )
        isTimeoutEnabled = true;

    QDateTime start = QDateTime::currentDateTimeUtc();
    qint64 totalDeltaMs = 0;

    while ( !reply->isFinished() ) {
        qApp->processEvents( QEventLoop::AllEvents, waitMs );

        if ( isTimeoutEnabled ) {
            QDateTime current = QDateTime::currentDateTimeUtc();
            totalDeltaMs = start.msecsTo( current );
            if ( totalDeltaMs > timeout_ms )
            {
                qDebug() << "Timeout" << totalDeltaMs;
                break;
            }
        }
    }
}
