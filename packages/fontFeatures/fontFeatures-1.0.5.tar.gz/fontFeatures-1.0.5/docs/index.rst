fontFeatures: Python library for manipulating OpenType font features
====================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   fee-format
   fontFeatures
   converting
   supportingmodules


OpenType fonts are “programmed” using features, which are normally
authored in Adobe’s `feature file
format <http://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html>`__.
This like source code to a computer program: it’s a user-friendly, but
computer-unfriendly, way to represent the features.

Inside a font, the features are compiled in an efficient `internal
format <https://simoncozens.github.io/fonts-and-layout/features.html#how-features-are-stored>`__.
This is like the binary of a computer program: computers can use it, but
they can’t do else anything with it, and people can’t read it.

The purpose of this library is to provide a middle ground for
representing features in a machine-manipulable format, kind of like the
abstract syntax tree of a computer programmer. This is so that:

-  features can be represented in a structured human-readable *and*
   machine-readable way, analogous to the XML files of the `Unified Font
   Object <http://unifiedfontobject.org/>`__ format.
-  features can be more directly authored by programs (such as font
   editors), rather than them having to output AFDKO feature file
   format.
-  features can be easily manipulated by programs - for example,
   features from two files merged together, or lookups moved between
   languages.

..

   How is this different from fontTool’s ``feaLib``? I’m glad you asked.
   ``feaLib`` translates between the Adobe feature file format and a
   abstract syntax tree representing *elements of the feature file* -
   not representing the feature data. The AST is still “source
   equivalent”. For example, when you code an ``aalt`` feature in
   feature file format, you might include code like ``feature salt`` to
   include lookups from another feature. But what’s actually *meant* by
   that is a set of lookups. ``fontFeatures`` allows you to manipulate
   meaning, not description.

One of the most useful uses of ``fontFeatures`` is that it powers the FEE
language. (See :ref:`fee`.)

Components
----------

fontFeatures consists of the following components:

-  :py:mod:`fontFeatures` itself, which is an abstract representation of the
   different layout operations inside a font.
-  :py:mod:`fontFeatures.feaLib` (included as a mixin) which translates
   between Adobe feature syntax and fontFeatures representation.
-  :py:mod:`fontFeatures.ttLib` which translates between OpenType binary
   fonts and fontFeatures representation. (Currently only OTF ->
   ``fontFeatures`` is partially implemented; there is no
   ``fontFeatures`` -> OTF compiler yet.)
-  :py:mod:`fontFeatures.feeLib` which parses a new, extensible format called
   FEE for font engineering.
-  :py:mod:`fontFeatures.fontDameLib` which translate FontDame text files into fontFeatures objects.

And the following utilities:

-  ``fee2fea``: translates a FEE file into Adobe feature syntax.
-  ``otf2fea``: translates an OTF file into Adobe features syntax.
-  ``mergeFee``: takes an existing font, adds FEE rules to it, and
   writes it out again.
-  ``txt2fea``: translates a FontDame txt file into Adobe features syntax.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
