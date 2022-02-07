/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

#include "gismapserver.h"
#include "mapsender.h"

QString gis_map_server_get_error_message( GisHttpCodes statusCode )
{
    switch ( statusCode ) {
    case GisHttpCodes::IsProcessing :
        return "Is processing";
    case GisHttpCodes::InvalidParameters :
        return "Invalid parameters";
    case GisHttpCodes::RequestFailed :
        return "Failed to request";
    case GisHttpCodes::Timeout :
        return "Timeout while processing request";
    case GisHttpCodes::RenderFailed :
        return "Failed to render request";
    case GisHttpCodes::Done :
        return "Request has been already obtained";
    case GisHttpCodes::Ok :
    default:
        return QString();
    }
}

int gis_map_server_request_map( const char *server_url,
                                double lat,
                                double lon,
                                int scale,
                                int w,
                                int h,
                                const char *format,
                                uint *orderId,
                                char *pinCode )
{
    if ( scale <= 0 || w <= 0 || h <= 0 || !orderId || !format )
        return EINVAL;

    uint timeout_ms = 30000;
    MapSender mapSender( QString(server_url), 0, timeout_ms );
    return mapSender.sendRequest( lat, lon, scale, w, h, format, orderId, pinCode );
}

int gis_map_server_get_image( const char *server_url, int orderId, char *pinCode, QImage *image )
{
    uint timeout_ms = 30000;
    MapSender mapSender( QString(server_url), orderId, timeout_ms );
    return mapSender.getImageWithWaiting( pinCode, image );
}
