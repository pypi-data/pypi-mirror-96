﻿'''_6229.py

PlanetaryConnectionCriticalSpeedAnalysis
'''


from mastapy.system_model.connections_and_sockets import _1940
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6528
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6243
from mastapy._internal.python_net import python_net_import

_PLANETARY_CONNECTION_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'PlanetaryConnectionCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryConnectionCriticalSpeedAnalysis',)


class PlanetaryConnectionCriticalSpeedAnalysis(_6243.ShaftToMountableComponentConnectionCriticalSpeedAnalysis):
    '''PlanetaryConnectionCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_CONNECTION_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryConnectionCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1940.PlanetaryConnection':
        '''PlanetaryConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1940.PlanetaryConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_load_case(self) -> '_6528.PlanetaryConnectionLoadCase':
        '''PlanetaryConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6528.PlanetaryConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase else None
