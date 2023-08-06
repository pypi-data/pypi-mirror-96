﻿'''_7059.py

FEPartCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2101
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6928
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7005
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'FEPartCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundAdvancedSystemDeflection',)


class FEPartCompoundAdvancedSystemDeflection(_7005.AbstractShaftOrHousingCompoundAdvancedSystemDeflection):
    '''FEPartCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2101.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2101.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_6928.FEPartAdvancedSystemDeflection]':
        '''List[FEPartAdvancedSystemDeflection]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_6928.FEPartAdvancedSystemDeflection))
        return value

    @property
    def component_advanced_system_deflection_load_cases(self) -> 'List[_6928.FEPartAdvancedSystemDeflection]':
        '''List[FEPartAdvancedSystemDeflection]: 'ComponentAdvancedSystemDeflectionLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAdvancedSystemDeflectionLoadCases, constructor.new(_6928.FEPartAdvancedSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundAdvancedSystemDeflection]':
        '''List[FEPartCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundAdvancedSystemDeflection))
        return value
