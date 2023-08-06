﻿'''_6599.py

SynchroniserLoadCase
'''


from mastapy.system_model.part_model.couplings import _2273
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6581
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'SynchroniserLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserLoadCase',)


class SynchroniserLoadCase(_6581.SpecialisedAssemblyLoadCase):
    '''SynchroniserLoadCase

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2273.Synchroniser':
        '''Synchroniser: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2273.Synchroniser)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None
