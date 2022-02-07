/*
 * (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
 */

/*************************************************/
/*                GIS Map Server                 */
/*            Server interface header            */
/*************************************************/


#ifndef GISMAPSENDER_H
#define GISMAPSENDER_H

#ifdef __cplusplus

#include <QImage>
#include <QString>


typedef enum {
    Ok = 200,
    IsProcessing = 202,
    InvalidParameters = 400,
    Timeout = 408,
    Done = 410,
    NoMemory = 418,
    RenderFailed = 500,
    RequestFailed = 520
} GisHttpCodes;

QString gis_map_server_get_error_message( GisHttpCodes statusCode );

/*
 * Make a request to the gis-map-server
 *
 * format -png, jpeg, bmp
 */
int gis_map_server_request_map(const char *server_url, double lat, double lon, int scale, int w, int h, const char *format, uint* orderId, char *pinCode );

int gis_map_server_get_image(const char *server_url, int orderId, char *pinCode, QImage *image );

#endif

#endif // GISMAPSENDER_H
