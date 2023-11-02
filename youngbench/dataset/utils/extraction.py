#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2023-11-01 11:53
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import onnx
import networkx

from typing import List, Dict, Tuple
from onnx.shape_inference import infer_shapes
from google.protobuf import json_format

from youngbench.dataset.modules.network import Network
from youngbench.dataset.modules.model import Model
from youngbench.dataset.modules.node import Node

from youngbench.constants import ONNXOperatorDomain, ONNXAttributeType


def extract_network(model: Model) -> Network:
    onnx_model = infer_shapes(model.onnx_model)
    network, _ = extract_from_gp(onnx_model.graph, dict(), deep_extract=False)
    return network


def extract_networks(model: Model, deep_extract: bool = bool()) -> Tuple[Network, List[Network]]:
    onnx_model = infer_shapes(model.onnx_model)
    deep_networks = list()

    fp_networks = dict()
    for function in onnx_model.functions:
        fp_networks[(function.name, function.domain)] = function

    for function in onnx_model.functions:
        fp_network = fp_networks[(function.name, function.domain)]
        if isinstance(fp_network, onnx.FunctionProto):
            fp_network, fp_deep_networks = extract_from_fp(function, fp_networks, deep_extract=deep_extract, is_sub=True)
            fp_networks[(function.name, function.domain)] = fp_network
            deep_networks.append(fp_network)
            deep_networks.extend(fp_deep_networks)
        else:
            assert isinstance(fp_network, Network)
            deep_networks.append(fp_network)

    network, gp_deep_networks = extract_from_gp(onnx_model.graph, fp_networks, deep_extract=deep_extract, is_sub=False)

    deep_networks.extend(gp_deep_networks)
    return network, deep_networks


def extract_from_fp(fp: onnx.FunctionProto, fp_networks: Dict[Tuple[str, str], Network], deep_extract: bool = bool(), is_sub: bool = bool()) -> Tuple[Network, List[Network]]:
    nn_graph = networkx.DiGraph()
    nn_nodes = dict()
    nn_size = 0
    deep_networks = list()

    i2x = dict()
    o2x = dict()
    for nid, node in enumerate(fp.node):
        nid = str(nid)
        if node.domain in ONNXOperatorDomain:
            operator = onnx.defs.get_schema(node.op_type, domain=node.domain)

            attributes = dict()
            for attribute in node.attribute:
                if attribute.type == ONNXAttributeType.GRAPH or attribute.type == ONNXAttributeType.GRAPHS:
                    all_extracted = list()
                    all_deep_extracted = list()
                    if deep_extract and attribute.type == ONNXAttributeType.GRAPH:
                        extracted, deep_extracted = extract_from_gp(attribute.g, fp_networks, deep_extract=deep_extract, is_sub=True)
                        all_extracted.append(extracted)
                        all_deep_extracted.extend(deep_extracted)
                    if deep_extract and attribute.type == ONNXAttributeType.GRAPHS:
                        for attribute_g in attribute.graphs:
                            extracted, deep_extracted = extract_from_gp(attribute_g, fp_networks, deep_extract=deep_extract, is_sub=True)
                            all_extracted.append(extracted)
                            all_deep_extracted.extend(deep_extracted)
                    attributes[attribute.name] = [extracted.identifier for extracted in all_extracted]
                    deep_networks.extend(all_extracted + all_deep_extracted)
                else:
                    attributes[attribute.name] = json_format.MessageToDict(attribute)

            operands = dict()
            variadic_index = 0
            for index, input in enumerate(node.input):
                if index >= len(operator.inputs) and operator.inputs[-1].option == operator.inputs[-1].option.Variadic.value:
                    index = len(operator.inputs) - 1
                    variadic_index += 1
                operand_name = operator.inputs[index].name + (f'_{variadic_index}' if variadic_index else '')
                i2x[input] = (nid, operand_name, index)
                operands[operand_name] = input

            results = dict()
            for index, output in enumerate(node.output):
                if index >= len(operator.outputs) and operator.outputs[-1].option == operator.outputs[-1].option.Variadic.value:
                    index = len(operator.outputs) - 1
                    variadic_index += 1
                result_name = operator.outputs[index].name + (f'_{variadic_index}' if variadic_index else '')
                o2x[output] = (nid, result_name, index)
                results[result_name] = output

            node = Node(
                operator_type=node.op_type,
                operator_domain=node.domain,
                attributes=attributes,
                parameters=dict(),
                operands=operands,
                results=results
            )
        else:
            fp_network = fp_networks.get((node.op_type, node.domain), None)
            if fp_network is None:
                attributes = dict()
            else:
                if isinstance(fp_network, onnx.FunctionProto):
                    fp_network, fp_deep_networks = extract_from_fp(fp_network, fp_networks, deep_extract=deep_extract, is_sub=True)
                    fp_networks[(function.name, function.domain)] = fp_network
                    deep_networks.extend(fp_deep_networks)
                else:
                    assert isinstance(fp_network, Network)
                attributes = dict(function=fp_network.identifier)

            operands = dict()
            for index, input in enumerate(node.input):
                i2x[input] = (nid, input, index)
                operands[input] = input

            results = dict()
            for index, output in enumerate(node.output):
                o2x[output] = (nid, output, index)
                results[output] = output

            node = Node(
                operator_type=node.op_type,
                operator_domain=node.domain,
                attributes=attributes,
                parameters=dict(),
                operands=operands,
                results=results
            )

        nn_graph.add_node(nid, **node.features)
        nn_nodes[nid] = node
        nn_size += 1

    for nid, node in enumerate(fp.node):
        nid = str(nid)

        for input in node.input:
            if input in i2x and input in o2x:
                u_nid, u_opn, u_opi = o2x[input]
                v_nid, v_opn, v_opi = i2x[input]
                nn_graph.add_edge(u_nid, v_nid, u_opn=u_opn, v_opn=v_opn, u_opi=u_opi, v_opi=v_opi)

        for output in node.output:
            if output in o2x and output in i2x:
                u_nid, u_opn, u_opi = o2x[output]
                v_nid, v_opn, v_opi = i2x[output]
                nn_graph.add_edge(u_nid, v_nid, u_opn=u_opn, v_opn=v_opn, u_opi=u_opi, v_opi=v_opi)
        
    assert networkx.is_directed_acyclic_graph(nn_graph), f'The \"Network\" converted from the \"ONNX Model\" (onnx_model) of Model() is not a Directed Acyclic Graph.'

    network = Network(nn_graph=nn_graph, nn_nodes=nn_nodes, nn_size=nn_size, is_sub=is_sub, is_fnc=True)

    return network, deep_networks


def extract_from_gp(gp: onnx.GraphProto, fp_networks: Dict[Tuple[str, str], Network], deep_extract: bool = bool(), is_sub: bool = bool()) -> Tuple[Network, List[Network]]:
    assert isinstance(gp, onnx.GraphProto)
    nn_graph = networkx.DiGraph()
    nn_nodes = dict()
    nn_size = 0
    deep_networks = list()

    # Parameter
    pm_info = dict()
    for initializer in gp.initializer:
        initializer_dict = json_format.MessageToDict(initializer)
        pm_info[initializer.name] = dict(
            dims = ['dims'],
            dataType = initializer_dict['dataType'],
        )

    # Input & Output
    io_info = dict()
    for input in gp.input:
        io_info[input.name] = json_format.MessageToDict(input.type)
    for value in gp.value_info:
        io_info[value.name] = json_format.MessageToDict(value.type)
    for output in gp.output:
        io_info[output.name] = json_format.MessageToDict(output.type)

    i2x = dict()
    o2x = dict()
    for nid, node in enumerate(gp.node):
        nid = str(nid)
        if node.domain in ONNXOperatorDomain:
            operator = onnx.defs.get_schema(node.op_type, domain=node.domain)

            attributes = dict()
            for attribute in node.attribute:
                if attribute.type == ONNXAttributeType.GRAPH or attribute.type == ONNXAttributeType.GRAPHS:
                    all_extracted = list()
                    all_deep_extracted = list()
                    if deep_extract and attribute.type == ONNXAttributeType.GRAPH:
                        extracted, deep_extracted = extract_from_gp(attribute.g, fp_networks, deep_extract=deep_extract, is_sub=True)
                        all_extracted.append(extracted)
                        all_deep_extracted.extend(deep_extracted)
                    if deep_extract and attribute.type == ONNXAttributeType.GRAPHS:
                        for attribute_g in attribute.graphs:
                            extracted, deep_extracted = extract_from_gp(attribute_g, fp_networks, deep_extract=deep_extract, is_sub=True)
                            all_extracted.append(extracted)
                            all_deep_extracted.extend(deep_extracted)
                    attributes[attribute.name] = [extracted.identifier for extracted in all_extracted]
                    deep_networks.extend(all_extracted + all_deep_extracted)
                else:
                    attributes[attribute.name] = json_format.MessageToDict(attribute)

            parameters = dict()
            variadic_index = 0
            for index, input in enumerate(node.input):
                if input in pm_info:
                    if index >= len(operator.inputs) and operator.inputs[-1].option == operator.inputs[-1].option.Variadic.value:
                        index = len(operator.inputs) - 1
                        variadic_index += 1
                    parameter_name = operator.inputs[index].name + (f'_{variadic_index}' if variadic_index else '')
                    parameters[parameter_name] = pm_info[input]

            operands = dict()
            variadic_index = 0
            for index, input in enumerate(node.input):
                index = min(index, len(operator.inputs) - 1)
                if input in io_info:
                    if index >= len(operator.inputs) and operator.inputs[-1].option == operator.inputs[-1].option.Variadic.value:
                        index = len(operator.inputs) - 1
                        variadic_index += 1
                    operand_name = operator.inputs[index].name + (f'_{variadic_index}' if variadic_index else '')
                    i2x[input] = (nid, operand_name, index)
                    operands[operand_name] = io_info[input]

            results = dict()
            variadic_index = 0
            for index, output in enumerate(node.output):
                index = min(index, len(operator.outputs) - 1)
                if output in io_info:
                    if index >= len(operator.outputs) and operator.outputs[-1].option == operator.outputs[-1].option.Variadic.value:
                        index = len(operator.outputs) - 1
                        variadic_index += 1
                    result_name = operator.outputs[index].name + (f'_{variadic_index}' if variadic_index else '')
                    o2x[output] = (nid, result_name, index)
                    results[result_name] = io_info[output]

            node = Node(
                operator_type=node.op_type,
                operator_domain=node.domain,
                attributes=attributes,
                parameters=parameters,
                operands=operands,
                results=results
            )
        else:
            fp_network = fp_networks.get((node.op_type, node.domain), None)
            if fp_network is None:
                attributes = dict()
            else:
                assert isinstance(fp_network, Network)
                attributes = dict(function=fp_network.identifier)

            operands = dict()
            for index, input in enumerate(node.input):
                if input in io_info:
                    i2x[input] = (nid, input, index)
                    operands[input] = io_info[input]

            results = dict()
            for index, output in enumerate(node.output):
                if output in io_info:
                    o2x[output] = (nid, output, index)
                    results[output] = io_info[output]

            node = Node(
                operator_type=node.op_type,
                operator_domain=node.domain,
                attributes=attributes,
                parameters=dict(),
                operands=operands,
                results=results
            )

        nn_graph.add_node(nid, **node.features)
        nn_nodes[nid] = node
        nn_size += 1

    for nid, node in enumerate(gp.node):
        nid = str(nid)

        for input in node.input:
            if input in i2x and input in o2x:
                u_nid, u_opn, u_opi = o2x[input]
                v_nid, v_opn, v_opi = i2x[input]
                nn_graph.add_edge(u_nid, v_nid, u_opn=u_opn, v_opn=v_opn, u_opi=u_opi, v_opi=v_opi)

        for output in node.output:
            if output in o2x and output in i2x:
                u_nid, u_opn, u_opi = o2x[output]
                v_nid, v_opn, v_opi = i2x[output]
                nn_graph.add_edge(u_nid, v_nid, u_opn=u_opn, v_opn=v_opn, u_opi=u_opi, v_opi=v_opi)
        
    assert networkx.is_directed_acyclic_graph(nn_graph), f'The \"Network\" converted from the \"ONNX Model\" (onnx_model) of Model() is not a Directed Acyclic Graph.'

    network = Network(nn_graph=nn_graph, nn_nodes=nn_nodes, nn_size=nn_size, is_sub=is_sub, is_fnc=False)

    return network, deep_networks