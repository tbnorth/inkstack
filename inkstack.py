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
    for layer in layers:
        layer.set('style', 'display:%s' % ('inline' if visible else 'none'))

def export(dom, prefix, name):
    with open('tmp.svg', 'w') as out:
        out.write(etree.tostring(dom))
    filename = "%s_%s.png" % (prefix, name.replace('+', ''))
    cmd = "inkscape --export-png %s --export-area-page tmp.svg" % filename
    os.system(cmd)

def main():
    dom = etree.parse(open(sys.argv[1]))
    prefix = sys.argv[2]
    layers = dom.xpath("//*[@inkscape:groupmode='layer']", namespaces=NS)
    names = []
    for layer in layers:
        name = layer.xpath(".//@inkscape:label", namespaces=NS)[0]
        names.append(name)

    base = None
    for layer_i, (layer, name) in enumerate(zip(layers, names)):
        print(name)
        layers_visible(layers, False)
        if name.startswith('_'):
            print("Ignoring '_' layer")
            continue
        if not name.startswith('+'):
            base = layer_i
        layers_visible(layers[base:layer_i+1], True)
        export(dom, prefix, name)

if __name__ == '__main__':
    main()
