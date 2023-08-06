﻿'''_4165.py

RollingRingConnectionCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.connections_and_sockets import _1945
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4035
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4137
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'RollingRingConnectionCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingConnectionCompoundParametricStudyTool',)


class RollingRingConnectionCompoundParametricStudyTool(_4137.InterMountableComponentConnectionCompoundParametricStudyTool):
    '''RollingRingConnectionCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingConnectionCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_1945.RollingRingConnection':
        '''RollingRingConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1945.RollingRingConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def connection_design(self) -> '_1945.RollingRingConnection':
        '''RollingRingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1945.RollingRingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_4035.RollingRingConnectionParametricStudyTool]':
        '''List[RollingRingConnectionParametricStudyTool]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_4035.RollingRingConnectionParametricStudyTool))
        return value

    @property
    def connection_parametric_study_tool_load_cases(self) -> 'List[_4035.RollingRingConnectionParametricStudyTool]':
        '''List[RollingRingConnectionParametricStudyTool]: 'ConnectionParametricStudyToolLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionParametricStudyToolLoadCases, constructor.new(_4035.RollingRingConnectionParametricStudyTool))
        return value

    @property
    def planetaries(self) -> 'List[RollingRingConnectionCompoundParametricStudyTool]':
        '''List[RollingRingConnectionCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingConnectionCompoundParametricStudyTool))
        return value
