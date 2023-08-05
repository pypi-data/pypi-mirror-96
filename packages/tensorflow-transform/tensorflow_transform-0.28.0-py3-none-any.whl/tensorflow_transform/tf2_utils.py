# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TF2 utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy

# GOOGLE-INITIALIZATION

import tensorflow as tf
from tensorflow.python import tf2  # pylint: disable=g-direct-tensorflow-import


def use_tf_compat_v1(force_tf_compat_v1):
  """Evaluate from environment variables if TF should be used in compat.v1 mode."""
  major, _, _ = tf.version.VERSION.split('.')
  return force_tf_compat_v1 or int(major) < 2 or not tf2.enabled()


def supply_missing_tensor(batch_size, tensor_shape, tensor_dtype):
  """Supplies a `tf.Tensor` compatible with `tensor`.

  Supports only string and numeric dtypes.
  Args:
    batch_size: an integer representing the size of the batch returned.
    tensor_shape: a `tf.TensorShape`. The returned tensor will have shape
      compatible with this.
    tensor_dtype: The dtype of the returned tensors.

  Returns:
    A batch of `tf.Tensor` tensors.
  """
  # If tensor rank is 0 or unknown, return a scalar.
  if tensor_shape.ndims is None or tensor_shape.ndims == 0:
    return tf.zeros([], dtype=tensor_dtype)

  input_shape = tensor_shape.as_list()
  result_shape = [input_shape[0] or batch_size]

  for shape in input_shape[1:]:
    if shape is None:
      result_shape = result_shape + [1]
    else:
      result_shape = result_shape + [shape]
  return tf.zeros(result_shape, dtype=tensor_dtype)


def supply_missing_inputs(structured_inputs, batch_size, missing_keys=None):
  """Supply inputs for unfed features.

  Supports only tf.Tensor.
  Args:
    structured_inputs: a dict from keys to batches of placeholder graph tensors.
    batch_size: an integer representing the size of the batch returned.
    missing_keys: (Optional) a subset of the keys of `structured_inputs` for
      which concrete tensors need to be supplied. If `None`, tensors are
      supplied for all keys.

  Returns:
    A batch of tensors with the same structure as in `structured_inputs`
    for the keys in `missing_keys`.
  """
  missing_keys = missing_keys or list(structured_inputs)
  result = {}
  for key in missing_keys:
    tensor = structured_inputs[key]
    if isinstance(tensor, tf.Tensor):
      result[key] = supply_missing_tensor(batch_size, tensor.shape,
                                          tensor.dtype)
    elif isinstance(tensor, tf.SparseTensor):
      values = supply_missing_tensor(batch_size, tensor.values.shape,
                                     tensor.values.dtype)
      dense_rank = tensor.shape.ndims
      # Since values is always a 1-D tensor, set index for every ith value in
      # values to be [i 0 0 ...]. Each index should be compatible with the
      # rank of the SparseTensor. Hence, the number of 0s is dense_rank-1.
      actual_batch_size = tf.shape(values)[0]
      indices = tf.stack(
          [tf.range(actual_batch_size, dtype=tf.int64)] +
          [tf.zeros(actual_batch_size, dtype=tf.int64)] * (dense_rank - 1),
          axis=1)
      dense_shape = [actual_batch_size] + [1] * (dense_rank - 1)
      result[key] = tf.SparseTensor(
          indices=indices, values=values, dense_shape=dense_shape)
    else:
      # TODO(b/169666856): Add support for generic CompositeTensors.
      raise ValueError('Received unsupported input tensor type. Only '
                       'dense/sparse tensors are currently supported.')
  return result


def get_structured_inputs_from_func_graph(func_graph):
  """Get structured inputs to a FuncGraph.

  Args:
    func_graph: A `FuncGraph` object.

  Returns:
    Input graph tensors of `func_graph` formatted as possibly-nested python
    objects received by it.
  """
  # structured_input_signature is a tuple of (args, kwargs). [0][0] retrieves
  # the structure of the first arg, which for the preprocessing function is
  # the dictionary of features.
  input_signature = func_graph.structured_input_signature[0][0]
  num_captures = len(func_graph.internal_captures)
  # `func_graph.inputs` contains placeholders that represent regular inputs
  # followed by captured inputs. We are only interested in the regular inputs.
  graph_inputs = copy.copy(func_graph.inputs)
  if num_captures > 0:
    graph_inputs = graph_inputs[:-num_captures]
  return tf.nest.pack_sequence_as(
      input_signature, graph_inputs, expand_composites=True)
