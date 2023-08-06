---
id: modules
title: Modules
sidebar_label: Modules
---

The modules contain the instructions to transform the data. The signature of a module always is:

```py
outputs = module_name(*inputs, **module_arguments)
```

Where outputs is a list of [data structures](data-structures) that the module returns.

* **inputs** is the list of positional arguments. They always are a Data Structure (for example something comming from soil.data or the output of another module).

* **module_arguments** are the keyword arguments the module receives and can be different for each module.

## Writing a new module

Modules must be in the `modules` package under the top level package.

A module must be decorated with @soil.modulify. Each modulify decorator takes one **output_types** parameter: a function that indicates the output types of that module.

The **output_types** will be evaluated before starting the pipeline. It gets two parameters:
* **input_types**: The of data structure types it will get.
* **args** : The arguments passed to the module.

Returns a list or a tuple with the Data Structures it will return. If the input_types or the arguments are not compatible with the module it is a good practice to raise a **ValueError exception** at this point before the execution and the resource alocation starts.

```py
from soil import modulify
from soil.data_structures.simple_datastructure import SimpleDataStructure

@modulify(output_types=lambda *input_types, **args: [SimpleDataStructure])
def simple_mean(patients, aggregation_column=None):
    if aggregation_column is None:
        raise TypeError('Expected aggregation_column parameter')
    total_sum = 0
    count = 0
    for patient in patients:
        if hasattr(patient, aggregation_column):
            val = patient[aggregation_column]
            total_sum += val
            count += 1
    return [SimpleDataStructure({'mean': round(total_sum / count)})]
```

The return type of a module must always be a tuple or list of initialized data structures.
