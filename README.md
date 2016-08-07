readoc - Human readable text documents
======================================

Readoc is intended to provide a mark-up format aimed at more formal
documents, while still using a text file that looks good as-is.

This is a reimplementation in python from an earlier project built in C
and is currently far from feature complete.

Examples
--------

There is a minimal interface available on the command line, currently
providing two output options: normalized readoc or HTML.

To normalize a readoc file, that is reindent, do consistent renumbering
and rewrap text use

    python -m readoc.normalize < in-file.txt

To output HTML use

    python -m readoc.html < in-file.txt
