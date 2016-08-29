readoc - Human readable plain text documents
============================================

ReaDoc is intended to provide a mark-up format aimed at more formal
documents, while still using a text file that looks good as-is.

This is a reimplementation in python from an earlier project built in C
and is currently far from feature complete.

The [README.txt](README.txt) documents the file format specification, and
is itself a readoc document.

Examples
--------

There is a minimal interface available on the command line, currently
providing three output options: normalized readoc, HTML, or LaTeX.

To normalize a readoc file, that is reindent, do consistent renumbering
and rewrap text use

    python -m readoc.normalize < in-file.txt

To output HTML use

    python -m readoc.html < in-file.txt

Note that HTML does not prefix html or body opening tags, so you'll need
to wrap the output appropriately if you want to serve and/or style it.

And finally, for LaTeX, use

    python -m readoc.latex < in-file.txt

Note that the output begins in the preamble, it will issue
begin{document} and end{document}, however no documentclass is
specified, so you'll need to prefix it with an appropriate preamble.
