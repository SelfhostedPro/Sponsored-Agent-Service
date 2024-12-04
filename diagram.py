# Diagram Docs: https://diagrams.mingrammer.com/docs/getting-started/installation

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.network import Istio
from diagrams.gcp.network import CDN, Armor, LoadBalancing
from diagrams.onprem.client import Users

# Custom
from diagrams.custom import Custom
from urllib.request import urlretrieve


# External
from diagrams.saas.communication import Twilio

# Data
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.compute import Server

# Deployment
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.network import Service


# Observability
from diagrams.elastic.agent import Agent
from diagrams.elastic.elasticsearch import Elasticsearch, Stack
from diagrams.elastic.observability import Metrics, Logs, Observability

# Workflows
from diagrams.onprem.gitops import Argocd

# Download custom logos
envoy_url = "https://icon.icepanel.io/Technology/png-512/Envoy.png"
envoy_logo = "logos/envoy.svg"
urlretrieve(envoy_url, envoy_logo)


# from diagrams.elastic
graph_attr = {"concentrate": "false", "splines": "spline"}

edge_attr = {
    "minlen": "2",
}


def data_edge(label: str, **attrs: dict[str, str]):
    return Edge(label=label, color="red", **attrs)


def metrics_edge(label: str, **attrs: dict[str, str]):
    return Edge(label=label, color="orange", style="dashed", **attrs)


def management_edge(label: str, **attrs: dict[str, str]):
    return Edge(label=label, color="blue", style="dotted", **attrs)


def security_edge(label: str, **attrs: dict[str, str]):
    return Edge(label=label, color="blue", style="dashed", **attrs)


with Diagram(
    "Sponsored Agent Service",
    show=False,
    graph_attr=graph_attr,
    direction="LR",
    edge_attr=edge_attr,
):
    with Cluster("Clients"):
        users = Users("Users")
        agents = Users("Agents")

    with Cluster("External Services"):
        sendgrid = Twilio("sendgrid")

    with Cluster("GCP"):
        cdn = CDN("Cloud CDN")
        armor = Armor("Cloud Armor")
        lb = LoadBalancing("Load Balancer")

        with Cluster("GKE Cluster"):
            es_agent = Agent("elastic agent")
            cluster_envoy = Custom("envoy proxy", envoy_logo)

            with Cluster("Deployment"):
                agent_crm = Server("Agent CRM")
                gw = Istio("gateway")
                net = gw >> Service("sponsored agent svc")
                hpa = HPA("hpa")

                pods = [Pod("sponsored agent\npod 1"), Pod("sponsored agent\npod 3"), Pod("sponsored agent\npod 2")]

                # Deployment Flow
                (
                    net
                    >> Edge(weight="1")
                    >> pods
                    << ReplicaSet("replicaset")
                    << Deployment("deployment")
                    << hpa
                )

        with Cluster("Other Cluster Services"):
            other_envoy = Custom("envoy proxy", envoy_logo)
            es = Stack("elastic stack")
            workflows = Argocd("argo workflows")
            sm = Istio("service mesh")

        sm >> management_edge("management") >> [cluster_envoy, other_envoy]
        sm >> management_edge("management") >> gw


    # Pod CRM Flow
    (
        agent_crm
        << Edge(label="Agent Data", labelfloat="true", color="red", minlen="4", weight="1")
        >> pods
    )

    # Elastic Agent Data Flow
    (
        es_agent
        >> metrics_edge(label="metrics\nlogs\ntraces")
        >> cluster_envoy
        >> Edge(label="mTLS", color="blue", style="dashed", weight="1")
        << other_envoy
        >> metrics_edge(label="metrics\nlogs\ntraces")
        >> es
    )

    # Ingress Flow
    (
        users
        << Edge(label="cache hit")
        >> cdn
        >> Edge(label="policies", color="blue", style="dotted", weight="1")
        << armor
    )
    cdn >> Edge(label="cache miss") >> lb >> gw

    # Featured Agent Metrics Flow
    (
        workflows
        >> Edge(label="request metrics\non schedule", labelfloat="true")
        >> es
        >> metrics_edge("agent metrics")
        >> workflows
        >> metrics_edge("agent metrics")
        >> sendgrid
        >> metrics_edge("agent metrics", weight="0")
        >> agents
    )
