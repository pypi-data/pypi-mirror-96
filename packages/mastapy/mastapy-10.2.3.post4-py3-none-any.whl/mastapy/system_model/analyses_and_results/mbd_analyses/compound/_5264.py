﻿'''_5264.py

ShaftCompoundMultiBodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2081
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5134
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5178
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'ShaftCompoundMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundMultiBodyDynamicsAnalysis',)


class ShaftCompoundMultiBodyDynamicsAnalysis(_5178.AbstractShaftOrHousingCompoundMultiBodyDynamicsAnalysis):
    '''ShaftCompoundMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2081.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2081.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_5134.ShaftMultiBodyDynamicsAnalysis]':
        '''List[ShaftMultiBodyDynamicsAnalysis]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_5134.ShaftMultiBodyDynamicsAnalysis))
        return value

    @property
    def component_multi_body_dynamics_analysis_load_cases(self) -> 'List[_5134.ShaftMultiBodyDynamicsAnalysis]':
        '''List[ShaftMultiBodyDynamicsAnalysis]: 'ComponentMultiBodyDynamicsAnalysisLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentMultiBodyDynamicsAnalysisLoadCases, constructor.new(_5134.ShaftMultiBodyDynamicsAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundMultiBodyDynamicsAnalysis]':
        '''List[ShaftCompoundMultiBodyDynamicsAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundMultiBodyDynamicsAnalysis))
        return value
