# quill

- `qu`⠶`scan`: Read `.mmd` files (using `lever`)
- `qu`⠶`manifest`: Read `spin.systems` configuration
- `qu`⠶`fold`: Manage `*.spin.systems` subdomains

## Usage memo

- Requires directory of static site repositories at
  location specified in [`spin.ini`](spin.ini) (by default
  this is as a sibling directory `../ss/`), containing
  a file `manifest.mmd` beginning with the apex domain and
  immediately followed by a subdomain list.

Below is a demo of accessing the `spin.systems` manifest file
(`ssm`) which implements the `MMD` class, subclassing `Doc`,
which parses the file contents in a structured way (specifically,
as a list of colon-separated values).

```py
>>> from pprint import pprint
>>> from qu import ssm
>>> ssm
Parsed MMD file (Document of 1 block, containing 1 list)
>>> ssm.list
Headered list with 16 items
>>> pprint(ssm.list.all_nodes)
[-spin.systems:spin-systems:,
 -:cal:qu-cal,
 -,:log:spin-log,
 -,:conf:qu-conf,
 -,:pore:qu-pore,
 -,:ocu:naiveoculus,
 -,:arc:appendens,
 -,:qrx:qu-arx,
 -,:erg:spin-erg,
 -,:opt:spin-opt,
 -,:poll:qu-poll,
 -,:arb:spin-arb,
 -,:reed:qu-reed,
 -,:noto:qu-noto,
 -,:plot:qu-plot,
 -,:doc:spin-doc,
 -,:labs:qu-labs]
>>> pprint(ssm.list.nodes)
[-:cal:qu-cal,
 -,:log:spin-log,
 -,:conf:qu-conf,
 -,:pore:qu-pore,
 -,:ocu:naiveoculus,
 -,:arc:appendens,
 -,:qrx:qu-arx,
 -,:erg:spin-erg,
 -,:opt:spin-opt,
 -,:poll:qu-poll,
 -,:arb:spin-arb,
 -,:reed:qu-reed,
 -,:noto:qu-noto,
 -,:plot:qu-plot,
 -,:doc:spin-doc,
 -,:labs:qu-labs]
>>> ssm.list.header
-spin.systems:spin-systems:
>>> ssm.list.header.parts
['spin.systems', 'spin-systems']
>>> ssm.list.nodes[0].parts
['cal', 'qu-cal']
>>> ssm.list.nodes[1].parts
['log', 'spin-log']
>>> ssm.list.nodes[2].parts
['conf', 'qu-conf']
>>> pprint(ssm.all_parts)
[['spin.systems', 'spin-systems'],
 ['cal', 'qu-cal'],
 ['log', 'spin-log'],
 ['conf', 'qu-conf'],
 ['pore', 'qu-pore'],
 ['ocu', 'naiveoculus'],
 ['arc', 'appendens'],
 ['qrx', 'qu-arx'],
 ['erg', 'spin-erg'],
 ['opt', 'spin-opt'],
 ['poll', 'qu-poll'],
 ['arb', 'spin-arb'],
 ['reed', 'qu-reed'],
 ['noto', 'qu-noto'],
 ['plot', 'qu-plot'],
 ['doc', 'spin-doc'],
 ['labs', 'qu-labs']]
```
