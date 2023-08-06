﻿'''_3060.py

FaceGearSetCompoundSteadyStateSynchronousResponseAtASpeed
'''


from typing import List

from mastapy.system_model.part_model.gears import _2175
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed.compound import _3058, _3059, _3065
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _2929
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed.Compound', 'FaceGearSetCompoundSteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetCompoundSteadyStateSynchronousResponseAtASpeed',)


class FaceGearSetCompoundSteadyStateSynchronousResponseAtASpeed(_3065.GearSetCompoundSteadyStateSynchronousResponseAtASpeed):
    '''FaceGearSetCompoundSteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetCompoundSteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2175.FaceGearSet':
        '''FaceGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2175.FaceGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def assembly_design(self) -> '_2175.FaceGearSet':
        '''FaceGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2175.FaceGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def face_gears_compound_steady_state_synchronous_response_at_a_speed(self) -> 'List[_3058.FaceGearCompoundSteadyStateSynchronousResponseAtASpeed]':
        '''List[FaceGearCompoundSteadyStateSynchronousResponseAtASpeed]: 'FaceGearsCompoundSteadyStateSynchronousResponseAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsCompoundSteadyStateSynchronousResponseAtASpeed, constructor.new(_3058.FaceGearCompoundSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def face_meshes_compound_steady_state_synchronous_response_at_a_speed(self) -> 'List[_3059.FaceGearMeshCompoundSteadyStateSynchronousResponseAtASpeed]':
        '''List[FaceGearMeshCompoundSteadyStateSynchronousResponseAtASpeed]: 'FaceMeshesCompoundSteadyStateSynchronousResponseAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesCompoundSteadyStateSynchronousResponseAtASpeed, constructor.new(_3059.FaceGearMeshCompoundSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def load_case_analyses_ready(self) -> 'List[_2929.FaceGearSetSteadyStateSynchronousResponseAtASpeed]':
        '''List[FaceGearSetSteadyStateSynchronousResponseAtASpeed]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_2929.FaceGearSetSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def assembly_steady_state_synchronous_response_at_a_speed_load_cases(self) -> 'List[_2929.FaceGearSetSteadyStateSynchronousResponseAtASpeed]':
        '''List[FaceGearSetSteadyStateSynchronousResponseAtASpeed]: 'AssemblySteadyStateSynchronousResponseAtASpeedLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySteadyStateSynchronousResponseAtASpeedLoadCases, constructor.new(_2929.FaceGearSetSteadyStateSynchronousResponseAtASpeed))
        return value
