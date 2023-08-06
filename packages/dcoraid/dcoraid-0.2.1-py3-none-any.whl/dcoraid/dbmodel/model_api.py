import warnings

from ..api import CKANAPI

from .core import DBInterrogator, DBModel
from .util import ttl_cache


class APIModel(DBModel):
    def __init__(self, url, api_key=None, *args, **kwargs):
        """A CKAN-API-based database model"""
        db = APIInterrogator(url=url, api_key=api_key)
        super(APIModel, self).__init__(interrogator=db, *args, **kwargs)


class APIInterrogator(DBInterrogator):
    def __init__(self, url, api_key=None):
        self.api = CKANAPI(url, api_key)
        super(APIInterrogator, self).__init__()

    @ttl_cache(seconds=5)
    def get_circles(self, mode="public"):
        """Return the list of DCOR Circles
        """
        if mode == "user":
            # Organizations the user is a member of
            data = self.api.get("organization_list_for_user",
                                permission="read")
        else:
            data = self.api.get("organization_list")
        return data

    @ttl_cache(seconds=5)
    def get_collections(self, mode="public"):
        """Return the list of DCOR Collections"""
        if mode == "user":
            data = self.api.get("group_list_authz", am_member=True)
        else:
            data = self.api.get("group_list")
        return data

    @ttl_cache(seconds=3600)
    def get_datasets_user_following(self):
        user_data = self.get_user_data()
        data = self.api.get("dataset_followee_list",
                            id=user_data["name"])
        return data

    @ttl_cache(seconds=3600)
    def get_datasets_user_owned(self):
        """Get all the user's datasets"""
        user_data = self.get_user_data()
        numd = user_data["number_created_packages"]
        if numd > 1000:
            raise NotImplementedError(
                "Reached hard limit of 1000 results! "
                + "Please ask someone to implement this with `start`.")
        data2 = self.api.get("package_search",
                             q="*:*",
                             fq="creator_user_id:{}".format(user_data["id"]),
                             rows=numd+1)
        if data2["count"] != numd:
            raise ValueError("Number of user datasets don't match!")

        return data2["results"]

    def get_datasets_user_shared(self):
        warnings.warn("`APIInterrogator.get_datasets_user_shared` "
                      + "not yet implemented!")
        return []

    def get_license_list(self):
        """Return the servers license list"""
        return self.api.get_license_list()

    def get_supplementary_resource_schema(self):
        """Return the servers supplementary resource schema"""
        return self.api.get_supplementary_resource_schema()

    def get_supported_resource_suffixes(self):
        """Return the servers supported resource suffixes"""
        return self.api.get_supported_resource_suffixes()

    @ttl_cache(seconds=3600)
    def get_user_data(self):
        """Return the current user data dictionary"""
        return self.api.get_user_dict()

    @ttl_cache(seconds=3600)
    def get_users(self, ret_fullnames=False):
        """Return the list of DCOR users"""
        data = self.api.get("user_list")
        user_list = []
        full_list = []
        for dd in data:
            user_list.append(dd["name"])
            if dd["fullname"]:
                full_list.append(dd["fullname"])
            else:
                full_list.append(dd["name"])
        if ret_fullnames:
            return user_list, full_list
        else:
            return user_list

    def search_dataset(self, query, circles, collections, mode="public"):
        # https://docs.ckan.org/en/latest/user-guide.html#search-in-detail
        solr_circles = ["organization:{}".format(ci) for ci in circles]
        solr_circle_query = " OR ".join(solr_circles)

        solr_collections = ["groups:{}".format(co) for co in collections]
        solr_collections_query = " OR ".join(solr_collections)

        data = self.api.get("package_search",
                            q=query,
                            include_private=(mode == "user"),
                            fq="({}) AND ({})".format(solr_circle_query,
                                                      solr_collections_query),
                            rows=100,
                            )
        return data["results"]

    @property
    def local_timestamp(self):
        """Local database date in seconds since epoch"""
        return self.remote_timestamp

    @property
    def local_version_score(self):
        """Local database version"""
        return self.remote_version_score
