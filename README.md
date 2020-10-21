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
[-spin.systems:spin-systems:4:,
 -:cal:qu-cal:3,
 -,:log:spin-log:4,
 -,:conf:qu-conf:4,
 -,:pore:qu-pore:2,
 -,:ocu:naiveoculus:4,
 -,:arc:appendens:4,
 -,:qrx:qu-arx:4,
 -,:erg:spin-erg:1,
 -,:opt:spin-opt:1,
 -,:poll:qu-poll:2,
 -,:arb:spin-arb:1,
 -,:reed:qu-reed:3,
 -,:noto:qu-noto:2,
 -,:plot:qu-plot:1,
 -,:doc:spin-doc:2,
 -,:labs:qu-labs:1]
>>> pprint(ssm.list.nodes)
[-:cal:qu-cal:3,
 -,:log:spin-log:4,
 -,:conf:qu-conf:4,
 -,:pore:qu-pore:2,
 -,:ocu:naiveoculus:4,
 -,:arc:appendens:4,
 -,:qrx:qu-arx:4,
 -,:erg:spin-erg:1,
 -,:opt:spin-opt:1,
 -,:poll:qu-poll:2,
 -,:arb:spin-arb:1,
 -,:reed:qu-reed:3,
 -,:noto:qu-noto:2,
 -,:plot:qu-plot:1,
 -,:doc:spin-doc:2,
 -,:labs:qu-labs:1]
>>> ssm.list.header
-spin.systems:spin-systems:
>>> ssm.list.header.parts
['spin.systems', 'spin-systems', '4']
>>> ssm.list.nodes[0].parts
['cal', 'qu-cal', '3']
>>> ssm.list.nodes[1].parts
['log', 'spin-log', '4']
>>> ssm.list.nodes[2].parts
['conf', 'qu-conf', '4']
>>> pprint(ssm.all_parts)
[['spin.systems', 'spin-systems', '4'],
 ['cal', 'qu-cal', '3'],
 ['log', 'spin-log', '4'],
 ['conf', 'qu-conf', '4'],
 ['pore', 'qu-pore', '2'],
 ['ocu', 'naiveoculus', '4'],
 ['arc', 'appendens', '4'],
 ['qrx', 'qu-arx', '4'],
 ['erg', 'spin-erg', '1'],
 ['opt', 'spin-opt', '1'],
 ['poll', 'qu-poll', '2'],
 ['arb', 'spin-arb', '1'],
 ['reed', 'qu-reed', '3'],
 ['noto', 'qu-noto', '2'],
 ['plot', 'qu-plot', '1'],
 ['doc', 'spin-doc', '2'],
 ['labs', 'qu-labs', '1']]
>>> ssm.as_df()
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

The numeric entry is a rating of my recollection of and/or
resolve for the purpose of each of these projects,
roughly interpretable as

1. little
2. some
3. fair
4. strong

This is just for review purposes currently, and any further info can be added as long
as all the lines ("nodes") have the same number of colon-separated values.

The manifest is parsed in [`manifest`⠶`parsing`](src/quill/manifest/parsing.py) by
`parse_man_node` which is wrapped 

```py
ssm.repos
```

Which will print out the repos' git addresses for each CNAME:

```STDOUT
('spin.systems', 'git@gitlab.com:spin-systems/spin-systems.gitlab.io.git')
('cal', 'git@gitlab.com:qu-cal/qu-cal.gitlab.io.git')
('log', 'git@gitlab.com:spin-log/spin-log.gitlab.io.git')
('conf', 'git@gitlab.com:qu-conf/qu-conf.gitlab.io.git')
('pore', 'git@gitlab.com:qu-pore/qu-pore.gitlab.io.git')
('ocu', 'git@gitlab.com:naiveoculus/naiveoculus.gitlab.io.git')
('arc', 'git@gitlab.com:appendens/appendens.gitlab.io.git')
('qrx', 'git@gitlab.com:qu-arx/qu-arx.gitlab.io.git')
('erg', 'git@gitlab.com:spin-erg/spin-erg.gitlab.io.git')
('opt', 'git@gitlab.com:spin-opt/spin-opt.gitlab.io.git')
('poll', 'git@gitlab.com:qu-poll/qu-poll.gitlab.io.git')
('arb', 'git@gitlab.com:spin-arb/spin-arb.gitlab.io.git')
('reed', 'git@gitlab.com:qu-reed/qu-reed.gitlab.io.git')
('noto', 'git@gitlab.com:qu-noto/qu-noto.gitlab.io.git')
('plot', 'git@gitlab.com:qu-plot/qu-plot.gitlab.io.git')
('doc', 'git@gitlab.com:spin-doc/spin-doc.gitlab.io.git')
('labs', 'git@gitlab.com:qu-labs/qu-labs.gitlab.io.git')
```

or we can get them as a DataFrame

```py
ssm.repos_df
```
⇣
```STDOUT
          domain     repo_name priority                                                 git_url
0   spin.systems  spin-systems        4  git@gitlab.com:spin-systems/spin-systems.gitlab.io.git
1            cal        qu-cal        3              git@gitlab.com:qu-cal/qu-cal.gitlab.io.git
2            log      spin-log        4          git@gitlab.com:spin-log/spin-log.gitlab.io.git
3           conf       qu-conf        4            git@gitlab.com:qu-conf/qu-conf.gitlab.io.git
4           pore       qu-pore        2            git@gitlab.com:qu-pore/qu-pore.gitlab.io.git
5            ocu   naiveoculus        4    git@gitlab.com:naiveoculus/naiveoculus.gitlab.io.git
6            arc     appendens        4        git@gitlab.com:appendens/appendens.gitlab.io.git
7            qrx        qu-arx        4              git@gitlab.com:qu-arx/qu-arx.gitlab.io.git
8            erg      spin-erg        1          git@gitlab.com:spin-erg/spin-erg.gitlab.io.git
9            opt      spin-opt        1          git@gitlab.com:spin-opt/spin-opt.gitlab.io.git
10          poll       qu-poll        2            git@gitlab.com:qu-poll/qu-poll.gitlab.io.git
11           arb      spin-arb        1          git@gitlab.com:spin-arb/spin-arb.gitlab.io.git
12          reed       qu-reed        3            git@gitlab.com:qu-reed/qu-reed.gitlab.io.git
13          noto       qu-noto        2            git@gitlab.com:qu-noto/qu-noto.gitlab.io.git
14          plot       qu-plot        1            git@gitlab.com:qu-plot/qu-plot.gitlab.io.git
15           doc      spin-doc        2          git@gitlab.com:spin-doc/spin-doc.gitlab.io.git
16          labs       qu-labs        1            git@gitlab.com:qu-labs/qu-labs.gitlab.io.git
```

Obviously this can then be used to clone the repositories locally
(or address them for any other `git`-related task)

One nice feature of GitLab (which at the time of writing GitHub doesn't
provide to my knowledge) is that these repos can all be private, and only
the static site will be hosted publicly (specified in 'Settings' > 'General')
