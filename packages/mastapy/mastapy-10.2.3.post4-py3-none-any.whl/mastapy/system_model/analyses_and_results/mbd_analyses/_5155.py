﻿'''_5155.py

SynchroniserSleeveMultiBodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.couplings import _2200
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6266
from mastapy.system_model.analyses_and_results.mbd_analyses import _5154
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_SLEEVE_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'SynchroniserSleeveMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserSleeveMultiBodyDynamicsAnalysis',)


class SynchroniserSleeveMultiBodyDynamicsAnalysis(_5154.SynchroniserPartMultiBodyDynamicsAnalysis):
    '''SynchroniserSleeveMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_SLEEVE_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserSleeveMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2200.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2200.SynchroniserSleeve)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6266.SynchroniserSleeveLoadCase':
        '''SynchroniserSleeveLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6266.SynchroniserSleeveLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
