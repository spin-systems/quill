# quill

- `qu`⠶`scan`: Read `.mmd` files (using `lever`)
- `qu`⠶`manifest`: Read `spin.systems` configuration
- `qu`⠶`fold`: Manage `*.spin.systems` subdomains

## Usage memo

- Requires directory of `spin.systems` static sites at
  location specified in [`spin.ini`](spin.ini) (by default
  this is as a sibling directory `../ss/`).

```py
>>> from qu import quill
>>> quill.ssm
Block of 17 nodes
>>> quill.ssm.nodes[0].contents
'spin.systems'
```
