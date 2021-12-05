import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from consensus_service_pb2 import (
    ConsensusTopicQuery,
    ConsensusTopicResponse,
    )
from basic_types_pb2 import TopicID
from timestamp_pb2 import Timestamp, TimestampSeconds
from consensus_service_pb2_grpc import ConsensusServiceStub
