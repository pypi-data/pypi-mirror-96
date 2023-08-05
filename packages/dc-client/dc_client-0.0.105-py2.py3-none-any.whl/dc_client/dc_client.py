import requests
import json

def _update_locations(locations):
    # sort locations array and remove field 'offset'
    locations.sort(key=lambda l:l['offset'])
    for i in locations:
        i.pop('offset')


class DataCatalogClient:
    """Data Catalog Client"""

    def __init__(self, url_base, auth=None):
        """
        Parameters
        ----------
        url_base: str
            The endpoint of the API. For example, http://www.myserver.com:8080/api
        auth: tuple
            Tuple of username and password. Optional.
        """
        self.url_base = url_base
        self.session = requests.Session()
        if auth is not None:
            self.session.auth = auth

    def get_dataset(self, name, major_version, minor_version=None):
        """Get dataset.

        Parameters
        ----------
        name: str
            The name of the dataset.
        major_version: str
            The major version of the dataset.
        minor_version: integer
            Optional. If present, we will get dataset that match the minor_version,
            otherwise, we will get the dataset with the highest minor_version.
        """

        url = "{}/Datasets/".format(self.url_base)
        params = {
            'name': name,
            'major_version': major_version,
        }
        if minor_version is None:
            # minor_version not specified, let's have the highest
            # minor_version at the top
            params.update({
                "ordering": "-minor_version"
            })
        else:
            # minor_version specified, no need to sort
            params.update({
                "minor_version": minor_version
            })

        r = self.session.get(url=url, params = params)
        r.raise_for_status()

        d = r.json()
        if d['count'] > 0:
            return d['results'][0]

        return None

    def create_dataset(self, name, major_version, minor_version, description, team):
        """Create a dataset.

        Parameters
        ----------
        name: str
            The name of the dataset.
        major_version: str
            The major version of the dataset.
        minor_version: integer
            The minor version of the dataset.
        description: str
            The description of the dataset. HTML code is allow.
        team: str
            The team who own the dataset.
        """
        url = "{}/Datasets/".format(self.url_base)
        data = {
            'name': name,
            'major_version': major_version,
            'minor_version': minor_version,
            'description': description,
            'team': team
        }

        r = self.session.post(url=url, json = data)
        r.raise_for_status()
        return r.json()

    def set_dataset_schema_and_sample_data(self, id, schema, sample_data=""):
        """set dataset schema.

        If dataset already have schema, and new schema is different it raise exception
        If dataset does not have schema, it sets the schema

        Parameters
        ----------
        id: str
            The dataset ID.
        schema: str
            The schema of the dataset
        """
        url = "{}/Datasets/{}/set_schema_and_sample_data/".format(self.url_base, id, )
        data = {
            'schema': schema,
            'sample_data': sample_data,
        }

        r = self.session.post(url=url, json = data)
        r.raise_for_status()
        return r.json()


    def delete_dataset(self, id):
        """Data a dataset by id.

        Parameters
        ----------
        id: str
            The dataset ID.
        """
        url = "{}/Datasets/{}".format(self.url_base, id)
        r = self.session.delete(url=url)
        r.raise_for_status()


    def get_dataset_instance(self, name, major_version, minor_version, path, revision=None):
        """Get a dataset instance.

        Parameters
        ----------
        name: str
            The name of the dataset.
        major_version: str
            The major version of the dataset.
        minor_version: integer
            The minor version of the dataset.
        path: str
            The path of the dataset instance.
        revision: integer
            Optional. If specified, only dataset matching the revision will be returned.
            Otherwise, the latest revision will be returned.
        """
        dataset = self.get_dataset(name, major_version, minor_version)
        if dataset is None:
            return None

        url = "{}/DatasetInstances/".format(self.url_base)
        params = {
            'path': path,
            'dataset': dataset['id'],
        }
        if revision is None:
            # get the latest revision
            params.update({
                "ordering": "-revision",
                "limit": 1,
            })
        else:
            params.update({
                "revision": revision
            })

        r = self.session.get(url=url, params = params)
        r.raise_for_status()

        d = r.json()
        if d['count'] > 0:
            dsi = d['results'][0]
            if dsi['deleted_time'] is not None:
                # dataset instance is already deleted
                return None
            return dsi

        return None


    def create_dataset_instance(self, name, major_version, minor_version, path, locations, data_time,
                                row_count=None, loader=None, src_dsi_paths=[],
                                application_id = None, application_args = None

        ):
        """Create a dataset instance.

        Parameters
        ----------
        name: str
            The name of the dataset.
        major_version: str
            The major version of the dataset.
        minor_version: integer
            The minor version of the dataset.
        row_count: integer
            The number of rows for this dataset instance.
        path: str
            The path of the dataset instance.
        locations: [Location]
            An array of location. A location is a dict object that has following fields:
            type: str
                The data type stored in this location, for example, csv, parquet, etc...
            location: str
                The location of the data, for example, s3://mybicket/foo.parquet
            size: integer
                Optional. The storage size of the data in this location.
            repo_name: string
                Optional. The name of the data repo
        src_dsi_paths: [string]
            list of dataset instances path that this asset depend on. the path MUST contain revision.
        application_id: string, optional
            if present, it is the application id which produces this asset
        application_args: string, optional
            if present, it is the args passed to this application.
        """
        dataset = self.get_dataset(name, major_version, minor_version)
        if dataset is None:
            raise Exception("dataset not found")

        if not path.startswith('/'):
            raise Exception("path must be absolute")
        if path.endswith('/'):
            raise Exception("path must not end with /")
        di_names = path[1:].split('/')

        for di_name in di_names:
            if len(di_name) == 0:
                raise Exception('Invalid path: name cannot be empty')

        if len(di_names) == 0:
            raise Exception('Invalid path: name not specified')

        if len(di_names) == 1:
            parent_instance = None
        else:
            new_path = '/' + '/'.join(di_names[:-1])
            parent_instance = self.get_dataset_instance(name, major_version, minor_version, new_path)

        url = "{}/DatasetInstances/".format(self.url_base)
        data = {
            'dataset_id': dataset['id'],
            'parent_instance_id': None if parent_instance is None else  parent_instance['id'],
            'name': di_names[-1],
            'data_time': data_time.strftime('%Y-%m-%d %H:%M:%S'),
            'row_count': row_count,
            'loader': loader,
            'locations': locations,
            'src_dsi_paths': src_dsi_paths,
            'application_id': application_id,
            'application_args': application_args,
        }
        if row_count is None:
            data.pop("row_count")

        r = self.session.post(url=url, json = data)
        r.raise_for_status()

        ret = r.json()
        _update_locations(ret['locations'])
        return ret

    def delete_dataset_instance(self, id):
        """Delete a dataset instance by id.

        Parameters
        ----------
        id: str
            The dataset ID.
        """
        url = "{}/DatasetInstances/{id}".format(self.url_base)
        r = self.session.delete(url=url)
        r.raise_for_status()

    def get_data_repo(self, name):
        """Get a data repo by name.
        Data repo's name is unique

        Parameters
        ----------
        name: str
            The data repo name.
        """
        url = "{}/DataRepos/".format(self.url_base)
        params = {
            'name': name,
        }
        r = self.session.get(url=url, params = params)
        r.raise_for_status()

        d = r.json()
        if d['count'] > 0:
            return d['results'][0]

        return None

class DataCatalogClientProxy:
    def __init(self, spark, channel, timeout=600, check_interval=5):
        self.channel = channel
        self.timeout = timeout
        self.check_interval = check_interval

    def _ask(self, spark, content):
        from spark_etl.utils import server_ask_client
        return server_ask_client(spark, self.channel, content, timeout=self.timeout, check_interval=self.check_interval)

    def get_dataset(self, spark, name, major_version, minor_version=None):
        return self._ask(spark, {
            "topic": "dc_client.get_dataset",
            "payload": {
                "name": name,
                "major_version": major_version,
                "minor_version": minor_version
            }
        })

    def create_dataset(self, spark, name, major_version, minor_version, description, team):
        return self._ask(spark, {
            "topic": "dc_client.create_dataset",
            "payload": {
                "name": name,
                "major_version": major_version,
                "minor_version": minor_version,
                "description": description,
                "team": team
            }
        })

    def set_dataset_schema_and_sample_data(self, spark, id, schema, sample_data=""):
        return self._ask(spark, {
            "topic": "dc_client.set_dataset_schema_and_sample_data",
            "payload": {
                "id": id,
                "schema": schema,
                "sample_data": sample_data
            }
        })

    def delete_dataset(self, spark, id):
        return self._ask(spark, {
            "topic": "dc_client.delete_dataset",
            "payload": {
                "id": id,
            }
        })

    def get_dataset_instance(self, spark, name, major_version, minor_version, path, revision=None):
        return self._ask(spark, {
            "topic": "dc_client.get_dataset_instance",
            "payload": {
                "name": name,
                "major_version": major_version,
                "minor_version": minor_version,
                "path": path,
                "revision": revision,
            }
        })

    def create_dataset_instance(self, spark, name, major_version, minor_version, path, locations, data_time,
                                row_count=None, loader=None, src_dsi_paths=[],
                                application_id = None, application_args = None):
        return self._ask(spark, {
            "topic": "dc_client.create_dataset_instance",
            "payload": {
                "name": name,
                "major_version": major_version,
                "minor_version": minor_version,
                "path": path,
                "locations": locations,
                "data_time": data_time.strftime('%Y-%m-%d %H:%M:%S'),
                "row_count": row_count,
                "loader": loader,
                "src_dsi_paths": src_dsi_paths,
                "application_id": application_id,
                "application_args": application_args,
            }
        })

    def delete_dataset_instance(self, spark, id):
        return self._ask(spark, {
            "topic": "dc_client.delete_dataset_instance",
            "payload": {
                "id": id,
            }
        })

    def get_data_repo(self, spark, name):
        return self._ask(spark, {
            "topic": "dc_client.get_data_repo",
            "payload": {
                "name": name,
            }
        })

def json_2_str(obj):
    return json.dumps(obj, indent=4, separators=(',', ': '))


def dc_job_handler(content, dcc):
    topic = content['topic']
    payload = content['payload']

    print("dc_job_handler: ask >>>")
    print(json_2_str(content))
    print("<<<")

    resp = (False, None, )
    if topic == "dc_client.get_dataset":
        resp = (True, dcc.get_dataset(**payload), )
    elif topic == "dc_client.create_dataset":
        resp = (True, dcc.create_dataset(**payload), )
    elif topic == "dc_client.set_dataset_schema_and_sample_data":
        resp = (True, dcc.set_dataset_schema_and_sample_data(**payload), )
    elif topic == "dc_client.delete_dataset":
        resp = (True, dcc.delete_dataset(**payload), )
    elif topic == "dc_client.get_dataset_instance":
        resp = (True, dcc.get_dataset_instance(**payload), )
    elif topic == "dc_client.create_dataset_instance":
        argv = dict(**payload)
        argv['data_time'] = datetime.strptime(payload["data_time"], "%Y-%m-%d %H:%M:%S")
        resp = (True, client.create_dataset_instance(**argv), )
    elif topic == "dc_client.delete_dataset_instance":
        resp = (True, dcc.delete_dataset_instance(**payload), )
    elif topic == "dc_client.get_data_repo":
        resp = (True, dcc.get_data_repo(**payload), )


    print("dc_job_handler: answer >>>")
    if resp[0]:
        print(json_2_str(resp[1]))
    else:
        print("skipped")
    print("<<<")

    return resp
