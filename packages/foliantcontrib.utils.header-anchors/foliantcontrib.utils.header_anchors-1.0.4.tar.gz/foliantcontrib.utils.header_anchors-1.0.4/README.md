[![](https://img.shields.io/pypi/v/foliantcontrib.utils.header_anchors.svg)](https://pypi.org/project/foliantcontrib.utils.header_anchors/)  [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.utils.header_anchors.svg?label=GitHub)](https://github.com/foliant-docs/foliantcontrib.utils.header_anchors)

# HeaderAnchors

HeaderAnchors is a module which converts heading titles into IDs just like it is done by specific backends.

Module exports three main functions:
- **to_id** which converts a title into an ID by the rules of specific backend,
- **make_unique** which adds a digit to make duplicate heading ID unique, according to the rules of specific backend.
- **is_flat** which determines whether backend uses flatten preprocessor or not.

# Introduction

All Foliant backends add anchors to each heading to make it possible to reference headings in URLs. The problem is that each backend has its own way to do that. For example, the heading **My wife's birthday-party** will get an ID `my-wifes-birthday-party` in Pandoc, `header-my-wife’s-birthday-party` in aglio and `my-wife-39-s-birthday-party` in slate.

Moreover, different backends have different ways to deal with duplicate IDs. Utils in this module help you cope with these problems.

# Usage

To use functions from this module, first install it with command

```bash
pip3 install foliantcontrib.utils.header_anchors
```

Then import the main functions:

```python
>>> from foliant.preprocessors.utils.header_anchors import to_id, make_unique, is_flat

```

## to_id

Feed a header title to the `to_id` function to get the proper id for each backend:

```python
>>> title = "My wife's birthday-party"
>>> to_id(title, 'pandoc')
'my-wifes-birthday-party'
>>> to_id(title, 'aglio')
'header-my-wife’s-birthday-party'
>>> to_id(title, 'slate')
'my-wife-39-s-birthday-party'

```

**available backends**:

param | backend
----- | -------
`'pandoc'` | [Pandoc](https://foliant-docs.github.io/docs/backends/pandoc/)
`'mdtopdf'` | [MdToPdf](https://foliant-docs.github.io/docs/backends/mdtopdf/)
`'aglio'` | [Aglio](https://foliant-docs.github.io/docs/backends/aglio/)
`'mkdocs'` | [MkDocs](https://foliant-docs.github.io/docs/backends/mkdocs/)
`'slate'` | [Slate](https://foliant-docs.github.io/docs/backends/slate/)
`'confluence'` | [Confluence](https://foliant-docs.github.io/docs/backends/confluence/)
`'no_transform'` | no transformations, return string as is

If the name of the backend is not recognized, pandoc will be used as a fallback backend:

```python
>>> to_id(title, 'nonexistent backend')
'my-wifes-birthday-party'

```

## make_unique

If some headers in the document have the same title or their IDs match, each backend transforms the ID for it to remain unique. Pandoc adds subsequent numbers with a hyphen, MkDocs — numbers with an unerscore.

`make_unique` function handles the proper transformations for you. Feed it an id, backend name and number of occurrences of this title in the document to get the proper unique id:

```python
>>> make_unique('my-title', 3, 'pandoc')
'my-title-2'
>>> make_unique('my-title', 3, 'mkdocs')
'my-title_2'
>>> make_unique('my-title', 3, 'slate')
'my-title-3'

```

If the name of the backend is not recognized, pandoc will be used as a fallback backend:

```python
>>> make_unique('my-title', 3, 'nonexistent backend')
'my-title-2'

```

## is_flat

is_flat function takes the backend name as parameter and returns True if backend uses flatten preprocessor to make a single file out of all chapters.

```python
>>> is_flat('pandoc')
True
>>> is_flat('mkdocs')
False

```

## IDGenerator class

IDGenerator is a class which helps generate unique anchors in seemless way. It records every call to generate an anchor from a title, and if the anchor repeats, it calls make_unique to make it unique.

Here's an example usage:

```python
>>> from foliant.preprocessors.utils.header_anchors import IDGenerator
>>> idgen = IDGenerator('pandoc')
>>> idgen.generate('My title')
'my-title'
>>> idgen.generate('Another title!')
'another-title'
>>> idgen.generate('My title')
'my-title-1'

```

After generating id for **My title** for a second time generator had added a `-1` to it. To reset the id count call the `reset` method:

```python
>>> idgen.reset()
>>> idgen.generate('My title')
'my-title'

```
