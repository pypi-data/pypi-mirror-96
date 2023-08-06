﻿'''_3890.py

RootAssemblyCompoundPowerFlow
'''


from mastapy.system_model.analyses_and_results.load_case_groups import (
    _5283, _5281, _5286, _5287,
    _5291
)
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.power_flows.compound import _3803
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'RootAssemblyCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyCompoundPowerFlow',)


class RootAssemblyCompoundPowerFlow(_3803.AssemblyCompoundPowerFlow):
    '''RootAssemblyCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def compound_static_load(self) -> '_5283.AbstractStaticLoadCaseGroup':
        '''AbstractStaticLoadCaseGroup: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5283.AbstractStaticLoadCaseGroup.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to AbstractStaticLoadCaseGroup. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad else None

    @property
    def compound_static_load_of_type_abstract_design_state_load_case_group(self) -> '_5281.AbstractDesignStateLoadCaseGroup':
        '''AbstractDesignStateLoadCaseGroup: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5281.AbstractDesignStateLoadCaseGroup.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to AbstractDesignStateLoadCaseGroup. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad else None

    @property
    def compound_static_load_of_type_design_state(self) -> '_5286.DesignState':
        '''DesignState: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5286.DesignState.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to DesignState. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad else None

    @property
    def compound_static_load_of_type_duty_cycle(self) -> '_5287.DutyCycle':
        '''DutyCycle: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5287.DutyCycle.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to DutyCycle. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad else None

    @property
    def compound_static_load_of_type_sub_group_in_single_design_state(self) -> '_5291.SubGroupInSingleDesignState':
        '''SubGroupInSingleDesignState: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5291.SubGroupInSingleDesignState.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to SubGroupInSingleDesignState. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad else None

    def set_face_widths_for_specified_safety_factors(self):
        ''' 'SetFaceWidthsForSpecifiedSafetyFactors' is the original name of this method.'''

        self.wrapped.SetFaceWidthsForSpecifiedSafetyFactors()
