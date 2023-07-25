from typing import Optional
from kubernetes import client
from pydantic import BaseModel
from datetime import datetime

from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient
import yaml
import json


class ApplyObject(BaseModel):
    raw_data: str
    namespace: Optional[str] = None


def convert_datetime(data):
    for key, value in data.items():
        if isinstance(value, dict):
            convert_datetime(value)
        elif isinstance(value, datetime):
            data[key] = value.strftime("%Y-%m-%d %H:%M:%S")


def apply_object(apply_object: ApplyObject):
    """Apply a YAML or JSON object to the Kubernetes cluster"""

    try:
        api_client = KubernetesClient().get_core_api_client()
        try:
            data = yaml.safe_load(apply_object.raw_data)
        except yaml.YAMLError:
            data = json.loads(apply_object.raw_data)

        # Convert the dictionary into a Kubernetes object
        k8s_object = client.ApiClient().deserialize(json_dict=data)

        # Determine the kind of object and call the appropriate API method
        if k8s_object.kind == "Pod":
            resp = api_client.create_namespaced_pod(body=k8s_object, namespace=apply_object.namespace)
        elif k8s_object.kind == "Deployment":
            resp = api_client.create_namespaced_deployment(body=k8s_object, namespace=apply_object.namespace)
        elif k8s_object.kind == "Service":
            resp = api_client.create_namespaced_service(body=k8s_object, namespace=apply_object.namespace)
        else:
            return {"error": "Unsupported object kind"}

        return {"response": resp.to_dict()}

    except client.rest.ApiException as e:
        return {"error": e.reason}

    except (yaml.YAMLError, json.JSONDecodeError) as e:
        return {"error": f"Error parsing input data: {e}"}
