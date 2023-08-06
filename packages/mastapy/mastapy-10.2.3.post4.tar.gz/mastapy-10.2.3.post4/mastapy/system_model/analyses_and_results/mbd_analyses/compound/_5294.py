﻿'''_5294.py

WormGearSetCompoundMultiBodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2150
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5292, _5293, _5230
from mastapy.system_model.analyses_and_results.mbd_analyses import _5167
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'WormGearSetCompoundMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetCompoundMultiBodyDynamicsAnalysis',)


class WormGearSetCompoundMultiBodyDynamicsAnalysis(_5230.GearSetCompoundMultiBodyDynamicsAnalysis):
    '''WormGearSetCompoundMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetCompoundMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2150.WormGearSet':
        '''WormGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2150.WormGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def assembly_design(self) -> '_2150.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2150.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def worm_gears_compound_multi_body_dynamics_analysis(self) -> 'List[_5292.WormGearCompoundMultiBodyDynamicsAnalysis]':
        '''List[WormGearCompoundMultiBodyDynamicsAnalysis]: 'WormGearsCompoundMultiBodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsCompoundMultiBodyDynamicsAnalysis, constructor.new(_5292.WormGearCompoundMultiBodyDynamicsAnalysis))
        return value

    @property
    def worm_meshes_compound_multi_body_dynamics_analysis(self) -> 'List[_5293.WormGearMeshCompoundMultiBodyDynamicsAnalysis]':
        '''List[WormGearMeshCompoundMultiBodyDynamicsAnalysis]: 'WormMeshesCompoundMultiBodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesCompoundMultiBodyDynamicsAnalysis, constructor.new(_5293.WormGearMeshCompoundMultiBodyDynamicsAnalysis))
        return value

    @property
    def load_case_analyses_ready(self) -> 'List[_5167.WormGearSetMultiBodyDynamicsAnalysis]':
        '''List[WormGearSetMultiBodyDynamicsAnalysis]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_5167.WormGearSetMultiBodyDynamicsAnalysis))
        return value

    @property
    def assembly_multi_body_dynamics_analysis_load_cases(self) -> 'List[_5167.WormGearSetMultiBodyDynamicsAnalysis]':
        '''List[WormGearSetMultiBodyDynamicsAnalysis]: 'AssemblyMultiBodyDynamicsAnalysisLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyMultiBodyDynamicsAnalysisLoadCases, constructor.new(_5167.WormGearSetMultiBodyDynamicsAnalysis))
        return value
