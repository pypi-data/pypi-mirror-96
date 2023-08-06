﻿'''_6217.py

KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2185
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6513
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6215, _6216, _6214
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis',)


class KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis(_6214.KlingelnbergCycloPalloidConicalGearSetCriticalSpeedAnalysis):
    '''KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2185.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2185.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6513.KlingelnbergCycloPalloidHypoidGearSetLoadCase':
        '''KlingelnbergCycloPalloidHypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6513.KlingelnbergCycloPalloidHypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None

    @property
    def klingelnberg_cyclo_palloid_hypoid_gears_critical_speed_analysis(self) -> 'List[_6215.KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis]: 'KlingelnbergCycloPalloidHypoidGearsCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearsCriticalSpeedAnalysis, constructor.new(_6215.KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes_critical_speed_analysis(self) -> 'List[_6216.KlingelnbergCycloPalloidHypoidGearMeshCriticalSpeedAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshCriticalSpeedAnalysis]: 'KlingelnbergCycloPalloidHypoidMeshesCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshesCriticalSpeedAnalysis, constructor.new(_6216.KlingelnbergCycloPalloidHypoidGearMeshCriticalSpeedAnalysis))
        return value
