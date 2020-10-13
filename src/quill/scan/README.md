## quill ⠶ scan

- Read `.mmd` file format
  - Effectively houses a sub-library, `lever`, which aims to be self-contained
    (3rd rewrite of a couple of previous attempts to perform the same purpose)

### Current status

- The `MMD` class (defined in [`lever.py`](lever.py)) currently initialises a
  `Doc` which is a wrapper around the `BlockDoc` class, and as such,
  sets up the `.doc` property of the `MMD` object, storing a list of `NodeBlock`
  objects in the `.doc.blocks` subproperty.
  - Each `NodeBlock` in turn has `.nodes`, each of which corresponds to a line
    which has no annotation until being validated (the parsing step after tokenisation).
  - The parsing step is triggered upon finishing the parse of the MMD file,
    in the initialisation method of the `Doc` class, which runs after the
    wrapped `BlockDoc` class initialisation method carries out tokenisation
    for each line (processed into a `Node`).
    - This ensures that no node is classified before it is 'prepared', which is
      necessary as 'lookbehind' can modify a node on a preceding line (e.g. a
      line ending in a colon is only marked as initialising a list if it is followed
      by a list item prefix on the immediately next line).
- `Doc` is intended to be the 'parser' class initialised following the 'tokenisation'
  of the input `.mmd` file's lines, and will 'tag' nodes as being of certain
  types, from which block-level and document-level elements can be assigned.
  - The `lever.parse_nodes_to_list` function returns a generator yielding all
    block-level lists (`BlockList` objects) which are collected at the document level
    in `Doc` following tokenisation, in `Doc.lists`. 
### TODO

- Due to the recursive functions used to parse block-level elements, it is now necessary
  to label nodes with their line numbers upon parsing (as an attribute of `Node`).
- Perhaps only store node `linenumber` index within `DocList` to remove the duplication?
- Use the `parent_elem` argument to `BlockList` where the header is within some
  other structure (e.g. has a continuation prefix) to 'situate' it within its block.
- Autodetect a structured list (default: off, or it will slow down list parsing)
