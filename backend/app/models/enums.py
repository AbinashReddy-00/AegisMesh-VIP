"""
AegisMesh — Shared Enumerations
Traces to: docs/architecture/aegismesh-design.md Section 2
"""
from enum import Enum


class Decision(str, Enum):
    ALLOW = "ALLOW"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"
    ISOLATE = "ISOLATE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InfrastructureDomain(str, Enum):
    PRIVATE_DC = "PRIVATE_DC"
    AWS_CLOUD = "AWS_CLOUD"
    KUBERNETES = "KUBERNETES"


class SecurityZone(str, Enum):
    FACULTY = "FACULTY"
    APP = "APP"
    DATABASE = "DATABASE"
    MANAGEMENT = "MANAGEMENT"
    SECURITY = "SECURITY"
    DMZ = "DMZ"
    CLOUD_EDU = "CLOUD_EDU"
    CLOUD_RES = "CLOUD_RES"
    CLOUD_FIN = "CLOUD_FIN"
    CLOUD_SEC = "CLOUD_SEC"
    K8S_EDU = "K8S_EDU"
    K8S_RES = "K8S_RES"
    K8S_FIN = "K8S_FIN"
    K8S_SYS = "K8S_SYS"
    K8S_MON = "K8S_MON"


class WorkloadState(str, Enum):
    NORMAL = "NORMAL"
    SUSPICIOUS = "SUSPICIOUS"
    CONTAINED = "CONTAINED"
    RECOVERED = "RECOVERED"


class SensitivityLevel(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class ActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    CONNECT = "CONNECT"
    EXECUTE = "EXECUTE"
    ADMIN = "ADMIN"
    DEPLOY = "DEPLOY"


class ResourceType(str, Enum):
    DATABASE = "DATABASE"
    API = "API"
    SERVICE = "SERVICE"
    STORAGE = "STORAGE"
    MANAGEMENT_INTERFACE = "MANAGEMENT_INTERFACE"
