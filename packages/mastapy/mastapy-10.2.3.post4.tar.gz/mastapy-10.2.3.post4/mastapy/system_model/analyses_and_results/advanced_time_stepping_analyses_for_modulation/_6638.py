﻿'''_6638.py

ConceptGearMeshAdvancedTimeSteppingAnalysisForModulation
'''


from mastapy.system_model.connections_and_sockets.gears import _1959
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6440
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6667
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_MESH_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'ConceptGearMeshAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearMeshAdvancedTimeSteppingAnalysisForModulation',)


class ConceptGearMeshAdvancedTimeSteppingAnalysisForModulation(_6667.GearMeshAdvancedTimeSteppingAnalysisForModulation):
    '''ConceptGearMeshAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_MESH_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearMeshAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1959.ConceptGearMesh':
        '''ConceptGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1959.ConceptGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_load_case(self) -> '_6440.ConceptGearMeshLoadCase':
        '''ConceptGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6440.ConceptGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase else None
