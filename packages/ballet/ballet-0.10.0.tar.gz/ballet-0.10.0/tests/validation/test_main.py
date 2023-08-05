import unittest
from unittest.mock import MagicMock, patch

import ballet.util.log
from ballet.exc import SkippedValidationTest
from ballet.validation.main import (  # noqa F401
    _check_project_structure, _evaluate_feature_performance,
    _load_validator_class_params, _prune_existing_features,
    _validate_feature_api, validate, validation_stage,)


class MainTest(unittest.TestCase):

    def test_validation_stage_success(self):
        @validation_stage('do something')
        def call():
            return True

        call()

    def test_validation_stage_skipped(self):
        @validation_stage('do something')
        def call():
            raise SkippedValidationTest

        logger = ballet.util.log.logger
        with self.assertLogs(logger=logger) as cm:
            call()

        output = '\n'.join(cm.output)
        self.assertIn('SKIPPED', output)

    def test_validation_stage_failure(self):
        exc = ValueError

        @validation_stage('do something')
        def call():
            raise exc

        with self.assertRaises(exc):
            call()

    @patch('ballet.validation.project_structure.validator.ChangeCollector')
    @patch('ballet.validation.main.import_module_from_modname')
    def test_load_validator_class_params_noparams(self, mock_import, _):
        """Check that _load_validator_class_params works"""

        import ballet.validation.project_structure.validator
        from ballet.validation.project_structure.validator import (
            ProjectStructureValidator,)
        mock_import.return_value = \
            ballet.validation.project_structure.validator

        mock_project = MagicMock()
        modname = 'ballet.validation.project_structure.validator'
        clsname = 'ProjectStructureValidator'
        path = modname + '.' + clsname
        mock_project.config.get.return_value = path

        config_key = None

        logger = ballet.util.log.logger
        with self.assertLogs(logger=logger, level='DEBUG') as cm:
            make_validator = _load_validator_class_params(
                mock_project, config_key)

        output = '\n'.join(cm.output)
        self.assertIn(clsname, output)

        validator = make_validator(mock_project)
        self.assertIsInstance(validator, ProjectStructureValidator)

    @unittest.expectedFailure
    def test_load_validator_class_params_withparams(self):
        """Check that _load_validator_class_params correctly applies kwargs"""
        raise NotImplementedError

    @unittest.expectedFailure
    def test_check_project_structure(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_validate_feature_api(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_evaluate_feature_performance(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_prune_existing_features(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_validate(self):
        raise NotImplementedError
