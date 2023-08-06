# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RpcRequest
from aliyunsdkdas.endpoint import endpoint_data

class UpdateAutoResourceOptimizeConfigRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'DAS', '2020-01-16', 'UpdateAutoResourceOptimizeConfig','das')
		self.set_method('POST')
		if hasattr(self, "endpoint_map"):
			setattr(self, "endpoint_map", endpoint_data.getEndpointMap())
		if hasattr(self, "endpoint_regional"):
			setattr(self, "endpoint_regional", endpoint_data.getEndpointRegional())


	def get___context(self):
		return self.get_query_params().get('__context')

	def set___context(self,__context):
		self.add_query_param('__context',__context)

	def get_Signature(self):
		return self.get_query_params().get('Signature')

	def set_Signature(self,Signature):
		self.add_query_param('Signature',Signature)

	def get_AutoDefragment(self):
		return self.get_query_params().get('AutoDefragment')

	def set_AutoDefragment(self,AutoDefragment):
		self.add_query_param('AutoDefragment',AutoDefragment)

	def get_AutoDuplicateIndexDelete(self):
		return self.get_query_params().get('AutoDuplicateIndexDelete')

	def set_AutoDuplicateIndexDelete(self,AutoDuplicateIndexDelete):
		self.add_query_param('AutoDuplicateIndexDelete',AutoDuplicateIndexDelete)

	def get_UserId(self):
		return self.get_query_params().get('UserId')

	def set_UserId(self,UserId):
		self.add_query_param('UserId',UserId)

	def get_Uid(self):
		return self.get_query_params().get('Uid')

	def set_Uid(self,Uid):
		self.add_query_param('Uid',Uid)

	def get_InstanceId(self):
		return self.get_query_params().get('InstanceId')

	def set_InstanceId(self,InstanceId):
		self.add_query_param('InstanceId',InstanceId)

	def get_AccessKey(self):
		return self.get_query_params().get('AccessKey')

	def set_AccessKey(self,AccessKey):
		self.add_query_param('AccessKey',AccessKey)

	def get_TableSpaceSize(self):
		return self.get_query_params().get('TableSpaceSize')

	def set_TableSpaceSize(self,TableSpaceSize):
		self.add_query_param('TableSpaceSize',TableSpaceSize)

	def get_TableFragmentationRatio(self):
		return self.get_query_params().get('TableFragmentationRatio')

	def set_TableFragmentationRatio(self,TableFragmentationRatio):
		self.add_query_param('TableFragmentationRatio',TableFragmentationRatio)