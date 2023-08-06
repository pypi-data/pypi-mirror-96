﻿'''_3463.py

KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis
'''


from mastapy.system_model.connections_and_sockets.gears import _1972, _1973, _1974
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.stability_analyses import _3428
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis',)


class KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis(_3428.ConicalGearMeshStabilityAnalysis):
    '''KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1972.KlingelnbergCycloPalloidConicalGearMesh':
        '''KlingelnbergCycloPalloidConicalGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1972.KlingelnbergCycloPalloidConicalGearMesh.TYPE not in self.wrapped.ConnectionDesign.__class__.__mro__:
            raise CastException('Failed to cast connection_design to KlingelnbergCycloPalloidConicalGearMesh. Expected: {}.'.format(self.wrapped.ConnectionDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectionDesign.__class__)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_design_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh(self) -> '_1973.KlingelnbergCycloPalloidHypoidGearMesh':
        '''KlingelnbergCycloPalloidHypoidGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1973.KlingelnbergCycloPalloidHypoidGearMesh.TYPE not in self.wrapped.ConnectionDesign.__class__.__mro__:
            raise CastException('Failed to cast connection_design to KlingelnbergCycloPalloidHypoidGearMesh. Expected: {}.'.format(self.wrapped.ConnectionDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectionDesign.__class__)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_design_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(self) -> '_1974.KlingelnbergCycloPalloidSpiralBevelGearMesh':
        '''KlingelnbergCycloPalloidSpiralBevelGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1974.KlingelnbergCycloPalloidSpiralBevelGearMesh.TYPE not in self.wrapped.ConnectionDesign.__class__.__mro__:
            raise CastException('Failed to cast connection_design to KlingelnbergCycloPalloidSpiralBevelGearMesh. Expected: {}.'.format(self.wrapped.ConnectionDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectionDesign.__class__)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None
