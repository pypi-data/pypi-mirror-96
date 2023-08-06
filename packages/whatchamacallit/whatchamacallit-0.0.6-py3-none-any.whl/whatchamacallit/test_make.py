import re
from whatchamacallit import make
from whatchamacallit.make import ImportToPackageMapper


def test_read_file():
    spec_map = ('gridchen/', '/root/')
    src = """
    import 'gridchen/foo.js'
    import 'gridchen/bar.js'
    """
    t = re.sub(r'(import.*?) (["\'])' + spec_map[0], r'\1 \2' + spec_map[1], src, flags=re.DOTALL)

    expected = """
    import '/root/foo.js'
    import '/root/bar.js'
    """
    assert t == expected


def test_comment():
    src = """
    /*
    Comment 1
    */
    // Comment 2
    /*
    Comment 3
    */
    import "foo";
    import "bar";
    function foo() {
    }
    """
    m = re.match(r'(\s*(/\*.*?\*/|//[^\r\n]*))*', src, flags=re.DOTALL)
    print(m.group())
    # index = 0
    # for m in re.finditer(r'(\s*(/\*.*?\*/|//[^\r\n]*))*', src, flags=re.DOTALL):
    #     print(m)
    #     index = m.end()
    #     print(m.group())
    end_of_comments = m.end()
    m = re.search(r'(function|const|let|var)\s', src[end_of_comments:], flags=re.DOTALL)
    print(m)
    imports = src[end_of_comments:end_of_comments + m.start()]
    is_import_section = re.match(r'\s*import\s', imports) is not None
    if is_import_section:
        pass


def test_process_js_imports():
    imports = {
        "gridchen/": "https://decatur.github.io/grid-chen/gridchen/"
    }

    src = """
/*
Comments...
*/

import 'gridchen/foo.js'
import * from 'gridchen/foo.js'
export * from 'gridchen/foo.js'

function foo() {}
    """
    expected = """
/*
Comments...
*/

import 'https://decatur.github.io/grid-chen/gridchen/foo.js'
import * from 'https://decatur.github.io/grid-chen/gridchen/foo.js'
export * from 'https://decatur.github.io/grid-chen/gridchen/foo.js'

function foo() {}
    """
    mapped, was_mapped = make.process_imports(src, imports)
    print(mapped)
    assert mapped == expected


def test_process_html_imports():
    class Foo(ImportToPackageMapper):
        def __init__(self, root_path):
            super().__init__(root_path)
            self._imports = {
                "gridchen/": "https://decatur.github.io/grid-chen/gridchen/"
            }

        def __contains__(self, item):
            return item in self._imports

        def __getitem__(self, item):
            return self._imports[item]

    imports = Foo('/prefix')

    src = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>form-chen Master-Detail</title>
    <link rel="stylesheet" href="gridchen/demo.css">
    <script src="gridchen/theme.js"></script>
</head>

<body>
    <h1><a href="index.html">form-chen</a> / Master-Detail Demo</h1>
    <img src="gridchen/foo.png">
</body>
<script nomodule>alert('Your browser is not supported')</script>
<script type="module">
    import * as demo from "gridchen/demo.js"

    const schema = {};
</script>

</html>"""

    expected = """<!DOCTYPE html>
<html lang="en">

<head><link href="/prefix" rel="index">
    <meta charset="UTF-8">
    <title>form-chen Master-Detail</title>
    <link rel="stylesheet" href="https://decatur.github.io/grid-chen/gridchen/demo.css">
    <script src="https://decatur.github.io/grid-chen/gridchen/theme.js"></script>
</head>

<body>
    <h1><a href="index.html">form-chen</a> / Master-Detail Demo</h1>
    <img src="https://decatur.github.io/grid-chen/gridchen/foo.png">
</body>
<script nomodule>alert('Your browser is not supported')</script>
<script type="module">
    import * as demo from "https://decatur.github.io/grid-chen/gridchen/demo.js"

    const schema = {};
</script>

</html>"""
    mapped, was_mapped = make.process_imports_html(src, imports)
    # print(mapped)
    assert mapped == expected




