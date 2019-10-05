[<img src="https://github.com/jangroth/markdownhelper/workflows/build/badge.svg" alt="build_status" width="200"/>](https://github.com/jangroth/markdownhelper/actions)

# CLI Helper for Markdown (WIP)

Adds table of contents to  markdown document. 

Dump raw document:
```bash
./bin/mdh dump tests/resources/simple.md
one
# two
three
## four
five
## six
seven
# eight
nine
```

Add TOC:

```bash
./bin/mdh dump tests/resources/simple.md --toc
<a name="top"></a>
---
* [two](#1)
  * [four](#1_1)
  * [six](#1_2)
* [eight](#2)
---
one

[▲](#top)
<a name="1"></a>
# two
three

[▲](#top)
<a name="1_1"></a>
## four
five

[▲](#top)
<a name="1_2"></a>
## six
seven

[▲](#top)
<a name="2"></a>
# eight
nine
```

## Screenshots

### Before
<img src="media/before.png" alt="before" width="400"/>

### After
<img src="media/after.png" alt="after" width="400"/>