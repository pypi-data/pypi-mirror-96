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
from aliyunsdkquickbi_public.endpoint import endpoint_data

class QueryDatasetListRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'quickbi-public', '2020-08-06', 'QueryDatasetList','quickbi')
		self.set_method('POST')
		if hasattr(self, "endpoint_map"):
			setattr(self, "endpoint_map", endpoint_data.getEndpointMap())
		if hasattr(self, "endpoint_regional"):
			setattr(self, "endpoint_regional", endpoint_data.getEndpointRegional())


	def get_PageSize(self):
		return self.get_query_params().get('PageSize')

	def set_PageSize(self,PageSize):
		self.add_query_param('PageSize',PageSize)

	def get_DirectoryId(self):
		return self.get_query_params().get('DirectoryId')

	def set_DirectoryId(self,DirectoryId):
		self.add_query_param('DirectoryId',DirectoryId)

	def get_WithChildren(self):
		return self.get_query_params().get('WithChildren')

	def set_WithChildren(self,WithChildren):
		self.add_query_param('WithChildren',WithChildren)

	def get_Keyword(self):
		return self.get_query_params().get('Keyword')

	def set_Keyword(self,Keyword):
		self.add_query_param('Keyword',Keyword)

	def get_PageNum(self):
		return self.get_query_params().get('PageNum')

	def set_PageNum(self,PageNum):
		self.add_query_param('PageNum',PageNum)

	def get_WorkspaceId(self):
		return self.get_query_params().get('WorkspaceId')

	def set_WorkspaceId(self,WorkspaceId):
		self.add_query_param('WorkspaceId',WorkspaceId)