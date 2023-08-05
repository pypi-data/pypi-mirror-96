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
from aliyunsdkretailcloud.endpoint import endpoint_data

class DeployAppRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'retailcloud', '2018-03-13', 'DeployApp')
		self.set_method('POST')
		if hasattr(self, "endpoint_map"):
			setattr(self, "endpoint_map", endpoint_data.getEndpointMap())
		if hasattr(self, "endpoint_regional"):
			setattr(self, "endpoint_regional", endpoint_data.getEndpointRegional())


	def get_DeployPacketUrl(self):
		return self.get_query_params().get('DeployPacketUrl')

	def set_DeployPacketUrl(self,DeployPacketUrl):
		self.add_query_param('DeployPacketUrl',DeployPacketUrl)

	def get_TotalPartitions(self):
		return self.get_query_params().get('TotalPartitions')

	def set_TotalPartitions(self,TotalPartitions):
		self.add_query_param('TotalPartitions',TotalPartitions)

	def get_Description(self):
		return self.get_query_params().get('Description')

	def set_Description(self,Description):
		self.add_query_param('Description',Description)

	def get_EnvId(self):
		return self.get_query_params().get('EnvId')

	def set_EnvId(self,EnvId):
		self.add_query_param('EnvId',EnvId)

	def get_UpdateStrategyType(self):
		return self.get_query_params().get('UpdateStrategyType')

	def set_UpdateStrategyType(self,UpdateStrategyType):
		self.add_query_param('UpdateStrategyType',UpdateStrategyType)

	def get_PauseType(self):
		return self.get_query_params().get('PauseType')

	def set_PauseType(self,PauseType):
		self.add_query_param('PauseType',PauseType)

	def get_DeployPacketId(self):
		return self.get_query_params().get('DeployPacketId')

	def set_DeployPacketId(self,DeployPacketId):
		self.add_query_param('DeployPacketId',DeployPacketId)

	def get_ContainerImageLists(self):
		return self.get_query_params().get('ContainerImageList')

	def set_ContainerImageLists(self, ContainerImageLists):
		for depth1 in range(len(ContainerImageLists)):
			if ContainerImageLists[depth1] is not None:
				self.add_query_param('ContainerImageList.' + str(depth1 + 1) , ContainerImageLists[depth1])

	def get_Name(self):
		return self.get_query_params().get('Name')

	def set_Name(self,Name):
		self.add_query_param('Name',Name)

	def get_InitContainerImageLists(self):
		return self.get_query_params().get('InitContainerImageList')

	def set_InitContainerImageLists(self, InitContainerImageLists):
		for depth1 in range(len(InitContainerImageLists)):
			if InitContainerImageLists[depth1] is not None:
				self.add_query_param('InitContainerImageList.' + str(depth1 + 1) , InitContainerImageLists[depth1])

	def get_ArmsFlag(self):
		return self.get_query_params().get('ArmsFlag')

	def set_ArmsFlag(self,ArmsFlag):
		self.add_query_param('ArmsFlag',ArmsFlag)