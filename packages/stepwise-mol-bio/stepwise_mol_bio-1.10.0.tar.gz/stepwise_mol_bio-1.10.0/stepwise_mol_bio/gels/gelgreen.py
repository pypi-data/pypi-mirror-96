#!/usr/bin/env python3

import stepwise, appcli, autoprop
from appcli import Key, DocoptConfig
from _biotium import Biotium
from laser_scanner import LaserScanner

@autoprop
class GelGreen(Biotium):
    """\
Stain nucleic acids using GelGreen.

GelGreen is a sensitive, stable and environmentally safe green fluorescent 
nucleic acid dye specifically designed for gel staining.  GelGreen has UV 
absorption between 250 nm and 300 nm and a strong absorption peak centered 
around 500 nm.  Thus, GelGreen is compatible with either a 254 nm UV 
transilluminator or a gel reader equipped with visible light excitation (such 
as a 488 nm laser-based gel scanner or a Dark Reader).  

Usage:
    gelgreen [-r] [-I] [-a]

Options:
    -r --fluorescent
        Image the gel using a 488 nm fluorescence laser scanner, rather than
        a UV transilluminator.
        
    -I --no-imaging
        Don't include the imaging step in the protocol (e.g. so you can provide 
        a customized alternative).

    -a --attach-pdf
        Attach the manufacturer's protocol to this one, so that both will be 
        printed out by `stepwise go`.
"""

    product = 'GelGreen'
    uv_wavelength = '254'
    attachment = 'biotium_gelgreen.pdf'
    image_type = appcli.param(
            Key(DocoptConfig, '--fluorescent', cast=lambda x: 'fluor'),
            Key(DocoptConfig, '--no-imaging', cast=lambda x: None),
            default='uv',
    )

    def get_imaging_protocols(self):
        return {
                **super().imaging_protocols,
                'fluor': self.get_fluorescent_imaging,
        }

    def get_fluorescent_imaging(self):
        scan = LaserScanner.from_laser_filter_pair(488, '518BP22')
        return scan.protocol

if __name__ == '__main__':
    GelGreen.main()
