import copy
import pathlib

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from ..api import CKANAPI


def activate_dataset(dataset_id, server, api_key):
    """Change the state of a dataset to "active"

    In the DCOR workflow, datasets are created as drafts and
    resources are added to the drafts. After that, the
    datasets are activated (and no resources can be added
    anymore).

    Parameters
    ----------
    dataset_id: str
        CKAN ID of the dataset
    server: str
        server domain name
    api_key: str
        API key of the CKAN/DCOR user
    """
    api = CKANAPI(server=server, api_key=api_key)
    revise_dict = {
        "match": {"id": dataset_id},
        "update": {"state": "active"}}
    res = api.post("package_revise", revise_dict)
    if res["package"]["state"] != "active":
        # TODO: Make this an error message in ckanext-dcor_schemas
        raise ValueError("Setting the state of the dataset "
                         + "'{}' to 'active' did not work! ".format(dataset_id)
                         + "Does the dataset contain resources? If not, then "
                         + "you are experienceing a ckanext-dcor_schemas "
                         + "restriction.")


def add_resource(dataset_id, path, server, api_key, resource_name=None,
                 resource_dict={}, monitor_callback=None):
    """Add a resource to a dataset

    Parameters
    ----------
    dataset_id: str
        CKAN ID of the dataset to which the resource is added
    path: str or pathlib.Path
        Path to the resource
    server: str
        server domain name
    api_key: str
        API key of the CKAN/DCOR user
    resource_name: str
        Alternate resource name, if not set `path.name` is used
    resource_dict: dict
        Dictionary of resource meta data (used for supplementary
        resource schemas "sp:section:key")
    monitor_callback: None or callable
        This callable is used to monitor the upload progress. It must
        accept one argument: a
        `requests_toolbelt.MultipartEncoderMonitor` object.

    See Also
    --------
    dcoraid.upload.joblist.UploadJob
        An implementation of an upload job that monitors progress.
    """
    path = pathlib.Path(path)
    if resource_name is None:
        resource_name = path.name
    api = CKANAPI(server=server, api_key=api_key)
    e = MultipartEncoder(fields={
        'package_id': dataset_id,
        'name': resource_name,
        'upload': (resource_name, path.open('rb'))})
    m = MultipartEncoderMonitor(e, monitor_callback)
    # perform upload
    data = api.post("resource_create",
                    data=m,
                    dump_json=False,
                    headers={"Content-Type": m.content_type})
    if resource_dict:
        # add resource_dict
        revise_dict = {
            "match": {"id": dataset_id},
            "update__resources__{}".format(data["id"]): resource_dict}
        api.post("package_revise", revise_dict)


def create_dataset(dataset_dict, server, api_key, resources=[],
                   create_circle=False, activate=False):
    """Create a draft dataset

    Parameters
    ----------
    dataset_dict: dict
        CKAN dataset dictionary
    server: str
        server domain name
    api_key: str
        API key of the CKAN/DCOR user
    resources: list of str or pathlib.Path
        Paths to dataset resources
    create_circle: bool
        Create the circle if it does not already exist
    activate: bool
        If True, then the dataset state is changed to "active"
        after uploading of the resources is complete. For DCOR,
        this implies that no other resources can be added to the
        dataset.
    """
    api = CKANAPI(server=server, api_key=api_key)
    if create_circle:
        circles = [c["name"] for c in api.get("organization_list_for_user")]
        if dataset_dict["owner_org"] not in circles:
            # Create the circle before creating the dataset
            api.post("organization_create",
                     data={"name": dataset_dict["owner_org"]})
    dataset_dict = copy.deepcopy(dataset_dict)
    dataset_dict["state"] = "draft"
    data = api.post("package_create", dataset_dict)
    if resources:
        for res in resources:
            add_resource(dataset_id=data["id"],
                         path=res,
                         server=server,
                         api_key=api_key)
    if activate:
        activate_dataset(dataset_id=data["id"], server=server, api_key=api_key)
        data["state"] = "active"
    return data


def remove_draft(dataset_id, server, api_key):
    """Remove a draft dataset

    Use this for deleting datasets that you created but which were
    not yet activated. The dataset is deleted and purged.

    Parameters
    ----------
    dataset_id: str
        CKAN ID of the dataset to which the resource is added
    server: str
        server domain name
    api_key: str
        API key of the CKAN/DCOR user
    """
    api = CKANAPI(server=server, api_key=api_key)
    api.post("package_delete", {"id": dataset_id})
    api.post("dataset_purge", {"id": dataset_id})


def remove_all_drafts(server, api_key):
    """Remove all draft datasets

    Find and delete all draft datasets for a user. The user
    ID is inferred from the API key.

    Parameters
    ----------
    server: str
        server domain name
    api_key: str
        API key of the CKAN/DCOR user
    """
    api = CKANAPI(server=server, api_key=api_key)
    user_dict = api.get_user_dict()
    data = api.get(
        "package_search",
        q="*:*",
        include_drafts=True,
        include_private=True,
        fq="creator_user_id:{} AND state:draft".format(user_dict["id"]),
        rows=1000)
    for dd in data["results"]:
        assert dd["state"] == "draft"
        remove_draft(dd["id"], server=server, api_key=api_key)
    return data["results"]


def resource_exists(dataset_id, resource_name, server, api_key):
    """Check whether a resource exists in a dataset"""
    api = CKANAPI(server=server, api_key=api_key)
    pkg_dict = api.get("package_show", id=dataset_id)
    for resource in pkg_dict["resources"]:
        if resource["name"] == resource_name:
            return True
    else:
        return False


def resource_sha256_sums(dataset_id, server, api_key):
    """Return a dictionary of resources with the SHA256 sums as values"""
    api = CKANAPI(server=server, api_key=api_key)
    pkg_dict = api.get("package_show", id=dataset_id)
    sha256dict = {}
    for resource in pkg_dict["resources"]:
        sha256dict[resource["name"]] = resource.get("sha256", None)
    return sha256dict
