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
>>> import qu
>>> qu.ssm
Parsed MMD file (Document of 1 block, containing 1 list)
>>> qu.ssm.doc
Document of 1 block, containing 1 list
>>> qu.ssm.doc.blocks
[Block of 17 nodes]
>>> from pprint import pprint
>>> pprint(qu.ssm.doc.blocks[0].nodes)
[-spin.systems:,
 -:cal,
 -,:log,
 -,:conf,
 -,:pore,
 -,:ocu,
 -,:arc,
 -,:qrx,
 -,:erg,
 -,:opt,
 -,:poll,
 -,:arb,
 -,:reed,
 -,:noto,
 -,:plot,
 -,:doc,
 -,:labs]
>>> qu.ssm.doc.lists
[Headered list with 16 items]
>>> qu.ssm.doc.lists[0].nodes
[-:cal, -,:log, -,:conf, -,:pore, -,:ocu, -,:arc, -,:qrx, -,:erg, -,:opt, -,:poll, -,:arb, -,:reed, -,:noto, -,:plot, -,:doc, -,:labs]
>>> qu.ssm.doc.lists[0].header
-spin.systems:
>>> qu.ssm.doc.lists[0].all_nodes
[-spin.systems:, -:cal, -,:log, -,:conf, -,:pore, -,:ocu, -,:arc, -,:qrx, -,:erg, -,:opt, -,:poll, -,:arb, -,:reed, -,:noto, -,:plot, -,:doc, -,:labs]
```
