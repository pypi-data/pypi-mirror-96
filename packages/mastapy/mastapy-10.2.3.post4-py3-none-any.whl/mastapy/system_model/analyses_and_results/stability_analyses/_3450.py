﻿'''_3450.py

FaceGearMeshStabilityAnalysis
'''


from mastapy.system_model.connections_and_sockets.gears import _1965
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6482
from mastapy.system_model.analyses_and_results.stability_analyses import _3455
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_MESH_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'FaceGearMeshStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearMeshStabilityAnalysis',)


class FaceGearMeshStabilityAnalysis(_3455.GearMeshStabilityAnalysis):
    '''FaceGearMeshStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_MESH_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearMeshStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1965.FaceGearMesh':
        '''FaceGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1965.FaceGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_load_case(self) -> '_6482.FaceGearMeshLoadCase':
        '''FaceGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6482.FaceGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase else None
