# -*- coding: utf-8 -*-
from optparse import OptionParser

import settings
from options import DOption
from song.reader import SongReader
from song.structure import scheme

parser = OptionParser(usage="usage: %prog options", option_class=DOption)
parser.add_option('-x', "--song", action="store", dest="xml", help="XML Song file")
parser.add_option('-s', "--size", action="store", type='dimension', dest="size", help="Output size", default=(640, 480))

if __name__ == '__main__':
    options, args = parser.parse_args()

    harmony = SongReader(options.xml)
    structure = harmony.getStructureAs(scheme.Structure)

    W, H = options.size
    wH = H / settings.WAVE_FORM_PART

    imStructure = structure.drawStructure(W, (H-wH) * 2, W/2)
    structureFilename = options.xml.rsplit('.', 1)[0] + '.structure.png'
    f = open(structureFilename, 'wb')
    imStructure.save(f, 'PNG')
    del imStructure
    f.close()
