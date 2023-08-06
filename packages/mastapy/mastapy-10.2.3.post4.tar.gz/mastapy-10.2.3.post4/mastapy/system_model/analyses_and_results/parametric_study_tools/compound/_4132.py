﻿'''_4132.py

GearSetCompoundParametricStudyTool
'''


from mastapy.gears.rating import _322
from mastapy._internal import constructor
from mastapy.gears.rating.worm import _335
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.face import _409
from mastapy.gears.rating.cylindrical import _421
from mastapy.gears.rating.conical import _488
from mastapy.gears.rating.concept import _499
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4170
from mastapy._internal.python_net import python_net_import

_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'GearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetCompoundParametricStudyTool',)


class GearSetCompoundParametricStudyTool(_4170.SpecialisedAssemblyCompoundParametricStudyTool):
    '''GearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_set_duty_cycle_results(self) -> '_322.GearSetDutyCycleRating':
        '''GearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _322.GearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to GearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults else None

    @property
    def gear_set_duty_cycle_results_of_type_worm_gear_set_duty_cycle_rating(self) -> '_335.WormGearSetDutyCycleRating':
        '''WormGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _335.WormGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to WormGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults else None

    @property
    def gear_set_duty_cycle_results_of_type_face_gear_set_duty_cycle_rating(self) -> '_409.FaceGearSetDutyCycleRating':
        '''FaceGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _409.FaceGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to FaceGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults else None

    @property
    def gear_set_duty_cycle_results_of_type_cylindrical_gear_set_duty_cycle_rating(self) -> '_421.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _421.CylindricalGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to CylindricalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults else None

    @property
    def gear_set_duty_cycle_results_of_type_conical_gear_set_duty_cycle_rating(self) -> '_488.ConicalGearSetDutyCycleRating':
        '''ConicalGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _488.ConicalGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to ConicalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults else None

    @property
    def gear_set_duty_cycle_results_of_type_concept_gear_set_duty_cycle_rating(self) -> '_499.ConceptGearSetDutyCycleRating':
        '''ConceptGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _499.ConceptGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to ConceptGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults else None
