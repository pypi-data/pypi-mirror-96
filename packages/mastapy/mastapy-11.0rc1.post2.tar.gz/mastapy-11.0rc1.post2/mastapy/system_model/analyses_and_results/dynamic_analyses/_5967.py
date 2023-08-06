﻿'''_5967.py

FaceGearMeshDynamicAnalysis
'''


from mastapy.system_model.connections_and_sockets.gears import _1987
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6515
from mastapy.system_model.analyses_and_results.dynamic_analyses import _5972
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_MESH_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'FaceGearMeshDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearMeshDynamicAnalysis',)


class FaceGearMeshDynamicAnalysis(_5972.GearMeshDynamicAnalysis):
    '''FaceGearMeshDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_MESH_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearMeshDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1987.FaceGearMesh':
        '''FaceGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1987.FaceGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_load_case(self) -> '_6515.FaceGearMeshLoadCase':
        '''FaceGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6515.FaceGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase else None
