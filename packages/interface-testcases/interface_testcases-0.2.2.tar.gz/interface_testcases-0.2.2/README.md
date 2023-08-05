# interface_testcases

接口多参数测试用例生成

## 功能特性

* 正常值pairwise-2组合的用例
* 异常值用例
* 不传必选参数用例
* 不传全部可选参数的用例

## 使用指南

### 安装

方法1. pip安装：pip install interface-testcases

方法2. 下载源代码：git clone git@github.com:caiyizhang/interface_testcases.git

    $ cd interface_testcases
    $ pip install .

### 示例
```python

from interface_testcases.testcases import InterfaceTestcases


# 传入参数一行代表一个参数，一个参数有3个属性。
# 前两个是列表，最后一个是布尔类型。分别是正常值、异常值和是否必选参数
params = [
    [[1, 2], [0, 3], False],
    [[-1, -2], [0, -3], True],
    [[-3, 3], [-2, 4], False]
]
for case in InterfaceTestcases(params):
    print(case)


# 结合pytest
import pytest


class Test1(object):

    @pytest.mark.parametrize(['param_1', 'param_2', 'param_3', 'normal_flag'], [
        value_list for value_list in InterfaceTestcases([
            [['1', '10'], ['0', '7'], True],
            [["1", '10', '100'], ['0', '101'], False],
            [[None, '', 2161524184], ['1'], False],
            [[None, '', '1', '11'], [0, 'f2rewrawr'], False]
        ])
    ])
    def test_1(self, param_1, param_2, param_3, normal_flag):
        params = {
            'param_1': param_1,
            'param_2': param_2,
            'param_3': param_3
        }

        # params删除不传入的参数
        params = {k: v for k, v in params.items() if v != 'no_param'}

        if normal_flag == 'normal':
            do_something_normal()
        elif normal_flag == 'abnormal':
            do_something_abnormal()
        else:
            pass
```
