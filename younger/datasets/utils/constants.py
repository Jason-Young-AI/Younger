#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2024-04-04 15:59
#
# This source code is licensed under the Apache-2.0 license found in the
# LICENSE file in the root directory of this source tree.


import onnx

from younger.commons.constants import Constant


class ONNX_OPERATOR_DOMAIN(Constant):
    def initialize(self) -> None:
        self.DEFAULT = onnx.defs.ONNX_DOMAIN
        self.ML = onnx.defs.ONNX_ML_DOMAIN
        self.PREVIEW_TRAINING = onnx.defs.AI_ONNX_PREVIEW_TRAINING_DOMAIN

ONNXOperatorDomain = ONNX_OPERATOR_DOMAIN()
ONNXOperatorDomain.initialize()
ONNXOperatorDomain.freeze()


class ONNX_OPERATOR_TYPE(Constant):
    def initialize(self) -> None:
        default_types = set()
        ml_types = set()
        preview_training_types = set()
        for op_schema in onnx.defs.get_all_schemas():
            if op_schema.domain == ONNXOperatorDomain.DEFAULT:
                default_types.add(op_schema.name)
            elif op_schema.domain == ONNXOperatorDomain.ML:
                ml_types.add(op_schema.name)
            elif op_schema.domain == ONNXOperatorDomain.PREVIEW_TRAINING:
                preview_training_types.add(op_schema.name)

        self.DEFAULT = frozenset(default_types)
        self.ML = frozenset(ml_types)
        self.PREVIEW_TRAINING = frozenset(preview_training_types)

ONNXOperatorType = ONNX_OPERATOR_TYPE()
ONNXOperatorType.initialize()
ONNXOperatorType.freeze()


class ONNX_OPERAND_TYPE(Constant):
    def initialize(self) -> None:
        operand_types = dict()
        for field in onnx.TypeProto.DESCRIPTOR.fields:
            if field.containing_oneof:
                operand_types[field.name] = field.number
        for name, value in operand_types.items():
            setattr(self, name, value)
        return

ONNXOperandType = ONNX_OPERAND_TYPE()
ONNXOperandType.initialize()
ONNXOperandType.freeze()


class ONNX_ELEMENT_TYPE(Constant):
    def initialize(self) -> None:
        element_types = dict()
        for element_type_name, element_type_number in onnx.TensorProto.DataType.items():
            element_types[element_type_name] = element_type_number
        for name, value in element_types.items():
            setattr(self, name, value)
        return

ONNXElementType = ONNX_ELEMENT_TYPE()
ONNXElementType.initialize()
ONNXElementType.freeze()


class ONNX_ATTRIBUTE_TYPE(Constant):
    def initialize(self) -> None:
        attribute_types = dict()
        for attribute_type_name, attribute_type_number in onnx.AttributeProto.AttributeType.items():
            attribute_types[attribute_type_name] = attribute_type_number
        for name, value in attribute_types.items():
            setattr(self, name, value)
        return

ONNXAttributeType = ONNX_ATTRIBUTE_TYPE()
ONNXAttributeType.initialize()
ONNXAttributeType.freeze()


class INSTANCE_LABEL_NAME(Constant):
    def initialize(self) -> None:
        self.MODEL_NAME = 'model_name'
        self.MODEL_SOURCE = 'model_source'
        self.ONNX_MODEL_FILENAME = 'onnx_model_filename'
        self.DOWNLOAD = 'download'
        self.LIKE = 'like'
        self.TAG = 'tag'
        self.README = 'readme'
        self.ANNOTATIONS = 'annotations'

InstanceLabelName = INSTANCE_LABEL_NAME()
InstanceLabelName.initialize()
InstanceLabelName.freeze()


ONNX = Constant()
ONNX.OPSetVersions = sorted(set(schema.since_version for schema in onnx.defs.get_all_schemas_with_history()))


# ^^^^^^^^^^^ Above Code Should Be Rewrite ^^^^^^^^^^^^^^

class README_PATTERN(Constant):
    def initialize(self) -> None:
        self.TABLE = r'(\|?(?:[^\r\n\|]*\|)+(?:[^\r\n]*\|?))\r?\n(\|?(?:(?:\s*:?-+:?\s*)\|)+(?:(?:\s*:?-+:?\s*)\|?))\r?\n((?:\|?(?:(?:[^\r\n\|]*)\|)+(?:(?:(?:[^\r\n\|]*)\|?))\r?\n)+)'
        self.DIGIT = r'(?:[+-]?(?:(?:\d+(?:\.\d+)?)|(?:\.\d+))%?)\s+|\s+(?:[+-]?(?:(?:\d+(?:\.\d+)?)|(?:\.\d+))%?)'
        self.DATE = r'(?:(?:\d{4})(?:-|\/)(?:\d{1,2})(?:-|\/)\d{1,2})|(?:(?:\d{1,2})(?:-|\/)(?:\d{1,2})(?:-|\/)\d{4})|(?:(?:\d{4})(?:-|\/)(?:\d{1,2}))|(?:(?:\d{1,2})(?:-|\/)(?:\d{4}))|(?:\d{1,2}(?:-|\/)\d{1,2})'
        self.DATETIME = r'\b\d{4}-(?!(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b)\d{1,2}-(?!([12]\d|3[01])\b)\d{1,2} \d{1,2}:\d{2}(:\d{2})?\b|\b\d{1,2}:\d{2}(:\d{2})?(?:\s*[apAP]\.?[mM]\.?)?\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'

READMEPattern = README_PATTERN()
READMEPattern.initialize()
READMEPattern.freeze()


class YOUNGER_API(Constant):
    def initialize(self) -> None:
        self.API_ADDRESS = 'https://datasets.yangs.cloud/public/'
        self.SERIES_COMPLETE_POINT = 'items/YoungerSeriesComplete'
        self.SERIES_FILTER_POINT = 'items/YoungerSeriesFilter'

YoungerAPI = YOUNGER_API()
YoungerAPI.initialize()
YoungerAPI.freeze()


class YOUNGER_DATASET_ADDRESS(Constant):
    def initialize(self) -> None:
        self.INDICATORS = 'https://datasets.yangs.cloud/Younger/indicators.json'
        self.ONNX_OPERATORS = 'https://datasets.yangs.cloud/Younger/onnx_operators.json'
        self.METRICS = 'https://datasets.yangs.cloud/Younger/metrics.json'
        self.SUPERVISED_TRAIN = 'https://datasets.yangs.cloud/Younger/Supervised_Train.tar.gz'
        self.SUPERVISED_VALID = 'https://datasets.yangs.cloud/Younger/Supervised_Valid.tar.gz'
        self.SUPERVISED_TEST = 'https://datasets.yangs.cloud/Younger/Supervised_Test.tar.gz'
        self.UNSUPERVISED = 'https://datasets.yangs.cloud/Younger/Unsupervised.tar.gz'

        self.DATAFLOW_TRAIN_WA_PAPER = 'https://datasets.yangs.cloud/public/assets/3ad6f8d5-bb8e-416a-aff1-6c97471ea7a9?download='
        self.DATAFLOW_TRAIN_WOA_PAPER = 'https://datasets.yangs.cloud/public/assets/7c782331-641f-412d-96dc-7adcbb0359e9?download='
        self.DATAFLOW_VALID_WA_PAPER = 'https://datasets.yangs.cloud/public/assets/b0989bfa-1956-4703-b6dc-48cf33b689dc?download='
        self.DATAFLOW_VALID_WOA_PAPER = 'https://datasets.yangs.cloud/public/assets/f53a64e6-f38c-465b-a17f-9844f0c4dd19?download='
        self.DATAFLOW_TEST_WA_PAPER = 'https://datasets.yangs.cloud/public/assets/3423c68a-8112-47f8-998b-aa7707b8e770?download='
        self.DATAFLOW_TEST_WOA_PAPER = 'https://datasets.yangs.cloud/public/assets/4301b27b-eab6-4543-a6e0-73989ae4affe?download='

        self.OPERATOR_TRAIN_WA_PAPER = 'https://datasets.yangs.cloud/public/assets/048b6198-30cc-406c-a5db-6b1b299a5876?download='
        self.OPERATOR_TRAIN_WOA_PAPER = 'https://datasets.yangs.cloud/public/assets/7c782331-641f-412d-96dc-7adcbb0359e9?download='
        self.OPERATOR_VALID_WA_PAPER = 'https://datasets.yangs.cloud/public/assets/17693925-d418-4945-a660-0c69f103d00c?download='
        self.OPERATOR_VALID_WOA_PAPER = 'https://datasets.yangs.cloud/public/assets/e9c80d0a-188e-4604-8ebd-e194aa372e81?download='
        self.OPERATOR_TEST_WA_PAPER = 'https://datasets.yangs.cloud/public/assets/45480765-f152-46fd-8c59-4b4d477fde3d?download='
        self.OPERATOR_TEST_WOA_PAPER = 'https://datasets.yangs.cloud/public/assets/14581e21-9667-4c05-aec2-0bd8abc66d2e?download='

YoungerDatasetAddress = YOUNGER_DATASET_ADDRESS()
YoungerDatasetAddress.initialize()
YoungerDatasetAddress.freeze()


class YOUNGER_DATASET_NODE_TYPE(Constant):
    def initialize(self) -> None:
        self.UNK = '__UNK__'
        self.OUTER = '__OUTER__'
        self.INPUT = '__INPUT__'
        self.OUTPUT = '__OUTPUT__'
        self.CONSTANT = '__CONSTANT__'
        self.OPERATOR = '__OPERATOR__'

YoungerDatasetNodeType = YOUNGER_DATASET_NODE_TYPE()
YoungerDatasetNodeType.initialize()
YoungerDatasetNodeType.freeze()