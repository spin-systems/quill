## quill ⠶ scan

- Read `.mmd` file format

### Current status

- The `MMD` class (defined in [`lever.py`](lever.py)) currently initialises a
  `ParsedDoc` which is a wrapper around the `BlockDoc` class, and as such,
  sets up the `.doc` property of the `MMD` object, storing a list of `NodeBlock`
  objects in the `.doc.blocks` subproperty.
  - Each `NodeBlock` in turn has `.nodes`, each of which corresponds to a line
    which has no annotation until being validated (the parsing step after tokenisation).
  - The parsing step is triggered upon finishing the parse of the MMD file,
    in the initialisation method of the `ParsedDoc` class, which runs after the
    wrapped `BlockDoc` class initialisation method carries out tokenisation
    for each line (processed into a `Node`).
    - This ensures that no node is classified before it is 'prepared', which is
      necessary as 'lookbehind' can modify a node on a preceding line (e.g. a
      line ending in a colon is only marked as initialising a list if it is followed
      by a list item prefix on the immediately next line).
- `ParsedDoc.__init__` is under construction, and will 'tag' nodes as being of certain
  types, from which block-level and document-level elements can be assigned.
