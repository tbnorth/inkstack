"""
inkstack.py - export inkscape layers to images

layers starting with '_' are ignored
layers starting with '+' are overlayed

Terry Brown, terrynbrown@gmail.com, Fri Jun 29 16:42:03 2018
"""

import os
import sys

from lxml import etree

NS = {'inkscape': "http://www.inkscape.org/namespaces/inkscape"}

def layers_visible(layers, visible):
    """
    layers_visible - set each layer in layers to be (in)visible.
    Modifies layers.

    Args:
        layers (list): list of Etree elements representing layers
        visible (bool): set to (in)visible
    """

    for layer in layers:
        layer.set('style', 'display:%s' % ('inline' if visible else 'none'))

def export(dom, filename):
    """
    export - Export the SVG DOM to a file

    Args:
        dom (Etree DOM): DOM to export
        filename (str): path to export to
    """
    with open('_inkstack.tmp.svg', 'w') as out:
        out.write(etree.tostring(dom))
    cmd = "inkscape --export-png %s --export-area-page _inkstack.tmp.svg" % filename
    os.system(cmd)
    os.unlink('_inkstack.tmp.svg')

def main():
    """usage: python inkstack.py SVG_FILE [PREFIX]

    Export layers in Inkscape SVG_FILE to individual images.

    Output files are names <prefix>_NN_<layer name>.png.
    <prefix> is either the base name of the SVG file, or the
    supplied prefix, if any.  <layer name> comes from the
    layer names displayed in Inkscape.
    """

    dom = etree.parse(open(sys.argv[1]))
    try:
        prefix = sys.argv[2]
    except IndexError:
        prefix = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    layers = dom.xpath("//*[@inkscape:groupmode='layer']", namespaces=NS)
    names = []
    for layer in layers:
        name = layer.xpath(".//@inkscape:label", namespaces=NS)[0]
        names.append(name)

    base = None
    exports = 0
    for layer_i, (layer, name) in enumerate(zip(layers, names)):
        print(name)
        layers_visible(layers, False)
        if name.startswith('_'):
            print("Ignoring '_' layer")
            continue
        if not name.startswith('+'):
            base = layer_i
        layers_visible(layers[base:layer_i+1], True)
        filename = "%s_%02d_%s.png" % (prefix, exports, name.replace('+', ''))
        export(dom, filename)
        exports += 1


if __name__ == '__main__':
    main()
