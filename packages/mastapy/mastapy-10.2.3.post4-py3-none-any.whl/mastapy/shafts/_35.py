﻿'''_35.py

ShaftSectionEndDamageResults
'''


from typing import List

from mastapy.nodal_analysis import _1407
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.shafts import (
    _15, _40, _16, _27
)
from mastapy.materials import _83
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_SECTION_END_DAMAGE_RESULTS = python_net_import('SMT.MastaAPI.Shafts', 'ShaftSectionEndDamageResults')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftSectionEndDamageResults',)


class ShaftSectionEndDamageResults(_0.APIBase):
    '''ShaftSectionEndDamageResults

    This is a mastapy class.
    '''

    TYPE = _SHAFT_SECTION_END_DAMAGE_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftSectionEndDamageResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def section_end(self) -> '_1407.SectionEnd':
        '''SectionEnd: 'SectionEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.SectionEnd)
        return constructor.new(_1407.SectionEnd)(value) if value else None

    @property
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Offset

    @property
    def outer_radius_to_achieve_shaft_fatigue_safety_factor_requirement(self) -> 'float':
        '''float: 'OuterRadiusToAchieveShaftFatigueSafetyFactorRequirement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterRadiusToAchieveShaftFatigueSafetyFactorRequirement

    @property
    def outer_diameter_to_achieve_fatigue_safety_factor_requirement(self) -> 'float':
        '''float: 'OuterDiameterToAchieveFatigueSafetyFactorRequirement' is the original name of this property.'''

        return self.wrapped.OuterDiameterToAchieveFatigueSafetyFactorRequirement

    @outer_diameter_to_achieve_fatigue_safety_factor_requirement.setter
    def outer_diameter_to_achieve_fatigue_safety_factor_requirement(self, value: 'float'):
        self.wrapped.OuterDiameterToAchieveFatigueSafetyFactorRequirement = float(value) if value else 0.0

    @property
    def displacement_radial_magnitude(self) -> 'float':
        '''float: 'DisplacementRadialMagnitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DisplacementRadialMagnitude

    @property
    def displacement_radial_tilt_magnitude(self) -> 'float':
        '''float: 'DisplacementRadialTiltMagnitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DisplacementRadialTiltMagnitude

    @property
    def displacement_axial(self) -> 'float':
        '''float: 'DisplacementAxial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DisplacementAxial

    @property
    def displacement_twist(self) -> 'float':
        '''float: 'DisplacementTwist' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DisplacementTwist

    @property
    def force_axial(self) -> 'float':
        '''float: 'ForceAxial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceAxial

    @property
    def force_torque(self) -> 'float':
        '''float: 'ForceTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceTorque

    @property
    def force_radial_magnitude(self) -> 'float':
        '''float: 'ForceRadialMagnitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceRadialMagnitude

    @property
    def static_safety_factor(self) -> 'float':
        '''float: 'StaticSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSafetyFactor

    @property
    def fatigue_safety_factor(self) -> 'float':
        '''float: 'FatigueSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactor

    @property
    def fatigue_damage(self) -> 'float':
        '''float: 'FatigueDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueDamage

    @property
    def fatigue_safety_factor_for_infinite_life(self) -> 'float':
        '''float: 'FatigueSafetyFactorForInfiniteLife' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorForInfiniteLife

    @property
    def shaft_reliability(self) -> 'float':
        '''float: 'ShaftReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftReliability

    @property
    def reliability_for_infinite_life(self) -> 'float':
        '''float: 'ReliabilityForInfiniteLife' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityForInfiniteLife

    @property
    def total_number_of_cycles(self) -> 'float':
        '''float: 'TotalNumberOfCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalNumberOfCycles

    @property
    def equivalent_alternating_stress(self) -> 'float':
        '''float: 'EquivalentAlternatingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentAlternatingStress

    @property
    def stress_concentration_factors(self) -> '_15.ShaftAxialBendingTorsionalComponentValues':
        '''ShaftAxialBendingTorsionalComponentValues: 'StressConcentrationFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_15.ShaftAxialBendingTorsionalComponentValues)(self.wrapped.StressConcentrationFactors) if self.wrapped.StressConcentrationFactors else None

    @property
    def sn_curve(self) -> '_83.SNCurve':
        '''SNCurve: 'SNCurve' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_83.SNCurve)(self.wrapped.SNCurve) if self.wrapped.SNCurve else None

    @property
    def din743201212_component_fatigue_limit_under_reversed_stress_sigma_zd_wk_sigma_bwk_tau_twk(self) -> '_40.StressMeasurementShaftAxialBendingTorsionalComponentValues':
        '''StressMeasurementShaftAxialBendingTorsionalComponentValues: 'DIN743201212ComponentFatigueLimitUnderReversedStressSigmaZdWKSigmaBWKTauTWK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_40.StressMeasurementShaftAxialBendingTorsionalComponentValues)(self.wrapped.DIN743201212ComponentFatigueLimitUnderReversedStressSigmaZdWKSigmaBWKTauTWK) if self.wrapped.DIN743201212ComponentFatigueLimitUnderReversedStressSigmaZdWKSigmaBWKTauTWK else None

    @property
    def din743201212_component_yield_point_sigma_zd_fk_sigma_bfk_tau_tfk(self) -> '_40.StressMeasurementShaftAxialBendingTorsionalComponentValues':
        '''StressMeasurementShaftAxialBendingTorsionalComponentValues: 'DIN743201212ComponentYieldPointSigmaZdFKSigmaBFKTauTFK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_40.StressMeasurementShaftAxialBendingTorsionalComponentValues)(self.wrapped.DIN743201212ComponentYieldPointSigmaZdFKSigmaBFKTauTFK) if self.wrapped.DIN743201212ComponentYieldPointSigmaZdFKSigmaBFKTauTFK else None

    @property
    def din743201212_influence_factor_for_mean_stress_sensitivity_psi_sigma_k_psi_tau_k(self) -> '_15.ShaftAxialBendingTorsionalComponentValues':
        '''ShaftAxialBendingTorsionalComponentValues: 'DIN743201212InfluenceFactorForMeanStressSensitivityPsiSigmaKPsiTauK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_15.ShaftAxialBendingTorsionalComponentValues)(self.wrapped.DIN743201212InfluenceFactorForMeanStressSensitivityPsiSigmaKPsiTauK) if self.wrapped.DIN743201212InfluenceFactorForMeanStressSensitivityPsiSigmaKPsiTauK else None

    @property
    def fkm_guideline_6th_edition_2012_cyclic_degree_of_utilization_for_finite_life(self) -> '_16.ShaftAxialBendingXBendingYTorsionalComponentValues':
        '''ShaftAxialBendingXBendingYTorsionalComponentValues: 'FKMGuideline6thEdition2012CyclicDegreeOfUtilizationForFiniteLife' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_16.ShaftAxialBendingXBendingYTorsionalComponentValues)(self.wrapped.FKMGuideline6thEdition2012CyclicDegreeOfUtilizationForFiniteLife) if self.wrapped.FKMGuideline6thEdition2012CyclicDegreeOfUtilizationForFiniteLife else None

    @property
    def fkm_guideline_6th_edition_2012_cyclic_degree_of_utilization_for_infinite_life(self) -> '_16.ShaftAxialBendingXBendingYTorsionalComponentValues':
        '''ShaftAxialBendingXBendingYTorsionalComponentValues: 'FKMGuideline6thEdition2012CyclicDegreeOfUtilizationForInfiniteLife' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_16.ShaftAxialBendingXBendingYTorsionalComponentValues)(self.wrapped.FKMGuideline6thEdition2012CyclicDegreeOfUtilizationForInfiniteLife) if self.wrapped.FKMGuideline6thEdition2012CyclicDegreeOfUtilizationForInfiniteLife else None

    @property
    def sn_curve_axial(self) -> '_83.SNCurve':
        '''SNCurve: 'SNCurveAxial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_83.SNCurve)(self.wrapped.SNCurveAxial) if self.wrapped.SNCurveAxial else None

    @property
    def sn_curve_bending_x(self) -> '_83.SNCurve':
        '''SNCurve: 'SNCurveBendingX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_83.SNCurve)(self.wrapped.SNCurveBendingX) if self.wrapped.SNCurveBendingX else None

    @property
    def sn_curve_bending_y(self) -> '_83.SNCurve':
        '''SNCurve: 'SNCurveBendingY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_83.SNCurve)(self.wrapped.SNCurveBendingY) if self.wrapped.SNCurveBendingY else None

    @property
    def sn_curve_torsional(self) -> '_83.SNCurve':
        '''SNCurve: 'SNCurveTorsional' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_83.SNCurve)(self.wrapped.SNCurveTorsional) if self.wrapped.SNCurveTorsional else None

    @property
    def stress_cycles(self) -> 'List[_27.ShaftPointStressCycleReporting]':
        '''List[ShaftPointStressCycleReporting]: 'StressCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StressCycles, constructor.new(_27.ShaftPointStressCycleReporting))
        return value

    @property
    def din743201212_stress_amplitude_of_component_fatigue_strength_sigma_zd_adk_sigma_badk_tau_tadk(self) -> 'List[_40.StressMeasurementShaftAxialBendingTorsionalComponentValues]':
        '''List[StressMeasurementShaftAxialBendingTorsionalComponentValues]: 'DIN743201212StressAmplitudeOfComponentFatigueStrengthSigmaZdADKSigmaBADKTauTADK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.DIN743201212StressAmplitudeOfComponentFatigueStrengthSigmaZdADKSigmaBADKTauTADK, constructor.new(_40.StressMeasurementShaftAxialBendingTorsionalComponentValues))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReportNames

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else None)

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else None)

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else None)

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else None, file_path if file_path else None)

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else None, file_path if file_path else None)

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else None, file_path if file_path else None)

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else None)
        return method_result
