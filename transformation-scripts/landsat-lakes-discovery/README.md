# Subset collections of Landsat 7-9

## Y tho?

For some stories to be told in the VEDA or EO Dashboard, we want to have nice pre-filtered collections of Landsat scenes that cover a specific AOI, so users can quickly browse through a long time series of nice imagery and visually see the changes the story intends to highlight.

We only need RGB and cross-mission physical consistency is not that important, so combined time series of Landsat-7 through 9 are fine.

## How to select the right path/row - manual method

To select the right scenes, we simply filter by two criteria

1. Low cloud cover (> 5% or so, depending on the local conditions)
2. A subset of WRS2 path/row combinations that cover the AOI

To process the data:

1. Grab the Landsat WRS2 scene outlines from <https://www.usgs.gov/media/files/landsat-wrs-2-scene-boundaries-kml-file>
2. Load it into QGIS
3. Zoom to your AOI / object of interest or get a geometry for it from somewhere
4. Find which features (path/row polygons) combined best cover the AOI
5. Put that into Microsoft Planetary Computer explorer and search for scenes
6. Export the Python code for that query
7. Run it and process the results in a notebook like the ones included here

This is not super elegant and could of course be automated, but it works fine for a small number of AOIs.
