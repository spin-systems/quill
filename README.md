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

```py
>>> from pprint import pprint
>>> import qu
>>> qu.ssm
Parsed MMD file (Document of 1 block, containing 1 list)
>>> qu.ssm.doc
Document of 1 block, containing 1 list
>>> qu.ssm.doc.list
Headered list with 16 items
>>> pprint(qu.ssm.doc.list.all_nodes)
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
>>> pprint(qu.ssm.doc.list.nodes)
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
>>> qu.ssm.doc.list.header
-spin.systems:spin-systems:
>>> qu.ssm.doc.list.header.parts
['spin.systems', 'spin-systems']
>>> qu.ssm.doc.list.nodes[0].parts
['cal', 'qu-cal']
>>> qu.ssm.doc.list.nodes[1].parts
['log', 'spin-log']
>>> qu.ssm.doc.list.nodes[2].parts
['conf', 'qu-conf']
```
