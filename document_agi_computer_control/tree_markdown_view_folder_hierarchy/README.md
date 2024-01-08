Every directory has only info on its children and not children's decendents during its summary creation. This makes it easy to build summary for large hierarchical structures.

When summarizing a directory, do it two by two recursively. Note you must include the path names and their types (directory? file?)

Strip blank spaces and asterisks from model response.

If the response is exceeding word limit or with multiple lines, ask the model to fix.

Hover to get longer explaination. Or just place it as is.

Toggle button to show detailed explanation.

Display "Loading" while loading tree.json

For index.html, add another parameter called "match" to filter the results by certain fields

Currently, when clicking on the link of tree.html will jump to index.html?file=filepath or index.html?q=filepath&search=off