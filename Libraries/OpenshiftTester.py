__author__ = 'Noam Manos'
__version__ = '1.0.1'
__email__ = 'manosnoam@gmail.com'

import warnings
import yaml
import requests
from kubernetes import client, config
from openshift.dynamic import DynamicClient
from openshift.dynamic import exceptions


class OpenshiftTester():
    ''' A Python Robot-Framework Library to test OpenShift '''

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    # ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    
    def __init__(self):
        print('Starting init...')
        self.k8s_client = None
        self.dyn_client = None
        warnings.filterwarnings("ignore", category=yaml.YAMLLoadWarning)
              
    def setup(self):  # *args):
        ''' Default Test setup - Runs before each step'''
        print('Starting Test Setup...')
    
    def connect_to_cluster(self, kube_conf): 
        ''' Setup Openshift Connection 
        IMPORTANT: kube config file must have a valid token that was generated in OpenShift Cluster, when login on the testing client.
        To get a valid token, login to the Web UI of Openshift, and click on the User to "Copy Login command" '''
          
        self.k8s_client = config.new_client_from_config(kube_conf)
        self.dyn_client = DynamicClient(self.k8s_client)
        
    def create_service(self, api_version, svc_name, app_name, protocol, port, target_port):
        kind = 'Service'
        v1_services = self.dyn_client.resources.get(api_version=api_version, kind=kind)
        
        service = F'''
        kind: {kind}
        apiVersion: {api_version}
        metadata:
          name: {svc_name}
        spec:
          selector:
            app: {app_name}
          ports:
            - protocol: {protocol}
              port: {port}
              targetPort: {target_port}
        '''
         
        service_data = yaml.load(service, Loader=yaml.SafeLoader)
        service_name = service_data['metadata']['name']
        try:
            # obj = v1_services.get(name=service_data['metadata']['name'], namespace='default')
            resp = v1_services.delete(name=service_name, namespace='default')
            print (F'Service {{service_name}} found and removed.')
        except exceptions.NotFoundError as err:
            print (F'Service "{service_name}" not found.')
        resp = v1_services.create(body=service_data, namespace='default')
        
        # resp is a ResourceInstance object
        print(resp.metadata)
        
    def create_router(self, api_version, route_name, host, target_svc):
        kind = 'Route'
        v1_routes = self.dyn_client.resources.get(api_version=api_version, kind=kind)
         
        route = F'''
        apiVersion: {api_version}
        kind: Route
        metadata:
          name: {route_name}
        spec:
          host: {host}
          to:
            kind: Service
            name: {target_svc}
        '''
        
        route_data = yaml.load(route, Loader=yaml.SafeLoader)
        route_name = route_data['metadata']['name']
        try:
            resp = v1_routes.delete(name=route_name, namespace='default')
            print (F'Route {{route_name}} found and removed.')
        except exceptions.NotFoundError as err:
            print (F'Route "{route_name}" not found.')
        resp = v1_routes.create(body=route_data, namespace='default')
        
        # resp is a ResourceInstance object
        print(resp.metadata)

