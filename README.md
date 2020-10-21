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
>>> import pandas as pd
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
>>> ssm.all_parts.as_df()
          domain     repo_name priority
0   spin.systems  spin-systems        4
1            cal        qu-cal        3
2            log      spin-log        4
3           conf       qu-conf        4
4           pore       qu-pore        2
5            ocu   naiveoculus        4
6            arc     appendens        4
7            qrx        qu-arx        4
8            erg      spin-erg        1
9            opt      spin-opt        1
10          poll       qu-poll        2
11           arb      spin-arb        1
12          reed       qu-reed        3
13          noto       qu-noto        2
14          plot       qu-plot        1
15           doc      spin-doc        2
16          labs       qu-labs        1
```

The numeric entry is a rating of my recollection and/or
resolve of the purpose for each of these projects,
roughly interpretable as

- 1. little
- 2. some
- 3. fair
- 4. strong


