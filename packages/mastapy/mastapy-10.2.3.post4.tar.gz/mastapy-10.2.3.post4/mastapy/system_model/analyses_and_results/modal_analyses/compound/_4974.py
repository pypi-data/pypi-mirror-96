﻿'''_4974.py

KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2136
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4831
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4971
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis',)


class KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis(_4971.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysis):
    '''KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2136.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2136.KlingelnbergCycloPalloidHypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_4831.KlingelnbergCycloPalloidHypoidGearModalAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearModalAnalysis]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_4831.KlingelnbergCycloPalloidHypoidGearModalAnalysis))
        return value

    @property
    def component_modal_analysis_load_cases(self) -> 'List[_4831.KlingelnbergCycloPalloidHypoidGearModalAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearModalAnalysis]: 'ComponentModalAnalysisLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentModalAnalysisLoadCases, constructor.new(_4831.KlingelnbergCycloPalloidHypoidGearModalAnalysis))
        return value
