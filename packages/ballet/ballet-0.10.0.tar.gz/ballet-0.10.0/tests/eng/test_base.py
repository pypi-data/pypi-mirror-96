import unittest

import numpy as np
import pandas as pd
import sklearn.base
from sklearn.impute import SimpleImputer

import ballet.eng
import ballet.exc
from ballet.util.testing import ArrayLikeEqualityTestingMixin


class BaseTest(ArrayLikeEqualityTestingMixin, unittest.TestCase):

    def setUp(self):
        pass

    def test_no_fit_mixin(self):
        class _Foo(ballet.eng.NoFitMixin):
            pass
        a = _Foo()

        self.assertTrue(hasattr(a, 'fit'))

        # method should exist
        a.fit('X')
        a.fit('X', y=None)

    def test_base_transformer(self):
        a = ballet.eng.BaseTransformer()

        self.assertIsInstance(a, sklearn.base.BaseEstimator)
        self.assertTrue(hasattr(a, 'fit'))

    def test_simple_function_transformer(self):
        def func(x): return x + 5
        data = np.arange(30)

        trans = ballet.eng.SimpleFunctionTransformer(func)
        trans.fit(data)
        data_trans = trans.transform(data)
        data_func = func(data)

        self.assertArrayEqual(data_trans, data_func)

    def test_simple_function_transformer_str_repr(self):
        trans = ballet.eng.SimpleFunctionTransformer(lambda x: x)
        for func in [str, repr]:
            s = func(trans)
            self.assertGreater(len(s), 0)

    def test_grouped_function_transformer(self):
        df = pd.DataFrame(
            data={
                'country': ['USA', 'USA', 'USA', 'Canada', 'Fiji'],
                'year': [2001, 2002, 2003, 2001, 2001],
                'length': [1, 2, 3, 4, 5],
                'width': [1.0, 1.0, 7.5, 9.0, 11.0],
            }
        ).set_index(['country', 'year']).sort_index()

        # with groupby kwargs, produces a df
        func = np.sum
        trans = ballet.eng.GroupedFunctionTransformer(
            func, groupby_kwargs={'level': 'country'})
        trans.fit(df)
        result = trans.transform(df)
        expected_result = df.groupby(level='country').apply(func)
        self.assertFrameEqual(result, expected_result)

        # without groupby kwargs, produces a series
        func = np.min
        trans = ballet.eng.GroupedFunctionTransformer(func)
        trans.fit(df)
        result = trans.transform(df)
        expected_result = df.pipe(func)
        self.assertSeriesEqual(result, expected_result)


class _SetupMixin:

    def setUp(self):
        self.X_tr = pd.DataFrame(
            data={
                'name': ['A', 'A', 'A', 'B', 'B', 'C', 'C'],
                'year': [2001, 2002, 2003, 2001, 2002, 2001, 2003],
                'value': [1, 2, np.nan, 4, 4, 5, np.nan],
                'size': [3, 5, 5, 5, 5, np.nan, 4],
            }
        ).set_index(['name', 'year']).sort_index()

        self.X_te = pd.DataFrame(
            data={
                'name': ['A', 'B', 'C'],
                'year': [2004, 2004, 2004],
                'value': [np.nan, 1.5, np.nan],
                'size': [4, 1, np.nan],
            }
        ).set_index(['name', 'year']).sort_index()


class GroupwiseTransformerTest(
    _SetupMixin, ArrayLikeEqualityTestingMixin, unittest.TestCase
):

    def setUp(self):
        super().setUp()
        self.groupby_kwargs = {'level': 'name'}

        # mean-impute within groups
        self.individual_transformer = SimpleImputer()
        self.trans = ballet.eng.GroupwiseTransformer(
            self.individual_transformer,
            groupby_kwargs=self.groupby_kwargs,
            column_selection=['value'],
        )

    def test_can_fit(self):
        self.trans.fit(self.X_tr)

    def test_can_transform(self):
        self.trans.fit(self.X_tr)

        result_tr = self.trans.transform(self.X_tr)
        expected_tr = self.X_tr.copy()
        expected_tr['value'] = np.array([1, 2, 1.5, 4, 4, 5, 5])
        expected_tr = expected_tr.drop('size', axis=1)
        self.assertFrameEqual(result_tr, expected_tr)

        result_te = self.trans.transform(self.X_te)
        expected_te = self.X_te.copy()
        expected_te['value'] = np.array([1.5, 1.5, 5])
        expected_te = expected_te.drop('size', axis=1)
        self.assertFrameEqual(result_te, expected_te)

    def test_raise_on_new_group(self):
        trans = ballet.eng.GroupwiseTransformer(
            self.individual_transformer,
            groupby_kwargs=self.groupby_kwargs,
            handle_unknown='error'
        )

        trans.fit(self.X_tr)

        X_te = self.X_te.copy().reset_index()
        X_te.loc[0, 'name'] = 'Z'  # new group
        X_te = X_te.set_index(['name', 'year'])

        with self.assertRaises(ballet.exc.BalletError):
            trans.transform(X_te)

    def test_ignore_on_new_group(self):
        trans = ballet.eng.GroupwiseTransformer(
            self.individual_transformer,
            groupby_kwargs=self.groupby_kwargs,
            handle_unknown='ignore'
        )

        trans.fit(self.X_tr)

        X_te = self.X_te.copy().reset_index()
        X_te.loc[0, 'name'] = 'Z'  # new group
        X_te = X_te.set_index(['name', 'year'])

        result = trans.transform(X_te)

        # the first group, Z, is new, and values are passed through, so such
        # be nan
        expected = X_te.copy()
        expected['value'] = np.array([np.nan, 1.5, 5.0])
        expected['size'] = np.array([4.0, 1.0, 4.0])

        self.assertFrameEqual(result, expected)

    def test_raise_on_transform_error(self):
        exc = Exception

        class TransformErrorTransformer(ballet.eng.BaseTransformer):
            def transform(self, X, **transform_kwargs):
                raise exc

        individual_transformer = TransformErrorTransformer()
        trans = ballet.eng.GroupwiseTransformer(
            individual_transformer,
            groupby_kwargs=self.groupby_kwargs,
            handle_error='error',
        )

        trans.fit(self.X_tr)

        with self.assertRaises(exc):
            trans.transform(self.X_tr)

    def test_ignore_on_transform_error(self):
        exc = Exception

        class TransformErrorTransformer(ballet.eng.BaseTransformer):
            def transform(self, X, **transform_kwargs):
                raise exc

        individual_transformer = TransformErrorTransformer()
        trans = ballet.eng.GroupwiseTransformer(
            individual_transformer,
            groupby_kwargs=self.groupby_kwargs,
            handle_error='ignore',
        )

        trans.fit(self.X_tr)

        result_tr = trans.transform(self.X_tr)
        expected_tr = self.X_tr

        self.assertFrameEqual(result_tr, expected_tr)

        result_te = trans.transform(self.X_te)
        expected_te = self.X_te
        self.assertFrameEqual(result_te, expected_te)


class ConditionalTransformerTest(
    _SetupMixin, ArrayLikeEqualityTestingMixin, unittest.TestCase
):

    def test_both_satisfied(self):
        t = ballet.eng.ConditionalTransformer(
            lambda ser: ser.sum() > 0,
            lambda ser: ser + 1,
        )

        # all the features are selected by sum > 0
        t.fit(self.X_tr)
        result_tr = t.transform(self.X_tr)
        for col in ['value', 'size']:
            self.assertSeriesNotEqual(result_tr[col], self.X_tr[col])

        result_te = t.transform(self.X_te)
        for col in ['value', 'size']:
            self.assertSeriesNotEqual(result_te[col], self.X_te[col])

    def test_one_satisfied(self):
        t = ballet.eng.ConditionalTransformer(
            lambda ser: (ser.dropna() >= 3).all(),
            lambda ser: ser.fillna(0) + 1,
        )

        t.fit(self.X_tr)
        result_tr = t.transform(self.X_tr)
        result_te = t.transform(self.X_te)

        # only 'size' is selected by the condition
        self.assertSeriesNotEqual(result_tr['size'], self.X_tr['size'])
        self.assertSeriesNotEqual(result_te['size'], self.X_te['size'])

        # 'value' is not selected by the condition, has items less than 3
        self.assertSeriesEqual(result_tr['value'], self.X_tr['value'])
        self.assertSeriesEqual(result_te['value'], self.X_te['value'])

    def test_unsatisfy_transform(self):
        t = ballet.eng.ConditionalTransformer(
            lambda ser: (ser.dropna() >= 3).all(),
            lambda ser: ser,
            lambda ser: ser.fillna(0) - 1,
        )

        t.fit(self.X_tr)
        result_tr = t.transform(self.X_tr)
        result_te = t.transform(self.X_te)

        # size is transformed by satisfy condition, but passed through
        self.assertSeriesEqual(result_tr['size'], self.X_tr['size'])
        self.assertSeriesEqual(result_te['size'], self.X_te['size'])

        # value is transformed by unsatisfy condition and is not equal
        self.assertSeriesNotEqual(result_tr['value'], self.X_tr['value'])
        self.assertSeriesNotEqual(result_te['value'], self.X_te['value'])
