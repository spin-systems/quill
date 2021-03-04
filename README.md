# quill

Quill is the "driver" for [spin.systems](https://spin.systems),
and packaged on PyPi as [ql](https://pypi.org/project/ql/).

A more detailed description of the package namespace can be found below,
but for everyday usage the commands needed are:

```py
import quill as ql
ql.ssm.check_manifest() # Check all component repos' status
ql.ssm.repos_df # print the summary dataframe
ql.fold.wire.standup() # build or rebuild any wire MMD documents as HTML pages
ql.remote_push_manifest() # Add/commit/push any dirty repos, triggering CI build
```

The last step is dependent on the manifest being updated: if changes are made, you need to
re-run `check_manifest` to update `ssm` ("spin.systems manifest"). This ensures that changes
do not 'go live' to the site unintentionally.

## Structure

- `ql`⠶`scan`: Read `.mmd` files
  - `scan`⠶`lever`: Parse `.mmd` file format
- `ql`⠶`manifest`: Read `spin.systems` configuration
- `ql`⠶`fold`: Manage `*.spin.systems` subdomains
  - `fold`⠶`address`: Manage subdomain address shorthand
  - `fold`⠶`wire`: Emit HTML websites from `.mmd` files

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
>>> from quill import ssm
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
>>> ql.ns
{}
>>> ql.clone(ql.ssm.repos_df.git_url[0], "spin.systems")
Cloning into 'spin.systems'...
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (6/6), done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 236 (delta 1), reused 0 (delta 0), pack-reused 230
Receiving objects: 100% (236/236), 34.16 KiB | 210.00 KiB/s, done.
Resolving deltas: 100% (123/123), done.
>>> ql.ns
{'spin.systems': 'https://gitlab.com/spin-systems/spin-systems.gitlab.io'}
```

Lastly, the entire manifest of repos can be sourced from `ssm` and `clone`d into the
`ns_path` directory.

```py
ql.source_manifest()
```

For now, if the directory named as the `domain` entry of the row in the `ssm.repos_df`
table exists, it will simply not touch it. If it doesn't exist, it will try to clone it.

Et voila the namespace now contains all the repos (stored in the sibling `ss` directory)

```py
>>> pprint(ql.ns)
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

The next thing we can do (having established that these are now cloned locally) is to read the CI YAML
as the 'layout' for each site, checking they're valid (according to the
[reference](https://docs.gitlab.com/ee/ci/yaml/#pages) on YAML configs for GitLab Pages)

```py
>>> manifests = ql.yaml_manifests(as_dicts=False)
>>> for k,m in manifests.items(): print(k, end="\t"); pprint(m)
spin.systems    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
cal     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
log     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
conf    SiteCI: PagesJob: {Stage.Deploy, Script <docs/>, Artifacts: paths=['public'], Only: branch=['master']}
pore    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
ocu     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
arc     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
qrx     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
erg     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
opt     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
poll    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
arb     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
reed    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
noto    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
plot    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
doc     SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
labs    SiteCI: PagesJob: {Stage.Deploy, Script <>, Artifacts: paths=['public'], Only: branch=['master']}
```

- The only notable thing here is that `conf` serves its site from the `docs/` subdirectory, the rest do not
- Obviously these could all be made more elaborate for less trivial scripts, this is a first draft showing basic functionality
- This setup is deliberately brittle, so any changes will need to be validated in the `fold.yaml_util` module,
  and so the library itself incorporates testing (simple `assert` statements based on a clear expected implementation)

The build directory can be set with `change_build_dir`, and using this I set all of the repos to
build from "site" (but this can be changed at a later date):

```py
for d in ql.alias_df.domain: ql.change_build_dir(d, "site")
```
⇣
```STDOUT
Moved build path for log from 'site' --> /home/louis/spin/ss/log/site
Created build path for ocu at /home/louis/spin/ss/ocu/site
Moved build path for arc from 'site' --> /home/louis/spin/ss/arc/site
Created build path for erg at /home/louis/spin/ss/erg/site
Created build path for opt at /home/louis/spin/ss/opt/site
Created build path for arb at /home/louis/spin/ss/arb/site
Created build path for doc at /home/louis/spin/ss/doc/site
Created build path for cal at /home/louis/spin/ss/cal/site
Moved build path for conf from 'docs' --> /home/louis/spin/ss/conf/site
Created build path for pore at /home/louis/spin/ss/pore/site
Created build path for qrx at /home/louis/spin/ss/qrx/site
Created build path for poll at /home/louis/spin/ss/poll/site
Created build path for reed at /home/louis/spin/ss/reed/site
Created build path for noto at /home/louis/spin/ss/noto/site
Created build path for plot at /home/louis/spin/ss/plot/site
Created build path for labs at /home/louis/spin/ss/labs/site
```

To commit these changes, I added some more functions to manage the `git` repos.
`ql.ssm.check_manifest()` now has a column referring to whether the working tree
is clean or has changes to tracked files not staged for commit.

The output will be something like this example (where the README in `arc`
was moved):

```py
ql.remote_push_manifest()
```
⇣
```STDERR
Skipping 'repo_dir=/home/louis/spin/ss/spin.systems' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/cal' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/log' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/conf' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/pore' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/ocu' (working tree clean)
Commit [repo_dir=/home/louis/spin/ss/arc] ⠶ Renamed site/README.md -> README.md
⇢ Pushing ⠶ origin
Skipping 'repo_dir=/home/louis/spin/ss/qrx' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/erg' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/opt' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/poll' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/arb' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/reed' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/noto' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/plot' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/doc' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/labs' (working tree clean)
```

Running `ssm.check_manifest()` again is required to update `ssm.repos_df`
(this is called rather than a property since it takes a little while
to calculate, and it'd slow down some operations which don't need it otherwise).

This `repos_df` dataframe is also useful for comparing whatever
other properties you might want to check, e.g. which have a README

```py
>>> df = ql.ssm.repos_df
>>> df["has_README"] = ["README.md" in [x.name for x in (ql.ns_path / d).iterdir()] for d in
>>> df.domain]
>>> df
          domain     repo_name priority  ... local  clean  has_README
0   spin.systems  spin-systems        4  ...  True   True       False
1            cal        qu-cal        3  ...  True   True       False
2            log      spin-log        4  ...  True   True        True
3           conf       qu-conf        4  ...  True   True        True
4           pore       qu-pore        2  ...  True   True       False
5            ocu   naiveoculus        4  ...  True   True       False
6            arc     appendens        4  ...  True   True        True
7            qrx        qu-arx        4  ...  True   True       False
8            erg      spin-erg        1  ...  True   True       False
9            opt      spin-opt        1  ...  True   True       False
10          poll       qu-poll        2  ...  True   True       False
11           arb      spin-arb        1  ...  True   True       False
12          reed       qu-reed        3  ...  True   True       False
13          noto       qu-noto        2  ...  True   True       False
14          plot       qu-plot        1  ...  True   True        True
15           doc      spin-doc        2  ...  True   True       False
16          labs       qu-labs        1  ...  True   True       False
```

Obviously this is the kind of thing to then follow up manually,
but it helps to have programmatic ways to view the set of directories.

If after reviewing `ssm.repos_df` you want to push, you can do so
either with an automated commit message or by passing it as the `commit_msg`
argument to `remote_push_manifest` (which will reuse the same commit message
if multiple repos are not clean).

```py
>>> ql.ssm.check_manifest()
>>> ql.ssm.repos_df
          domain     repo_name priority                                            git_url  local  clean
0   spin.systems  spin-systems        4  git@gitlab.com:spin-systems/spin-systems.gitla...   True   True
1            cal        qu-cal        3         git@gitlab.com:qu-cal/qu-cal.gitlab.io.git   True   True
2            log      spin-log        4     git@gitlab.com:spin-log/spin-log.gitlab.io.git   True   True
3           conf       qu-conf        4       git@gitlab.com:qu-conf/qu-conf.gitlab.io.git   True   True
4           pore       qu-pore        2       git@gitlab.com:qu-pore/qu-pore.gitlab.io.git   True   True
5            ocu   naiveoculus        4  git@gitlab.com:naiveoculus/naiveoculus.gitlab....   True   True
6            arc     appendens        4   git@gitlab.com:appendens/appendens.gitlab.io.git   True   True
7            qrx        qu-arx        4         git@gitlab.com:qu-arx/qu-arx.gitlab.io.git   True   True
8            erg      spin-erg        1     git@gitlab.com:spin-erg/spin-erg.gitlab.io.git   True   True
9            opt      spin-opt        1     git@gitlab.com:spin-opt/spin-opt.gitlab.io.git   True   True
10          poll       qu-poll        2       git@gitlab.com:qu-poll/qu-poll.gitlab.io.git   True  False
11           arb      spin-arb        1     git@gitlab.com:spin-arb/spin-arb.gitlab.io.git   True   True
12          reed       qu-reed        3       git@gitlab.com:qu-reed/qu-reed.gitlab.io.git   True   True
13          noto       qu-noto        2       git@gitlab.com:qu-noto/qu-noto.gitlab.io.git   True   True
14          plot       qu-plot        1       git@gitlab.com:qu-plot/qu-plot.gitlab.io.git   True   True
15           doc      spin-doc        2     git@gitlab.com:spin-doc/spin-doc.gitlab.io.git   True   True
16          labs       qu-labs        1       git@gitlab.com:qu-labs/qu-labs.gitlab.io.git   True   True
```

E.g. here `poll` has changes locally to be pushed (I added the first draft of a parliamentary
transcript), so I add (`all`) and push the changes to the [live website] repo

- I can manually go in and check the `git diff` beforehand if I want

```py
>>> ql.remote_push_manifest(commit_msg="Wiring through first transmission transcript")
Skipping 'repo_dir=/home/louis/spin/ss/spin.systems' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/cal' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/log' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/conf' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/pore' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/ocu' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/arc' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/qrx' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/erg' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/opt' (working tree clean)
Commit [repo_dir=/home/louis/spin/ss/poll] ⠶ Wiring through first transmission transcript
⇢ Pushing ⠶ origin
Skipping 'repo_dir=/home/louis/spin/ss/arb' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/reed' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/noto' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/plot' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/doc' (working tree clean)
Skipping 'repo_dir=/home/louis/spin/ss/labs' (working tree clean)
```

After which point there should be a web page under the path
`wire/20/11/3/oral-evidence_1122.html` i.e.
[https://poll.spin.systems/wire/20/11/3/oral-evidence_1122.html](https://poll.spin.systems/wire/20/11/3/oral-evidence_1122.html)

To build all sites with a wire config, run `ql.fold.wire.standup()`.

<details><summary>More details</summary>

<p>

In fact, `standup` returns a dictionary of the domains, though for now
only one domain is in use with wires.

```py
emitters = ql.fold.wire.standup(verbose=False)
emitters
```
⇣
```STDOUT
{'poll': <quill.fold.wire.emitters.WireEmitter object at 0x7f304980eb20>}
```

</p>

</details>

Then to push the sites 'live', run `ql.remote_push_manifest("Commit message goes here")`.

## Aliases

The "canonical names" displayed in the README are the aliases, which by and large
are the same as the domain names.

These provide the titles of the index pages of each site.

I might make more use of these in future, I originally only needed these
as it turns out the description on GitHub/GitLab isn't stored in the git repo
itself (silly as there's a `description` built in to `git`?)

Using this let me generate a nice README for the spin.systems superrepo:

> # spin.systems
> 
> spin.systems: [`ss`](https://gitlab.com/spin.systems/spin.systems.gitlab.io)
> 
> - `cal`: [q ⠶ cal](https://gitlab.com/qu-cal/qu-cal.gitlab.io)
> - `log`: [∫ ⠶ log](https://gitlab.com/spin-log/spin-log.gitlab.io)
> - `conf`: [q ⠶ conf](https://gitlab.com/qu-conf/qu-conf.gitlab.io)
> - `pore`: [q ⠶ biorx](https://gitlab.com/qu-pore/qu-pore.gitlab.io)
> - `ocu`: [∫ ⠶ ocu](https://gitlab.com/naiveoculus/naiveoculus.gitlab.io)
> - `arc`: [∫ ⠶ app](https://gitlab.com/appendens/appendens.gitlab.io)
> - `qrx`: [q ⠶ arx](https://gitlab.com/qu-arx/qu-arx.gitlab.io)
> - `erg`: [∫ ⠶ erg](https://gitlab.com/spin-erg/spin-erg.gitlab.io)
> - `opt`: [∫ ⠶ opt](https://gitlab.com/spin-opt/spin-opt.gitlab.io)
> - `poll`: [q ⠶ poll](https://gitlab.com/qu-poll/qu-poll.gitlab.io)
> - `arb`: [∫ ⠶ arb](https://gitlab.com/spin-arb/spin-arb.gitlab.io)
> - `reed`: [q ⠶ reed](https://gitlab.com/qu-reed/qu-reed.gitlab.io)
> - `noto`: [q ⠶ ruinoto](https://gitlab.com/qu-noto/qu-noto.gitlab.io)
> - `plot`: [q ⠶ plotspot](https://gitlab.com/qu-plot/qu-plot.gitlab.io)
> - `doc`: [∫ ⠶ doc](https://gitlab.com/spin-doc/spin-doc.gitlab.io)
> - `labs`: [q ⠶ labs](https://gitlab.com/qu-labs/qu-labs.gitlab.io)

## Addresses

"Spin addresses" follow the above "{namespace}⠶{domain|alias}" format, and additionally:

- Some (initially only `∫⠶log`) subdomain repos are 'deploy' stage counterparts
  to local 'dev' stage directories.
- Some (initially only `∫⠶log`) subdomain repos will be 'addressed' with a date
  [and a zero-based counter for same-day entries]

```py
>>> example = "∫⠶log⠶20⠶oct⠶25⠶0"
>>> eg_addr = ql.AddressPath(example)
>>> eg_addr
['∫', 'log', '20', 'oct', '25', '0']
```

The path has been parsed ("strictly" by default) into parts which are
'typed' strings.

```py
pprint(list(map(type, eg_addr)))
```
⇣
```STDOUT
[<class 'ql.src.quill.scan.address.paths.NameSpaceString'>,
 <class 'ql.src.quill.scan.address.paths.DomainString'>,
 <class 'ql.src.quill.scan.address.paths.YyDigitString'>,
 <class 'ql.src.quill.scan.address.paths.mmmString'>,
 <class 'ql.src.quill.scan.address.paths.DdDigitString'>,
 <class 'ql.src.quill.scan.address.paths.FileIntString'>]
```

A file path can be obtained from this using `interpret_filepath`,
which is bound to the class as the `filepath` property:

```py
>>> eg_addr.filepath
PosixPath('/home/louis/spin/l/20/10oct/25/0_digitalising_spin_addresses.mmd')
>>> eg_addr.filepath.exists()
True
>>> ql.mmd(eg_addr.filepath)
Parsed MMD file (Document of 4 blocks)
```

This comes in handy when building components of the spin.systems site such as
[`tap`](https://github.com/lmmx/tap) which can then build parts for a particular domain
with

```py
>>> eg_addr = ql.AddressPath.from_parts(domain="poll", ymd=(2021, 2, 17))
>>> eg_addr.filepath
PosixPath('/home/louis/spin/ss/poll/transmission/21/02feb/17')
```

This gives a simple date-based interface obeying the storage structure of quill,
though unlike files, paths to directories in this way may not exist
(instead they can be created as needed).

## TODO

- [ ] A next step could be a class representing the state of the websites [beyond CI], which can
  then be cross-referenced against the `repos_df` (but the goal is not to entirely Python-ise
  the site development, just the management of key aspects to do with the version control on disk)
- [x] Make a pip installable binary wheel (bdist not currently working with SCM, just sdist)
- [ ] Make package capable of downloading missing data files in the event it is being distributed
