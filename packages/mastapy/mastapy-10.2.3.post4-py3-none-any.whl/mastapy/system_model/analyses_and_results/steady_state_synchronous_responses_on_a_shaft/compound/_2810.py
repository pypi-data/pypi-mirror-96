﻿'''_2810.py

HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2181
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2808, _2809, _2752
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2679
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft',)


class HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft(_2752.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft):
    '''HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2181.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2181.HypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def assembly_design(self) -> '_2181.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2181.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def hypoid_gears_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2808.HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft]: 'HypoidGearsCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2808.HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def hypoid_meshes_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2809.HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'HypoidMeshesCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2809.HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def load_case_analyses_ready(self) -> 'List[_2679.HypoidGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearSetSteadyStateSynchronousResponseOnAShaft]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_2679.HypoidGearSetSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_steady_state_synchronous_response_on_a_shaft_load_cases(self) -> 'List[_2679.HypoidGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblySteadyStateSynchronousResponseOnAShaftLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySteadyStateSynchronousResponseOnAShaftLoadCases, constructor.new(_2679.HypoidGearSetSteadyStateSynchronousResponseOnAShaft))
        return value
