﻿'''_3475.py

OilSealStabilityAnalysis
'''


from mastapy.system_model.part_model import _2114
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6522
from mastapy.system_model.analyses_and_results.stability_analyses import _3432
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'OilSealStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealStabilityAnalysis',)


class OilSealStabilityAnalysis(_3432.ConnectorStabilityAnalysis):
    '''OilSealStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2114.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2114.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6522.OilSealLoadCase':
        '''OilSealLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6522.OilSealLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
