"""
AegisMesh — Policy Engine
Traces to: docs/architecture/aegismesh-design.md Section 4
"""
from typing import Tuple, Optional
from ..models.enums import Decision, WorkloadState
from ..models.schemas import EvaluateRequest, PolicyRuleSchema
from ..database.store import store


class PolicyEngine:
    def evaluate(self, request: EvaluateRequest) -> Tuple[Decision, Optional[str], str]:
        """
        Evaluates an access request against configured security policies.
        Returns: (policy_decision, matched_policy_id, explanation)
        """
        source_id = request.source.workload_id
        source_workload = store.get_workload(source_id)

        # 1. Check for Active Containment Override
        if source_workload and source_workload.state == WorkloadState.CONTAINED:
            target_id = request.destination.resource_id
            if target_id not in source_workload.allowed_dependencies:
                return (
                    Decision.BLOCK,
                    "CONTAINMENT-OVERRIDE",
                    f"BLOCKED: Workload '{source_id}' is in CONTAINED state. Egress restricted to authorized dependencies {source_workload.allowed_dependencies}.",
                )

        # 2. Iterate policies in priority order
        sorted_policies = sorted(store.policies, key=lambda p: p.priority)

        for policy in sorted_policies:
            # Check source match
            if policy.source_zone and policy.source_zone != request.source.zone:
                continue
            if policy.source_workload_id and policy.source_workload_id != source_id:
                continue

            # Check destination match
            if policy.destination_zone and policy.destination_zone != request.destination.zone:
                continue
            if policy.destination_resource_id and policy.destination_resource_id != request.destination.resource_id:
                continue

            # Check action match
            if request.action not in policy.actions:
                continue

            # Policy matched
            explanation = (
                f"Policy '{policy.name}' matched with decision {policy.decision.value}. "
                f"Mitigates {policy.threat_mitigated or 'Unauthorized Access'}."
            )
            return policy.decision, policy.id, explanation

        # 3. Default Deny Fallback
        return (
            Decision.BLOCK,
            "POL-DEFAULT-DENY",
            "BLOCKED: No explicit permissive policy found. Default-deny zero-trust rule enforced.",
        )


policy_engine = PolicyEngine()
