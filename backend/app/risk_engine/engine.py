"""
AegisMesh — Risk Engine
Traces to: docs/architecture/aegismesh-design.md Section 5
"""
from ..models.enums import (
    RiskLevel,
    SecurityZone,
    SensitivityLevel,
    ActionType,
)
from ..models.schemas import EvaluateRequest, RiskFactorDetail, RiskAssessment
from ..database.store import store


class RiskEngine:
    def compute_risk(self, request: EvaluateRequest) -> RiskAssessment:
        factors = []

        # 1. Factor 1: Source Trust (Weight 20%)
        source_workload = store.get_workload(request.source.workload_id)
        raw_trust = source_workload.trust_score if source_workload else 50
        is_anom = bool(request.context and request.context.is_anomaly)
        if is_anom:
            # Active anomaly degrades effective trust score to high risk
            trust_risk_score = max(80, 100 - raw_trust)
        else:
            trust_risk_score = max(0, 100 - raw_trust)

        f1 = RiskFactorDetail(
            name="Source Workload Trust",
            score=trust_risk_score,
            weight=0.20,
            weighted_score=round(trust_risk_score * 0.20, 2),
            description=f"Workload trust baseline is {raw_trust}/100 (anomaly penalty yields risk score {trust_risk_score}).",
        )
        factors.append(f1)

        # 2. Factor 2: Destination Sensitivity (Weight 25%)
        sens_map = {
            SensitivityLevel.RESTRICTED: 95,
            SensitivityLevel.CONFIDENTIAL: 75,
            SensitivityLevel.INTERNAL: 40,
            SensitivityLevel.PUBLIC: 10,
        }
        sens_score = sens_map.get(request.destination.sensitivity, 50)
        f2 = RiskFactorDetail(
            name="Destination Resource Sensitivity",
            score=sens_score,
            weight=0.25,
            weighted_score=round(sens_score * 0.25, 2),
            description=f"Target sensitivity is {request.destination.sensitivity.value} (base risk {sens_score}).",
        )
        factors.append(f2)

        # 3. Factor 3: Action Severity (Weight 15%)
        act_map = {
            ActionType.ADMIN: 95,
            ActionType.EXECUTE: 85,
            ActionType.DEPLOY: 75,
            ActionType.WRITE: 70,
            ActionType.CONNECT: 35,
            ActionType.READ: 25,
        }
        act_score = act_map.get(request.action, 40)
        f3 = RiskFactorDetail(
            name="Requested Action Severity",
            score=act_score,
            weight=0.15,
            weighted_score=round(act_score * 0.15, 2),
            description=f"Action '{request.action.value}' carries operational impact score {act_score}.",
        )
        factors.append(f3)

        # 4. Factor 4: Cross-Zone Penalty (Weight 15%)
        zone_penalty = self._compute_zone_penalty(request.source.zone, request.destination.zone)
        f4 = RiskFactorDetail(
            name="Cross-Zone Boundary Penalty",
            score=zone_penalty,
            weight=0.15,
            weighted_score=round(zone_penalty * 0.15, 2),
            description=f"Traversing from {request.source.zone.value} to {request.destination.zone.value} incurs zone penalty {zone_penalty}.",
        )
        factors.append(f4)

        # 5. Factor 5: Behavioral Anomaly / Threat Context (Weight 15%)
        anom_score = 95 if is_anom else 10
        f5 = RiskFactorDetail(
            name="Behavioral Anomaly & Threat Indicator",
            score=anom_score,
            weight=0.15,
            weighted_score=round(anom_score * 0.15, 2),
            description="Elevated anomaly indicator detected (Threat Correlation)." if is_anom else "Behavior aligns with baseline activity.",
        )
        factors.append(f5)

        # 6. Factor 6: Time Context (Weight 10%)
        time_score = 40 if is_anom else 15
        f6 = RiskFactorDetail(
            name="Temporal & Environment Context",
            score=time_score,
            weight=0.10,
            weighted_score=round(time_score * 0.10, 2),
            description=f"Environment context modifier ({time_score}).",
        )
        factors.append(f6)

        # Total Weighted Sum
        total_score = sum(f.weighted_score for f in factors)
        normalized_score = int(min(100, max(0, round(total_score))))

        # Classify Level
        if normalized_score <= 30:
            level = RiskLevel.LOW
        elif normalized_score <= 60:
            level = RiskLevel.MEDIUM
        elif normalized_score <= 80:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        explanation = (
            f"Computed risk score: {normalized_score}/100 ({level.value}). "
            f"Key contributors: Destination ({sens_score}/100), Cross-Zone ({zone_penalty}/100), Anomaly ({anom_score}/100)."
        )

        return RiskAssessment(
            score=normalized_score,
            level=level,
            factors=factors,
            explanation=explanation,
        )

    def _compute_zone_penalty(self, src: SecurityZone, dst: SecurityZone) -> int:
        if src == dst:
            return 0
        # High-security target boundaries
        if dst in [SecurityZone.MANAGEMENT, SecurityZone.CLOUD_SEC, SecurityZone.K8S_SYS]:
            return 85
        if dst in [SecurityZone.DATABASE, SecurityZone.CLOUD_FIN, SecurityZone.K8S_FIN]:
            return 90
        # Normal cross-zone boundary
        return 50


risk_engine = RiskEngine()
