#!/bin/sh
if [ -z "$GIS_ROOT" ]; then
    export GIS_ROOT=/opt/gis/
fi
export LD_LIBRARY_PATH=$GIS_ROOT/lib:$LD_LIBRARY_PATH
export PATH=$GIS_ROOT/bin:$GIS_ROOT/sbin:$PATH
export GIS_DEBUG_LEVEL=2
export GIS_DISABLE_VERIFIER=y

slay -f gis-core
gis-core -dsxf-local,sync=soft -ds57-local,sync=soft &
waitfor /dev/gis_core 300

echo 'Starting server'
$GIS_ROOT/data/resources/gis-map-server/server.py $GIS_ROOT/data/config/gis-map-server.conf
