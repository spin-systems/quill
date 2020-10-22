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

- One nice feature of GitLab (which at the time of writing GitHub doesn't
  provide to my knowledge) is that these repos can all be private, and only
  the static site will be hosted publicly (specified in 'Settings' > 'General')

To clone a given repo (testing has all been with SSH URLs), there is the `clone` function,
and subsequently the namespace can be `refresh`ed to reflect the new addition (this is
done automatically within the `clone` function).

```py
>>> qu.ns
{}
>>> qu.clone(qu.ssm.repos_df.git_url[0], "spin.systems")
Cloning into 'spin.systems'...
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (6/6), done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 236 (delta 1), reused 0 (delta 0), pack-reused 230
Receiving objects: 100% (236/236), 34.16 KiB | 210.00 KiB/s, done.
Resolving deltas: 100% (123/123), done.
>>> qu.ns
{'spin.systems': 'https://gitlab.com/spin-systems/spin-systems.gitlab.io'}
```

Lastly, the entire manifest of repos can be sourced from `ssm` and `clone`d into the
`ns_path` directory.

```py
qu.source_manifest()
```

For now, if the directory named as the `domain` entry of the row in the `ssm.repos_df`
table exists, it will simply not touch it. If it doesn't exist, it will try to clone it.

Et voila the namespace now contains all the repos (stored in the sibling `ss` directory)

```py
>>> pprint(qu.ns)
{'arb': 'https://gitlab.com/spin-arb/spin-arb.gitlab.io',
 'arc': 'https://gitlab.com/appendens/appendens.gitlab.io',
 'cal': 'https://gitlab.com/qu-cal/qu-cal.gitlab.io',
 'conf': 'https://gitlab.com/qu-conf/qu-conf.gitlab.io',
 'doc': 'https://gitlab.com/spin-doc/spin-doc.gitlab.io',
 'erg': 'https://gitlab.com/spin-erg/spin-erg.gitlab.io',
 'labs': 'https://gitlab.com/qu-labs/qu-labs.gitlab.io',
 'log': 'https://gitlab.com/spin-log/spin-log.gitlab.io',
 'noto': 'https://gitlab.com/qu-noto/qu-noto.gitlab.io',
 'ocu': 'https://gitlab.com/naiveoculus/naiveoculus.gitlab.io',
 'opt': 'https://gitlab.com/spin-opt/spin-opt.gitlab.io',
 'plot': 'https://gitlab.com/qu-plot/qu-plot.gitlab.io',
 'poll': 'https://gitlab.com/qu-poll/qu-poll.gitlab.io',
 'pore': 'https://gitlab.com/qu-pore/qu-pore.gitlab.io',
 'qrx': 'https://gitlab.com/qu-arx/qu-arx.gitlab.io',
 'reed': 'https://gitlab.com/qu-reed/qu-reed.gitlab.io',
 'spin.systems': 'https://gitlab.com/spin-systems/spin-systems.gitlab.io'}
```

At the end of `source_manifest`, the `ssm.repos_df` DataFrame is updated with a column `local`
indicating whether each domain in the manifest is now in the `ns` namespace (i.e. whether a
local repo has been created), via the `check_manifest` method which `ssm`'s `MMD` class inherits
from the `Doc` class.

- This `update_manifest` method will be expanded to supplement the `repos_df` DataFrame with
  other information worth knowing to do with the `git` status of the repo in question, for those
  which are locally available. This ensures no unnecessary computation is done before the extra
  information is needed.

```py
>>> ssm.repos_df
          domain     repo_name priority                                                 git_url  local
0   spin.systems  spin-systems        4  git@gitlab.com:spin-systems/spin-systems.gitlab.io.git   True
1            cal        qu-cal        3              git@gitlab.com:qu-cal/qu-cal.gitlab.io.git   True
2            log      spin-log        4          git@gitlab.com:spin-log/spin-log.gitlab.io.git   True
3           conf       qu-conf        4            git@gitlab.com:qu-conf/qu-conf.gitlab.io.git   True
4           pore       qu-pore        2            git@gitlab.com:qu-pore/qu-pore.gitlab.io.git   True
5            ocu   naiveoculus        4    git@gitlab.com:naiveoculus/naiveoculus.gitlab.io.git   True
6            arc     appendens        4        git@gitlab.com:appendens/appendens.gitlab.io.git   True
7            qrx        qu-arx        4              git@gitlab.com:qu-arx/qu-arx.gitlab.io.git   True
8            erg      spin-erg        1          git@gitlab.com:spin-erg/spin-erg.gitlab.io.git   True
9            opt      spin-opt        1          git@gitlab.com:spin-opt/spin-opt.gitlab.io.git   True
10          poll       qu-poll        2            git@gitlab.com:qu-poll/qu-poll.gitlab.io.git   True
11           arb      spin-arb        1          git@gitlab.com:spin-arb/spin-arb.gitlab.io.git   True
12          reed       qu-reed        3            git@gitlab.com:qu-reed/qu-reed.gitlab.io.git   True
13          noto       qu-noto        2            git@gitlab.com:qu-noto/qu-noto.gitlab.io.git   True
14          plot       qu-plot        1            git@gitlab.com:qu-plot/qu-plot.gitlab.io.git   True
15           doc      spin-doc        2          git@gitlab.com:spin-doc/spin-doc.gitlab.io.git   True
16          labs       qu-labs        1            git@gitlab.com:qu-labs/qu-labs.gitlab.io.git   True
```

## TODO

- The next step is to read the CI YAML as the 'layout' for each site
  - check it's valid (given a predetermined expected format for the YAML configs)
- We can now use this to generate a nice README for the spin.systems superrepo(?) corresponding to
  a nicely formatted markdown doc of the info in this DataFrame.
  - For this, we reuse the original list representation, with the apex domain as the header,
    and convert it to markdown to present it in the conventional format
- I would also like to keep track of the `git status` of each repo in the same repo
  - This will involve making the `repos_df` __always__ have the `local` column, 
    for which I'll have to abstract away the call at the end of `fold`⠶`git`⠶`source_manifest`
- A next step could be a class representing the state of the websites, which can
  then be cross-referenced against the `repos_df` (but the goal is not to entirely Python-ise
  the site development, just the management of key aspects to do with the version control on disk)
