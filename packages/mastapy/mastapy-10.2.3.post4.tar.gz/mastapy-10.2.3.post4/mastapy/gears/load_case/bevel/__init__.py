﻿'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._662 import BevelLoadCase
    from ._663 import BevelMeshLoadCase
    from ._664 import BevelSetLoadCase
