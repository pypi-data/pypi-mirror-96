﻿'''_3771.py

StraightBevelDiffGearMeshPowerFlow
'''


from mastapy.system_model.connections_and_sockets.gears import _1979
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6558
from mastapy.gears.rating.straight_bevel_diff import _355
from mastapy.system_model.analyses_and_results.power_flows import _3679
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_MESH_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'StraightBevelDiffGearMeshPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearMeshPowerFlow',)


class StraightBevelDiffGearMeshPowerFlow(_3679.BevelGearMeshPowerFlow):
    '''StraightBevelDiffGearMeshPowerFlow

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_MESH_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearMeshPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1979.StraightBevelDiffGearMesh':
        '''StraightBevelDiffGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1979.StraightBevelDiffGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_load_case(self) -> '_6558.StraightBevelDiffGearMeshLoadCase':
        '''StraightBevelDiffGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6558.StraightBevelDiffGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase else None

    @property
    def rating(self) -> '_355.StraightBevelDiffGearMeshRating':
        '''StraightBevelDiffGearMeshRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_355.StraightBevelDiffGearMeshRating)(self.wrapped.Rating) if self.wrapped.Rating else None

    @property
    def component_detailed_analysis(self) -> '_355.StraightBevelDiffGearMeshRating':
        '''StraightBevelDiffGearMeshRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_355.StraightBevelDiffGearMeshRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis else None
