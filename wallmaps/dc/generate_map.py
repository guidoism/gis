from pdfrw import PdfReader, PdfWriter, PageMerge
from pdfrw.buildxobj import ViewInfo
from kartograph import Kartograph
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape


# -85.7935 -85.5736
# 38.2387 38.2497

width_in_degrees = -85.6 - -85.8635
height_in_degrees = 38.7 - 38.2927

def squares(width, height):
    "Draws squares showing where this page should go"
    # down and then to the right
    #c = canvas.Canvas('index.pdf', bottomup=0, pagesize=landscape(letter))
    c = canvas.Canvas('index.pdf', bottomup=0, pagesize=letter)
    c.setFillGray(0.8)
    c.setStrokeGray(0.8)
    for ci in range(width):
        for cj in range(height):
            for i in range(width):
                for j in range(height):
                    x = i * 12 + 100
                    y = j * 22 + 100
                    c.rect(x, y, 10, 20, stroke=1,
                           fill=(1 if (ci, cj) == (i, j) else 0))
            c.showPage()
    c.save()
    return PdfReader('index.pdf')

k = Kartograph()
config = {
    "layers": {
        "roads": { "src": "gis.osm_roads_free_1.shp",
                   "attributes": { "name": "name" },
                   #"labeling": {"key": "name"}
        },
        "buildings": { "src": "gis.osm_buildings_a_free_1.shp" },
        "water": { "src": "gis.osm_water_a_free_1.shp" }
    },
    "bounds": {
        "mode": "bbox",
        "data": [-77.127222, 38.9955, -76.910215, 38.798990],
    },
    #"bounds": {
    #    "mode": "bbox",
        # "data": [-85.7935, 38.2387, -85.5736, 38.2497],

        # "data": [upper_left[0], upper_left[1], bottom_right[0], bottom_right[1]],
        # upper_left = (-85.6, 38.7)
        # bottom_right = (-85.8635, 38.2927)
 
        # [minLon, minLat, maxLon, maxLat]
    #    "data": [-85.84, 38.15, -85.6, 38.3] # 24 x 15 == 8 x 5
        # "data": [-85.87, 38.15, -85.6, 38.3] # 27 x 15 == 9 x 5 -- Failed!
        #"data": [-85.8635, 38.15, -85.6, 38.3] # 26.35 x 15
        #"data": [-85.8635, 38.2127, -85.6, 38.3]
        #"data": [-85.8635, 38.2127, -85.6, 38.4]
        #"data": [-85.8635, 38.2127, -85.6, 38.5]
        # "data": [-85.8635, 38.2127, -85.6, 38.7] # -big1
        # "data": [-85.8635, 38.2927, -85.6, 38.7]
    #},
    "export": {
	"width": 10000,
        #"prettyprint": True,
    }
}

# TODO: Add css
# Because I don't want to deal with getting everything else in python 3 right now
# I use subprocess, lame, I know.

k.generate(config, outfile='map.svg')
subprocess.call(['cairosvg', '-o', 'map.pdf', 'map.svg', '--unsafe'])

ipdf = PdfReader('map.pdf')
p = ipdf.pages[0]
pdf = PdfWriter()

# width_to_height_ratio = 1.3 

# 10 pages wide is 85"
# 2 pages down is 22"

# It's printing at 10.75" x 6.5"

width_pages = 8
height_pages = 5

index = squares(width_pages, height_pages)

width_fraction = 1 / float(width_pages)
height_fraction = 1 / float(height_pages)

n = 0
for left in [i/float(width_pages) for i in range(0, width_pages)]:
    for top in [i/float(height_pages) for i in range(0, height_pages)]:
        # 'viewrect=<left>,<top>,<width>,<height>'
        v = ViewInfo("viewrect=%f,%f,%f,%f" % \
                     (left, top, width_fraction, height_fraction))
        print "viewrect=%f,%f,%f,%f" % (left, top, width_fraction, height_fraction)
        pdf.addpage(PageMerge().add(p, viewinfo=v).render())
        pdf.addpage(index.pages[n])
        n += 1
pdf.write('mymap-transformed.pdf')

