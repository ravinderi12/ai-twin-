import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index, Enum
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(128), nullable=True)
    role = Column(String(32), default="analyst", nullable=False)  # admin, analyst, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(128), index=True, nullable=True)
    ip_address = Column(String(64), index=True, nullable=False)
    mac_address = Column(String(32), nullable=True)
    os_name = Column(String(128), nullable=True)
    os_version = Column(String(64), nullable=True)
    asset_type = Column(String(64), default="server", nullable=False)  # gateway, server, workstation, database, firewall, router
    criticality = Column(String(32), default="MEDIUM", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    environment = Column(String(64), default="internal", nullable=False)  # dmz, internal, cloud, management, external
    subnet = Column(String(64), index=True, nullable=True)  # e.g., 192.168.1.0/24
    is_isolated = Column(Boolean, default=False, nullable=False)
    is_perimeter = Column(Boolean, default=False, nullable=False)  # Directly exposed to public/gateway
    business_impact_score = Column(Float, default=50.0, nullable=False)  # 1 to 100
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    services = relationship("ServicePort", back_populates="asset", cascade="all, delete-orphan")
    findings = relationship("VulnerabilityFinding", back_populates="asset", cascade="all, delete-orphan")
    outbound_relationships = relationship("NetworkRelationship", foreign_keys="NetworkRelationship.source_asset_id", back_populates="source_asset", cascade="all, delete-orphan")
    inbound_relationships = relationship("NetworkRelationship", foreign_keys="NetworkRelationship.target_asset_id", back_populates="target_asset", cascade="all, delete-orphan")


class ServicePort(Base):
    __tablename__ = "service_ports"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    port = Column(Integer, nullable=False)
    protocol = Column(String(16), default="tcp", nullable=False)  # tcp, udp
    service_name = Column(String(64), nullable=True)  # http, ssh, mysql, rdp, etc.
    product = Column(String(128), nullable=True)  # Apache, OpenSSH, MySQL
    version = Column(String(64), nullable=True)  # 2.4.49, 8.2p1
    banner = Column(Text, nullable=True)
    state = Column(String(32), default="open", nullable=False)  # open, filtered, closed
    is_exposed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    asset = relationship("Asset", back_populates="services")
    findings = relationship("VulnerabilityFinding", back_populates="service", cascade="all, delete-orphan")


class NetworkRelationship(Base):
    __tablename__ = "network_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(64), default="can_connect", nullable=False)  # can_connect, routes_to, manages, trusts, parent_child
    protocol = Column(String(16), default="tcp", nullable=True)
    port = Column(Integer, nullable=True)
    is_inferred = Column(Boolean, default=False, nullable=False)
    confidence = Column(String(32), default="HIGH", nullable=False)  # HIGH, MEDIUM, LOW
    weight = Column(Float, default=1.0, nullable=False)  # Traversal cost
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    source_asset = relationship("Asset", foreign_keys=[source_asset_id], back_populates="outbound_relationships")
    target_asset = relationship("Asset", foreign_keys=[target_asset_id], back_populates="inbound_relationships")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    assessment_type = Column(String(64), default="simulated_demo", nullable=False)  # imported_xml, imported_json, simulated_demo, live_nmap
    target_scope = Column(String(255), nullable=True)
    status = Column(String(32), default="completed", nullable=False)  # pending, running, completed, failed
    total_assets_found = Column(Integer, default=0, nullable=False)
    total_vulns_found = Column(Integer, default=0, nullable=False)
    overall_risk_score = Column(Float, default=0.0, nullable=False)
    execution_duration_seconds = Column(Float, default=0.0, nullable=False)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    findings = relationship("VulnerabilityFinding", back_populates="assessment", cascade="all, delete-orphan")
    attack_paths = relationship("SimulatedAttackPath", back_populates="assessment", cascade="all, delete-orphan")
    remediations = relationship("RemediationRecommendation", back_populates="assessment", cascade="all, delete-orphan")
    scenarios = relationship("RemediationScenario", back_populates="assessment", cascade="all, delete-orphan")


class VulnerabilityFinding(Base):
    __tablename__ = "vulnerability_findings"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("service_ports.id", ondelete="SET NULL"), nullable=True, index=True)
    cve_id = Column(String(32), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cvss_v3_score = Column(Float, default=0.0, nullable=False)
    cvss_v3_severity = Column(String(32), default="MEDIUM", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW, NONE
    cvss_vector = Column(String(128), nullable=True)
    reference_url = Column(String(512), nullable=True)
    source = Column(String(64), default="NVD", nullable=False)  # NVD, Nmap Script, Simulated Intel, Manual Audit
    match_type = Column(String(64), default="version_heuristic", nullable=False)  # version_heuristic, confirmed_signature, simulated_intel
    reachability_status = Column(String(64), default="subnet_reachable", nullable=False)  # internet_reachable, subnet_reachable, isolated
    raw_score = Column(Float, default=0.0, nullable=False)
    contextual_risk_score = Column(Float, default=0.0, nullable=False)
    risk_factors_json = Column(Text, nullable=True)  # JSON breakdown: reachability, asset_impact, exploitability, confidence
    remediation_advice = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    assessment = relationship("Assessment", back_populates="findings")
    asset = relationship("Asset", back_populates="findings")
    service = relationship("ServicePort", back_populates="findings")


class CVECacheRecord(Base):
    __tablename__ = "cve_cache"

    cve_id = Column(String(32), primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    cvss_v3_score = Column(Float, default=0.0, nullable=False)
    cvss_v3_severity = Column(String(32), default="MEDIUM", nullable=False)
    cvss_vector = Column(String(128), nullable=True)
    published_date = Column(String(64), nullable=True)
    last_modified_date = Column(String(64), nullable=True)
    reference_urls_json = Column(Text, nullable=True)
    cached_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class SimulatedAttackPath(Base):
    __tablename__ = "simulated_attack_paths"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(128), nullable=False)
    start_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    target_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    algorithm_used = Column(String(32), default="Dijkstra", nullable=False)  # BFS, Dijkstra
    total_path_cost = Column(Float, default=0.0, nullable=False)
    hop_count = Column(Integer, default=0, nullable=False)
    total_path_risk = Column(Float, default=0.0, nullable=False)
    path_nodes_json = Column(Text, nullable=False)  # Ordered list of asset IDs
    path_steps_json = Column(Text, nullable=False)  # Detailed steps with rationale, vulns, relationships
    mitre_tactics_json = Column(Text, nullable=True)  # MITRE ATT&CK techniques associated
    bottleneck_asset_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    assessment = relationship("Assessment", back_populates="attack_paths")


class RemediationRecommendation(Base):
    __tablename__ = "remediation_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True, index=True)
    finding_id = Column(Integer, ForeignKey("vulnerability_findings.id", ondelete="SET NULL"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    action_description = Column(Text, nullable=False)
    priority = Column(String(32), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(32), default="PLANNED", nullable=False)  # PLANNED, IN_PROGRESS, RESOLVED
    risk_before = Column(Float, default=0.0, nullable=False)
    risk_after = Column(Float, default=0.0, nullable=False)
    risk_reduction_estimate = Column(Float, default=0.0, nullable=False)
    affected_attack_paths_count = Column(Integer, default=0, nullable=False)
    expected_security_benefit = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    assessment = relationship("Assessment", back_populates="remediations")


class RemediationScenario(Base):
    __tablename__ = "remediation_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    baseline_risk_score = Column(Float, default=0.0, nullable=False)
    simulated_risk_score = Column(Float, default=0.0, nullable=False)
    risk_reduction_percentage = Column(Float, default=0.0, nullable=False)
    eliminated_paths_count = Column(Integer, default=0, nullable=False)
    remaining_paths_count = Column(Integer, default=0, nullable=False)
    patches_applied_json = Column(Text, nullable=False)  # Finding IDs or CVEs patched in this simulation
    scenario_details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    assessment = relationship("Assessment", back_populates="scenarios")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(64), nullable=False)  # SCAN_INITIATED, ASSET_IMPORTED, SCENARIO_RUN, CVE_QUERIED, etc.
    target_type = Column(String(64), nullable=True)
    target_id = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
