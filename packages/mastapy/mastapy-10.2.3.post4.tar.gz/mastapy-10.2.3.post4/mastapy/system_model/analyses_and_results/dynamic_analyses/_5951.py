﻿'''_5951.py

RollingRingConnectionDynamicAnalysis
'''


from typing import List

from mastapy.system_model.connections_and_sockets import _1908
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6240
from mastapy.system_model.analyses_and_results.dynamic_analyses import _5926
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CONNECTION_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'RollingRingConnectionDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingConnectionDynamicAnalysis',)


class RollingRingConnectionDynamicAnalysis(_5926.InterMountableComponentConnectionDynamicAnalysis):
    '''RollingRingConnectionDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CONNECTION_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingConnectionDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_1908.RollingRingConnection':
        '''RollingRingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1908.RollingRingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def connection_load_case(self) -> '_6240.RollingRingConnectionLoadCase':
        '''RollingRingConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6240.RollingRingConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase else None

    @property
    def planetaries(self) -> 'List[RollingRingConnectionDynamicAnalysis]':
        '''List[RollingRingConnectionDynamicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingConnectionDynamicAnalysis))
        return value
