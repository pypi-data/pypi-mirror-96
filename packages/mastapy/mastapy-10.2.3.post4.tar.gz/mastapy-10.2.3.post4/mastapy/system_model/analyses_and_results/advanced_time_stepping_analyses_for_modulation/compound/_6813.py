﻿'''_6813.py

MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model import _2110
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6684
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6860
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation',)


class MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation(_6860.VirtualComponentCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2110.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2110.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_6684.MassDiscAdvancedTimeSteppingAnalysisForModulation]':
        '''List[MassDiscAdvancedTimeSteppingAnalysisForModulation]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_6684.MassDiscAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def component_advanced_time_stepping_analysis_for_modulation_load_cases(self) -> 'List[_6684.MassDiscAdvancedTimeSteppingAnalysisForModulation]':
        '''List[MassDiscAdvancedTimeSteppingAnalysisForModulation]: 'ComponentAdvancedTimeSteppingAnalysisForModulationLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAdvancedTimeSteppingAnalysisForModulationLoadCases, constructor.new(_6684.MassDiscAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value
