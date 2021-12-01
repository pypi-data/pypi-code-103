# Copyright 2021 The Couler Authors. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict


class Affinity(object):
    def __init__(self, affinity: dict):
        print(affinity)
        self.pod_affinity = affinity["pod_affinity"]
        self.pod_anti_affinity = affinity["pod_anti_affinity"]
        if self.pod_affinity:
            self.key = affinity["pod_affinity"][
                "required_during_scheduling_ignored_during_execution"
            ]["label_selector"][0]["match_expressions"][0]["key"]
            self.operator = affinity["pod_affinity"][
                "required_during_scheduling_ignored_during_execution"
            ]["label_selector"][0]["match_expressions"][0]["operator"]
            self.value = affinity["pod_affinity"][
                "required_during_scheduling_ignored_during_execution"
            ]["label_selector"][0]["match_expressions"][0]["values"][0]
        if self.pod_anti_affinity:
            self.key = affinity["pod_anti_affinity"][
                "required_during_scheduling_ignored_during_execution"
            ]["label_selector"][0]["match_expressions"][0]["key"]
            self.operator = affinity["pod_anti_affinity"][
                "required_during_scheduling_ignored_during_execution"
            ]["label_selector"][0]["match_expressions"][0]["operator"]
            self.value = affinity["pod_anti_affinity"][
                "required_during_scheduling_ignored_during_execution"
            ]["label_selector"][0]["match_expressions"][0]["values"][0]

    def to_dict(self):
        if self.pod_affinity:
            return OrderedDict(
                {
                    "podAffinity": {
                        "requiredDuringSchedulingIgnoredDuringExecution": [
                            {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {
                                            "key": self.key,
                                            "operator": self.operator,
                                            "values": [self.value],
                                        }
                                    ]
                                },
                                "topologyKey": "kubernetes.io/hostname",
                            }
                        ]
                    }
                }
            )
        elif self.pod_anti_affinity:
            return OrderedDict(
                {
                    "podAntiAffinity": {
                        "requiredDuringSchedulingIgnoredDuringExecution": [
                            {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {
                                            "key": self.key,
                                            "operator": self.operator,
                                            "values": [self.value],
                                        }
                                    ]
                                },
                                "topologyKey": "kubernetes.io/hostname",
                            }
                        ]
                    }
                }
            )
