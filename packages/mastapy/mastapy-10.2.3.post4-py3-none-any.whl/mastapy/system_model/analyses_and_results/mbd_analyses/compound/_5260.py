﻿'''_5260.py

RollingRingAssemblyCompoundMultiBodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2191
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5127
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5267
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_ASSEMBLY_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'RollingRingAssemblyCompoundMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingAssemblyCompoundMultiBodyDynamicsAnalysis',)


class RollingRingAssemblyCompoundMultiBodyDynamicsAnalysis(_5267.SpecialisedAssemblyCompoundMultiBodyDynamicsAnalysis):
    '''RollingRingAssemblyCompoundMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_ASSEMBLY_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingAssemblyCompoundMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2191.RollingRingAssembly':
        '''RollingRingAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2191.RollingRingAssembly)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def assembly_design(self) -> '_2191.RollingRingAssembly':
        '''RollingRingAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2191.RollingRingAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_5127.RollingRingAssemblyMultiBodyDynamicsAnalysis]':
        '''List[RollingRingAssemblyMultiBodyDynamicsAnalysis]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_5127.RollingRingAssemblyMultiBodyDynamicsAnalysis))
        return value

    @property
    def assembly_multi_body_dynamics_analysis_load_cases(self) -> 'List[_5127.RollingRingAssemblyMultiBodyDynamicsAnalysis]':
        '''List[RollingRingAssemblyMultiBodyDynamicsAnalysis]: 'AssemblyMultiBodyDynamicsAnalysisLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyMultiBodyDynamicsAnalysisLoadCases, constructor.new(_5127.RollingRingAssemblyMultiBodyDynamicsAnalysis))
        return value
