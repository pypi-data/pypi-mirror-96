﻿'''_6259.py

SynchroniserCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model.couplings import _2247
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6566
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6244
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'SynchroniserCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserCriticalSpeedAnalysis',)


class SynchroniserCriticalSpeedAnalysis(_6244.SpecialisedAssemblyCriticalSpeedAnalysis):
    '''SynchroniserCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2247.Synchroniser':
        '''Synchroniser: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2247.Synchroniser)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6566.SynchroniserLoadCase':
        '''SynchroniserLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6566.SynchroniserLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None
