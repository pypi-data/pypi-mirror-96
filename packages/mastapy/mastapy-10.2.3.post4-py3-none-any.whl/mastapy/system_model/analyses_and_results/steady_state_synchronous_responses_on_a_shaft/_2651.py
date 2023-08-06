﻿'''_2651.py

SynchroniserSteadyStateSynchronousResponseOnAShaft
'''


from mastapy.system_model.part_model.couplings import _2196
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6264
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2632
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'SynchroniserSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserSteadyStateSynchronousResponseOnAShaft',)


class SynchroniserSteadyStateSynchronousResponseOnAShaft(_2632.SpecialisedAssemblySteadyStateSynchronousResponseOnAShaft):
    '''SynchroniserSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2196.Synchroniser':
        '''Synchroniser: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2196.Synchroniser)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6264.SynchroniserLoadCase':
        '''SynchroniserLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6264.SynchroniserLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None
