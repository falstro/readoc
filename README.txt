Date: August, 2016                                         Author: F. Alstromer



              Readoc - Human Readable Plain Text Documents


0 Abstract

  This document presents a formal specification of the readoc text document
  file format and structure, along with documentation of the accompanying
  parser and rendering tools. It also specifies the canonical form which
  any tool rendering readoc should adhere to. Please note that this
  document is work in progress.

1 Introduction

  The readoc format is heavily inspired by the classic RFC text output format,
  but rather than using being the output and using something not-so-readable
  as an input format, readoc is intended to be easy on the eyes already in its
  source form.

  Being a human readable is however not enough, it also has to be human
  editable, thus the parser is appropriately lenient and should achieve the
  intuitive result in most cases.

  Being a visual format, white space is highly relevant, and the only sensible
  font for viewing readoc sources is a monospace font. Tab-characters are
  interpreted as at least one space, and as many as necessary to align the
  column to the nearest multiple of eight. A line containing only white space
  is considered a blank line.

  Encoding is UTF-8 but UTF-16 (LE or BE) is also supported. A byte order
  marker is permissible. Any Unicode character (regardless of byte count)
  counts as one column wide.

0.1 Canonical white space

  When outputting canonical readoc, the following applies:
    - All input tab characters are expanded and replaced by space characters.
    - All trailing white space is trimmed
    - All empty or white space only lines at the end of the document are
      discarded.

2 Document structure

  A readoc document is context sensitive, which means that text is interpreted
  differently depending on where in the document it is encountered. There are
  four (more like three and a half) different base contexts:
    - Properties
    - Title
    - Body text
    - Embedded documents
  We shall look at each of this in more detail below.

  In general, a readoc document starts out with a properties section defining
  meta-data for the document itself. There are no set fields, and any
  appropriate information can be recorded. Common examples can include author
  and date, but more exotic options are conceivable, such as keywords, topic,
  or even document security classification. This is also a perfect place for a
  VIm modeline.

  After the initial section of properties the context switches to title. If no
  title can be identified, the context switches to body text. There can be
  only one title per document.

  The body text has a couple of different sub contexts which are outlined
  below, but in principal the body text continues until the end of the
  document. If a marker for an embedded document is encountered, the body text
  context is suspended in its current state, and the context switches to the
  embedded document.

  The embedded document is read verbatim until the end marker is encountered.
  At that point the context switches to properties again, which describe the
  embedded document. These properties do affect the interpretation of the
  embedded document and how it's presented during rendering. Generally
  embedded documents are used to describe graphs or illustrations, which can
  be used to generate a graphical representation during rendering. An
  excellent example of this is Graphviz integration, which is discussed in the
  rendering sections below.

  After the properties for the embedded document, the context reverts to the
  same body text state as before. This means that, for example, we can insert
  an embedded document in an enumerated list, without restarting the list item
  numbering.

2.1 Properties

  Properties end if either a blank line is encountered, or a value is
  encountered that cannot be matched to a key from a previous line. The most
  common reason for the latter case is if we're encountering body text
  containing spaces (thus not qualifying as a key) already on the first line
  (where there are no previous keys). If we end on a blank line, the blank
  line is consumed before switching contexts. If not, the line remains to be
  interpreted in the new context. This is relevant when reading properties
  after embedded documents, in which case a blank line after the properties
  would not end the current paragraph (a blank line before the embedded
  document would, though), and two blank lines are needed to end the paragraph
  here.

2.2 Title

  Any text line indented by at least five columns will be interpreted as a
  title text line. The title text continues until we encounter either a blank
  line, or a line which is indented less than five columns.

0.2.1 Canonical form

  When outputting canonical readoc, the following applies:
    - All title text lines are joined using a single space and rewrapped.
    - Consecutive white space are normalized to a single space.
    - All text lines are wrapped to be at most 70 characters long.
    - Each text line is centered on an 80 column wide line, leaving at least a
      five column margin on each side.
    - The title is output with two leading and two trailing blank lines.

2.3 Body text

  The body text is split into a few different elements, which are listed in
  their own section below. When processing body text, it's important to note
  that white space within the text, i.e. not used for indentation, will be
  treated as if normalized to a single space. That means that doubled spaces
  can be used, to visually adjust text at the authors discretion. Indeed, the
  normalizing output of the readoc tool allows you take advantage of that fact
  to output paragraphs using justified alignment. It should be noted that in
  the canonical form, extra spaces will be removed, thus the output using
  justified alignment deviates from the canoncial form.

2.4 Embedded documents

  Embedded documents start and end using markers. Markers are lines containing
  nothing but dashes ('-') and white space. A marker must have at least 4
  dashes to qualify, and the end marker must have the exact same number of
  dashes as the corresponding start marker. Note that only the number of
  dashes is relevant when matching start and end markers, the dashes need not
  be consecutive, and white space placement doesn't need to match.

3 Body text elements

3.1 Sections

  Section headings start at the left most column (i.e. may not be indented)
  using a period ('.') separated list of numbers. The value of the numbers
  themselves are not important and will not be interpreted, except if the
  first number is zero which turns it into an unnumbered section (see below).
  However, the number of elements in the list determines the section depth.
  Terminating the list with a period is optional.

0.1.1 Numbered and unnumbered

0.1.2 Canonical form

  When outputting a canonical section header the following applies:
    - The numbering is natural, with the first section starting at one, and
      each section incrementing the appropriate element in the list and
      resetting all counters for deeper sections.
    - There is no terminating period on the last number element.
    - An unnumbered section simply outputs the first element as zero, but
      otherwise keeps counting as normal, except if it's top-level section in
      which case the counter remains as-is.

3.2 Paragraphs

  Paragraphs end if an empty line is encountered, or if a new section is
  encountered. Note that a list does not end a paragraph unless it's preceded
  or followed by an empty line. Note that empty lines within the list does not
  affect the current paragraph.

  Text lines in paragraphs can have arbitrary indentation, except if we start
  the document with a paragraph and there's no title, in which case the first
  line may be indented by at most 4 columns in order to avoid being
  interpreted as a title.

0.2.2 Canonical form

  In the canonical form, the following applies to paragraphs:
    - Consecutive lines are joined using a single space, and then re-wrapped.
    - Consecutive space characters are normalized to a single space.
    - All text lines are indented by two spaces, and are wrapped no later than
      at column 78, leaving two columns of margin on either side on a standard
      80 column display.
    - All paragraphs end with a blank line, even if followed by a section,
      except if we've reached the end of the file.

3.3 Lists

  Lists come in two forms, enumerated and itemized. Lists can be nested
  arbitrarily, with either one being used as a sub list to either one. Similar
  indentation rules apply for both, in that the top-level list must be
  indented by at least one column, and sub-lists must be indented at least one
  more column than the containing list. Consecutive elements in the same list
  (i.e. on the same list depth) must be indented to the same column.

  If a line break is needed within the item, indent the continuation line to
  at least the same column as where the text from the first line started,
  after the item marker itself.

  If an itemized list follows an enumerated list (or vice versa) on the same
  indentation level, it is interpreted as if the enumerated list ends and a
  new itemized list begins.

3.3.1 Enumerated

  Enumerated lists must be intended at least one column (or it will be
  interpreted as a section) and each item must lead with a digit followed by a
  '.' and at least one space. The digit used for the first entry in every
  enumerated list is significant and determines both the starting digit and
  the type of items to use.

  The following are valid as list item types:
    - Arabic, i.e. '1.'
    - Alphabetic, upper or lower case, i.e. 'A.' or 'a.'
    - Roman, upper or lower case, i.e. 'I.' or 'i.'

  To start at a higher number, simply start the first item with that, all the
  following items will count up naturally from there regardless of item type
  used. This means you can start with the alphabetic 'A.', and then use '1.'
  (or any enumerated item type) for all following items and the list will
  continue to count alphabetically, A, B, C, etc. All enumerated items start
  with one letter/digit followed by '.' except for roman numerals starting at
  a higher number than 1. For example, to start a roman numbered list at
  three, use 'iii.' as the first item.

  Note that the rendering might override the selected item styles.

  There's currently no way to start an alphabetically enumerated list using
  the letter 'I' or 'i', which would be interpreted as the upper- or lowercase
  roman numeral for one.

0.3.1.1 Canonical form

  In the canonical form, the following applies to enumerated lists:
    - The top level is indented four columns (two columns in from the
      canonical paragraph)
    - Each sub list is indented two columns further than the containing list.
    - The first item in the enumerated list uses the same label as the input.
      Subsequent items continue the numbering scheme regardless of the labels
      used in the input.

3.3.2 Itemized

  Like enumerated lists, itemized lists must be indented at least one column.
  The itemized list can use one of '-', '*', or '+' followed by at least one
  space before the item text. The actual item character used is ignored, and
  may be mixed freely.

0.3.1.1 Canonical form

  In the canonical form, the following applies to itemized lists:
    - The top level is indented four columns (two columns in from the
      canonical paragraph)
    - Each sub list is indented two columns further than the containing list.
    - All items use a dash ('-') as label.

4 Markup

  All text can use various forms of inline markup such as for emphasis or for
  creating footnotes and references. This section is still work in progress.

5 Rendering

  The reference readoc implementation (currently) provides three output
  formats:
    - Normalized readoc output,
    - HTML, and
    - LaTeX

  If a table of contents is produced, it will be generated before the first
  numbered section. This means any unnumbered section before the first
  numbered section will appear before the table of contents.

  Both HTML and LaTeX interpret embedded documents. If there is a embedded
  document property called "Figure", the contents of the embedded document
  will be frame appropriately, and the property value will be used as a figure
  caption. There's one special property "t" which specifies how to interpret
  the content, in particular Graphviz formats are supported:
    - dot
    - neato
    - twopi
    - circo
    - fdp
    - sfdp
    - patchwork
  In addition, there's also the graphviz-like mscgen format
    - msc

  In all the Graphviz (and msc) cases, the embedded content will be wrapped in
  a "graph" (or "digraph") as appropriate and should not be included. Use of
  these formats require the appropriate tools to be installed.

                                   --- -- -
                                    A -> B
                                    B -> C
                                    C -> A
                                   - -- ---
                         Figure: Example dot diagram                    t: dot

  Again, note that the start and end markers for embedded documents need only
  match in the number of dashes, not exact arrangement.

5.1 Normalized

  Work in progress

5.2 HTML

  By default, the title is output using "h1" and the class "title", and
  top-level sections use plain "h1". There are two options for customizing
  this behavior, either style the title differently (using classes, or styles
  directly) or push sections down to "h2" (with subsections ending up "h3" and
  so on).

5.3 LaTeX

  The LaTeX generator will output an incomplete LaTeX file and should be
  prefixed with a preamble. The prefixed preamble should not specify begin
  document, as the renderer will need to amend it with a few statements
  before continuing to render the document.

  The document title will be used to set the standard LaTeX title.
  Furthermore, two document properties are interpreted, case insensitive:
    - "author" (or "authors") will be used to specify the standard LaTeX
      author.
    - "date" will be used to specify the date.
  In addition, all properties can be made available as macros with a user
  defined prefix ("readoc@" by default), useful for example when defining
  header and footer.

  After begin-document, the standard "maketitle" macro will be used to
  generate the title.

  Leading unnumbered sections will be treated as abstracts. If the section
  heading is literally "Abstract", the default abstract heading will be used
  (which may be modified by the LaTeX environment, such as by a language
  pack). Otherwise the heading is replaced to match the source document.
