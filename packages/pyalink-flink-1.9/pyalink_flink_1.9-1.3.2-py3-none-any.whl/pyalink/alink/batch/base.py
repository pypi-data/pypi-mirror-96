# -*- coding: utf-8 -*-
from .lazy.lazy_evaluation import pipe_j_lazy_to_py_callbacks
from ..common.sql.sql_query_utils import register_table_name, sql_query
from ..common.types.bases.op_cores import BaseOperator
from ..common.types.bases.params import Params
from ..common.types.conversion.java_method_call import auto_convert_java_type
from ..common.types.conversion.type_converters import py_list_to_j_array, dataframeToOperator, \
    lazy_collect_to_dataframes, collectToDataframes, j_value_to_py_value
from ..common.utils.printing import print_with_title
from ..py4j_util import get_java_class
from ..udf.utils import register_pyflink_function


class BatchOperator(BaseOperator):

    def __init__(self, j_op=None, *args, **kwargs):
        name = kwargs.pop('name', None)
        clsName = kwargs.pop('CLS_NAME', None)
        self.opType = kwargs.pop('OP_TYPE', 'FUNCTION')
        params = Params.from_args(*args, **kwargs)
        super(BatchOperator, self).__init__(params, name, clsName, j_op)

    def linkFrom(self, *ops):
        j_batch_operator_class = get_java_class("com.alibaba.alink.operator.batch.BatchOperator")
        if len(ops) == 1 and isinstance(ops[0], (list, tuple)):
            ops = ops[0]
        num = len(ops)
        j_ops = list(map(lambda op: op.get_j_obj(), ops))
        j_args = py_list_to_j_array(j_batch_operator_class, num, j_ops)
        self.get_j_obj().linkFrom(j_args)
        super(BatchOperator, self).linkFrom(ops)
        return self

    @classmethod
    def execute(cls):
        j_batch_operator_class = get_java_class("com.alibaba.alink.operator.batch.BatchOperator")
        j_batch_operator_class.execute()

    def collectToDataframe(self):
        return collectToDataframes(self)[0]

    @staticmethod
    def fromDataframe(df, schemaStr):
        return dataframeToOperator(df, schemaStr, opType="batch")

    def print(self):
        self.lazyPrint(-1)
        BatchOperator.execute()

    def getSideOutput(self, index):
        from .common import SideOutputBatchOp
        return SideOutputBatchOp().setIndex(index).linkFrom(self)

    def firstN(self, n):
        from .common import FirstNBatchOp
        return self.linkTo(FirstNBatchOp().setSize(n))

    def sample(self, ratio, withReplacement=False):
        from .common import SampleBatchOp
        return self.link(SampleBatchOp().setRatio(ratio).setWithReplacement(withReplacement))

    def sampleWithSize(self, numSamples, withReplacement=False):
        from .common import SampleWithSizeBatchOp
        return self.link(SampleWithSizeBatchOp().setSize(numSamples).setWithReplacement(withReplacement))

    def distinct(self):
        from .common import DistinctBatchOp
        return self.link(DistinctBatchOp())

    def orderBy(self, field, limit=-1, fetch=-1, offset=-1, order="asc"):
        from .common import OrderByBatchOp
        order_by_op = OrderByBatchOp() \
            .setClause(field) \
            .setOrder(order)
        if limit > 0:
            order_by_op = order_by_op.setLimit(limit)
        elif fetch > 0 and offset > 0:
            order_by_op = order_by_op.setFetch(fetch) \
                .setOffset(offset)
        else:
            raise Exception("Need to set parameter limit or fetch+offset")
        return self.link(order_by_op)

    def groupBy(self, by, select):
        from .common import GroupByBatchOp
        group_by_batch_op = GroupByBatchOp() \
            .setGroupByPredicate(by) \
            .setSelectClause(select)
        return self.link(group_by_batch_op)

    def registerTableName(self, name):
        self.get_j_obj().registerTableName(name)
        register_table_name(self, name, "batch")

    @staticmethod
    def sqlQuery(query):
        return sql_query(query, "batch")

    @staticmethod
    def registerFunction(name, func):
        register_pyflink_function(name, func, 'batch')

    def lazyPrint(self, n: int, title: str = None):
        from .common import FirstNBatchOp
        op = self.linkTo(FirstNBatchOp().setSize(n)) if n > 0 else self
        op.lazyCollectToDataframe(lambda df: print_with_title(df, title))
        return self

    def lazyCollectToDataframe(self, *callbacks):
        lazy_dataframe = lazy_collect_to_dataframes(self)[0]
        for callback in callbacks:
            lazy_dataframe.addCallback(callback)
        return self

    @auto_convert_java_type
    def collectStatistics(self):
        return self.collectStatistics()

    def lazyCollectStatistics(self, *callbacks):
        pipe_j_lazy_to_py_callbacks(
            self.get_j_obj().lazyCollectStatistics,
            callbacks,
            j_value_to_py_value)
        return self

    def lazyPrintStatistics(self, title: str = None):
        return self.lazyCollectStatistics(lambda summary: print_with_title(summary, title))


class BaseSourceBatchOp(BatchOperator):
    def __init__(self, *args, **kwargs):
        kwargs['OP_TYPE'] = 'SOURCE'
        super(BaseSourceBatchOp, self).__init__(*args, **kwargs)

    def linkFrom(self, *args):
        raise RuntimeError('Source operator does not support linkFrom()')


class BaseSinkBatchOp(BatchOperator):
    def __init__(self, j_op=None, *args, **kwargs):
        kwargs['OP_TYPE'] = 'SINK'
        super(BaseSinkBatchOp, self).__init__(j_op, *args, **kwargs)
        pass


class BatchOperatorWrapper(BatchOperator):
    def __init__(self, op):
        super(BatchOperatorWrapper, self).__init__(j_op=op)


# TODO: not sure what the following 3 methods do?
def _makeBatchOp(opName, clsName, cls=BatchOperator):
    def __init__(self, *args, **kwargs):
        kwargs['CLS_NAME'] = clsName
        cls.__init__(self, *args, **kwargs)
        pass

    newcls = type(opName, (cls,), {'__init__': __init__})
    return newcls


def _makeSourceBatchOp(opName, clsName):
    return _makeBatchOp(opName, clsName, cls=BaseSourceBatchOp)


def _makeSinkBatchOp(opName, clsName):
    return _makeBatchOp(opName, clsName, cls=BaseSinkBatchOp)
