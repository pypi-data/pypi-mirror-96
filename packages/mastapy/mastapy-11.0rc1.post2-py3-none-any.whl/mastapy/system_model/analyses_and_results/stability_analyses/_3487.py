﻿'''_3487.py

GuideDxfModelStabilityAnalysis
'''


from mastapy.system_model.part_model import _2128
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6526
from mastapy.system_model.analyses_and_results.stability_analyses import _3450
from mastapy._internal.python_net import python_net_import

_GUIDE_DXF_MODEL_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'GuideDxfModelStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideDxfModelStabilityAnalysis',)


class GuideDxfModelStabilityAnalysis(_3450.ComponentStabilityAnalysis):
    '''GuideDxfModelStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _GUIDE_DXF_MODEL_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideDxfModelStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2128.GuideDxfModel':
        '''GuideDxfModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2128.GuideDxfModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6526.GuideDxfModelLoadCase':
        '''GuideDxfModelLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6526.GuideDxfModelLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
