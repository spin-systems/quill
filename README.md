# quill

- `qu`⠶`scan`: Read `.mmd` files (using `lever`)
- `qu`⠶`manifest`: Read `spin.systems` configuration
- `qu`⠶`fold`: Manage `*.spin.systems` subdomains

## Usage memo

Load the `quill` module:

```sh
python -ic "from qu import quill"
```
⇣
```STDOUT
>>> mmd = quill.mmd(manifest)
>>> mmd.nodes
[-spin.systems:, -:cal, -,:log, -,:conf, -,:pore, -,:ocu, -,:arc, -,:qrx, -,:erg, -,:opt, -,:poll, -,:arb, -,:reed, -,:noto, -,:plot, -,:doc, -,:labs]
>>> mmd.nodes[0]
-spin.systems:
>>> mmd.nodes[0].prefix
<Prefix.PlainNode: ('-',)>
>>> mmd.nodes[0].suffix
<Suffix.InitList: ':'>
>>> mmd.nodes[0].contents
'spin.systems'
```
