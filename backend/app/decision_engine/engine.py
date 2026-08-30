"""
AegisMesh — Decision Engine
Traces to: docs/architecture/aegismesh-design.md Section 6
"""
from datetime import datetime, timezone
import uuid
from ..models.enums import Decision, RiskLevel, InfrastructureDomain
from ..models.schemas import EvaluateRequest, EvaluateResponse, AuditLogSchema
from ..policy_engine.engine import policy_engine
from ..risk_engine.engine import risk_engine
from ..database.store import store
from ..integrations.siem_client import siem_client


class DecisionEngine:
    # Decision Matrix: [policy_decision][risk_level] -> final_decision
    DECISION_MATRIX = {
        Decision.ALLOW: {
            RiskLevel.LOW: Decision.ALLOW,
            RiskLevel.MEDIUM: Decision.ALLOW,
            RiskLevel.HIGH: Decision.RESTRICT,
            RiskLevel.CRITICAL: Decision.BLOCK,
        },
        Decision.RESTRICT: {
            RiskLevel.LOW: Decision.RESTRICT,
            RiskLevel.MEDIUM: Decision.RESTRICT,
            RiskLevel.HIGH: Decision.BLOCK,
            RiskLevel.CRITICAL: Decision.ISOLATE,
        },
        Decision.BLOCK: {
            RiskLevel.LOW: Decision.BLOCK,
            RiskLevel.MEDIUM: Decision.BLOCK,
            RiskLevel.HIGH: Decision.BLOCK,
            RiskLevel.CRITICAL: Decision.ISOLATE,
        },
        Decision.ISOLATE: {
            RiskLevel.LOW: Decision.ISOLATE,
            RiskLevel.MEDIUM: Decision.ISOLATE,
            RiskLevel.HIGH: Decision.ISOLATE,
            RiskLevel.CRITICAL: Decision.ISOLATE,
        },
    }

    def evaluate_request(self, request: EvaluateRequest) -> EvaluateResponse:
        req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

        # 1. Evaluate Policy
        policy_decision, policy_id, policy_explanation = policy_engine.evaluate(request)

        # 2. Evaluate Risk
        risk_assessment = risk_engine.compute_risk(request)

        # 3. Combine in Decision Matrix
        final_decision = self.DECISION_MATRIX.get(policy_decision, {}).get(
            risk_assessment.level, Decision.BLOCK
        )

        risk_override = final_decision != policy_decision

        # 4. Generate Human Explanation
        if risk_override:
            explanation = (
                f"Risk override applied: Policy evaluated as {policy_decision.value}, but risk level is "
                f"{risk_assessment.level.value} (Score {risk_assessment.score}/100), elevating decision to {final_decision.value}."
            )
        else:
            explanation = (
                f"Decision: {final_decision.value}. {policy_explanation} "
                f"Risk verified at {risk_assessment.level.value} ({risk_assessment.score}/100)."
            )

        threat_id = request.context.threat_id if request.context else None

        # 5. Automatically trigger Containment if verdict is ISOLATE
        if final_decision == Decision.ISOLATE:
            from ..containment.controller import containment_controller
            contain_res = containment_controller.isolate_workload(
                workload_id=request.source.workload_id,
                reason=explanation,
                threat_id=threat_id,
                namespace=request.source.namespace,
            )
            if contain_res.get("enforcement") == "REAL_KUBERNETES_NETWORKPOLICY":
                enforcement_layer = f"Calico Dynamic NetworkPolicy ({contain_res.get('policy_name')})"
            else:
                enforcement_layer = self._determine_enforcement_layer(request, final_decision)
        else:
            enforcement_layer = self._determine_enforcement_layer(request, final_decision)


        response = EvaluateResponse(
            request_id=req_id,
            decision=final_decision,
            policy_decision=policy_decision,
            risk_override=risk_override,
            risk_score=risk_assessment.score,
            risk_level=risk_assessment.level,
            policy_matched=policy_id,
            explanation=explanation,
            factors=risk_assessment.factors,
            timestamp=datetime.now(timezone.utc),
            audit_id=audit_id,
            enforcement_layer=enforcement_layer,
            threat_id=threat_id,
        )

        # 6. Record Audit Log
        actor = f"{request.source.workload_id} ({request.source.ip_address or request.source.zone.value})"
        target = f"{request.destination.resource_id} ({request.destination.zone.value})"
        store.add_audit_log(
            AuditLogSchema(
                id=audit_id,
                timestamp=response.timestamp,
                actor=actor,
                source_ip=request.source.ip_address,
                target=target,
                action=request.action.value,
                decision=final_decision,
                risk_score=risk_assessment.score,
                threat_id=threat_id,
                details=explanation,
            )
        )

        # 7. Send ALLOW/BLOCK decisions to centralized SIEM.
        # ISOLATE is logged by the Containment Controller after quarantine is applied.
        if final_decision != Decision.ISOLATE:
            siem_client.log_event(
                decision=final_decision,
                risk_score=risk_assessment.score,
                severity=risk_assessment.level,
                source_domain=request.source.domain.value,
                source_workload=request.source.workload_id,
                target=request.destination.resource_id,
                containment_status="NONE",
                threat_id=threat_id,
            )

        return response

    def _determine_enforcement_layer(self, req: EvaluateRequest, decision: Decision) -> str:
        src_dom = req.source.domain
        if src_dom == InfrastructureDomain.PRIVATE_DC:
            return f"Cisco Core Switch SVI Ingress ACL ({req.source.zone.value}-ACCESS)"
        elif src_dom == InfrastructureDomain.AWS_CLOUD:
            return f"AWS Security Group & VPC Routing Boundary ({req.source.vpc_id or 'VPC-A'})"
        elif src_dom == InfrastructureDomain.KUBERNETES:
            return f"Calico Default-Deny NetworkPolicy ({req.source.namespace or 'namespace'})"
        return "AegisMesh Central Decision Plane"


decision_engine = DecisionEngine()

