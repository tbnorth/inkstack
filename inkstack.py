"""
inkstack.py - export inkscape layers to images

layers starting with '_' are ignored
layers starting with '+' are overlayed

Terry Brown, terrynbrown@gmail.com, Fri Jun 29 16:42:03 2018
"""

import argparse
import os

from lxml import etree

NS = {'inkscape': "http://www.inkscape.org/namespaces/inkscape"}

def make_parser():
    """Command line options parser"""

    parser = argparse.ArgumentParser(
        description="""Export layers in Inkscape SVG_FILE to individual images.
        Output files are names <prefix>_NN_<layer name>.png.
        <prefix> is either the base name of the SVG file, or the
        supplied prefix, if any.  <layer name> comes from the
        layer names displayed in Inkscape.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--prefix", help="Prefix for exported image file names")

    parser.add_argument('svg_file', help="Inkscape SVG file to process")
    parser.add_argument('out_path', help="Path for output files", nargs='?')

    return parser

def get_options(args=None):
    """
    get_options - use argparse to parse args, and return a
    argparse.Namespace, possibly with some changes / expansions /
    validatations.

    Client code should call this method with args as per sys.argv[1:],
    rather than calling make_parser() directly.

    Args:
        args ([str]): arguments to parse

    Returns:
        argparse.Namespace: options with modifications / validations
    """
    opt = make_parser().parse_args(args)

    # modifications / validations go here
    opt.out_path = opt.out_path or '.'
    opt.prefix = opt.prefix or os.path.splitext(os.path.basename(opt.svg_file))[0]
    return opt

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
    tmp_file = os.path.join(os.path.dirname(filename), '_inkstack.tmp.svg')
    with open(tmp_file, 'w') as out:
        out.write(etree.tostring(dom))
    cmd = 'inkscape --export-png "%s" --export-area-page "%s"' % (filename, tmp_file)
    os.system(cmd)
    os.unlink(tmp_file)
def main():
    """Export layers in Inkscape SVG_FILE to individual images."""

    opt = get_options()

    dom = etree.parse(open(opt.svg_file))

    layers = dom.xpath("//*[@inkscape:groupmode='layer']", namespaces=NS)
    names = []
    for layer in layers:
        name = layer.xpath(".//@inkscape:label", namespaces=NS)[0]
        names.append(name)

    base = None
    exports = []
    for layer_i, (layer, name) in enumerate(zip(layers, names)):
        print(name)
        layers_visible(layers, False)
        if name.startswith('_'):
            print("Ignoring '_' layer")
            continue
        if not name.startswith('+'):
            base = layer_i
        layers_visible(layers[base:layer_i+1], True)
        filename = "%s_%02d_%s.png" % (opt.prefix, len(exports), name.replace('+', ''))
        filename = os.path.join(opt.out_path, filename)
        export(dom, filename)
        exports.append(filename)
    print()
    for filename in exports:
        print("![%s](%s)" % (filename.split('_', 2)[-1][:-4], filename))





if __name__ == '__main__':
    main()
