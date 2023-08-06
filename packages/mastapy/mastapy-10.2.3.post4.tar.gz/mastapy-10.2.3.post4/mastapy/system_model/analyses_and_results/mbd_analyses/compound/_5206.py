﻿'''_5206.py

ConceptGearSetCompoundMultiBodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2120
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5204, _5205, _5230
from mastapy.system_model.analyses_and_results.mbd_analyses import _5064
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'ConceptGearSetCompoundMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetCompoundMultiBodyDynamicsAnalysis',)


class ConceptGearSetCompoundMultiBodyDynamicsAnalysis(_5230.GearSetCompoundMultiBodyDynamicsAnalysis):
    '''ConceptGearSetCompoundMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_COMPOUND_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetCompoundMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2120.ConceptGearSet':
        '''ConceptGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2120.ConceptGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def assembly_design(self) -> '_2120.ConceptGearSet':
        '''ConceptGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2120.ConceptGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def concept_gears_compound_multi_body_dynamics_analysis(self) -> 'List[_5204.ConceptGearCompoundMultiBodyDynamicsAnalysis]':
        '''List[ConceptGearCompoundMultiBodyDynamicsAnalysis]: 'ConceptGearsCompoundMultiBodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearsCompoundMultiBodyDynamicsAnalysis, constructor.new(_5204.ConceptGearCompoundMultiBodyDynamicsAnalysis))
        return value

    @property
    def concept_meshes_compound_multi_body_dynamics_analysis(self) -> 'List[_5205.ConceptGearMeshCompoundMultiBodyDynamicsAnalysis]':
        '''List[ConceptGearMeshCompoundMultiBodyDynamicsAnalysis]: 'ConceptMeshesCompoundMultiBodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptMeshesCompoundMultiBodyDynamicsAnalysis, constructor.new(_5205.ConceptGearMeshCompoundMultiBodyDynamicsAnalysis))
        return value

    @property
    def load_case_analyses_ready(self) -> 'List[_5064.ConceptGearSetMultiBodyDynamicsAnalysis]':
        '''List[ConceptGearSetMultiBodyDynamicsAnalysis]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_5064.ConceptGearSetMultiBodyDynamicsAnalysis))
        return value

    @property
    def assembly_multi_body_dynamics_analysis_load_cases(self) -> 'List[_5064.ConceptGearSetMultiBodyDynamicsAnalysis]':
        '''List[ConceptGearSetMultiBodyDynamicsAnalysis]: 'AssemblyMultiBodyDynamicsAnalysisLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyMultiBodyDynamicsAnalysisLoadCases, constructor.new(_5064.ConceptGearSetMultiBodyDynamicsAnalysis))
        return value
