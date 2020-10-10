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
Parsed MMD file (Document of 1 block)
>>> qu.ssm.doc
Document of 1 block
>>> qu.ssm.doc.blocks
[Block of 17 nodes]
>>> qu.ssm.doc.blocks[0]
Block of 17 nodes
>>> qu.ssm.doc.blocks[0].nodes
[-spin.systems:, -:cal, -,:log, -,:conf, -,:pore, -,:ocu, -,:arc, -,:qrx, -,:erg, -,:opt, -,:poll, -,:arb, -,:reed, -,:noto, -,:plot, -,:doc, -,:labs]
>>> qu.ssm.doc.blocks[0].nodes[0]
-spin.systems:
>>> n = qu.ssm.doc.blocks[0].nodes[0]
>>> n.
n.contents  n.prefix    n.suffix    
>>> n.prefix
<Prefix.PlainNode: ('-',)>
>>> n.contents
'spin.systems'
```
