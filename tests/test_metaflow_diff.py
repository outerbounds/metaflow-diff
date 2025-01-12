import os
import tempfile
import unittest
from subprocess import PIPE
from unittest.mock import MagicMock, patch

from metaflow_diff.metaflow_diff import (
    EXCLUSIONS,
    extract_code_package,
    op_diff,
    op_patch,
    op_pull,
    perform_diff,
    run_op,
)


class TestMetaflowDiff(unittest.TestCase):

    @patch("metaflow_diff.metaflow_diff.Run")
    @patch("metaflow_diff.metaflow_diff.namespace")
    def test_extract_code_package(self, mock_namespace, mock_run):
        mock_run.return_value.code.tarball.getmembers.return_value = []
        mock_run.return_value.code.tarball.extractall = MagicMock()
        runspec = "HelloFlow/3"

        with patch(
            "tempfile.TemporaryDirectory", return_value=tempfile.TemporaryDirectory()
        ) as mock_tmp:
            tmp = extract_code_package(runspec, EXCLUSIONS)

        mock_namespace.assert_called_once_with(None)
        mock_run.assert_called_once_with(runspec)
        self.assertTrue(os.path.exists(tmp.name))

    @patch("metaflow_diff.metaflow_diff.run")
    def test_perform_diff_output_false(self, mock_run):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source_file = os.path.join(source_dir, "file.txt")
            target_file = os.path.join(target_dir, "file.txt")
            with open(source_file, "w") as f:
                f.write("source content")
            with open(target_file, "w") as f:
                f.write("target content")

            perform_diff(source_dir, target_dir, output=False)

            # if output=False, run should be called twice:
            # 1. git diff
            # 2. less -R
            assert mock_run.call_count == 2

            mock_run.assert_any_call(
                [
                    "git",
                    "diff",
                    "--no-index",
                    "--exit-code",
                    "--no-color",
                    "./file.txt",
                    source_file,
                ],
                text=True,
                stdout=PIPE,
                cwd=target_dir,
            )

            mock_run.assert_any_call(["less", "-R"], input=mock_run().stdout, text=True)

    @patch("metaflow_diff.metaflow_diff.run")
    def test_perform_diff_output_true(self, mock_run):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source_file = os.path.join(source_dir, "file.txt")
            target_file = os.path.join(target_dir, "file.txt")
            with open(source_file, "w") as f:
                f.write("source content")
            with open(target_file, "w") as f:
                f.write("target content")

            perform_diff(source_dir, target_dir, output=True)

            assert mock_run.call_count == 1

            mock_run.assert_called_once_with(
                [
                    "git",
                    "diff",
                    "--no-index",
                    "--exit-code",
                    "--no-color",
                    "./file.txt",
                    source_file,
                ],
                text=True,
                stdout=PIPE,
                cwd=target_dir,
            )

    @patch("shutil.rmtree")
    @patch("metaflow_diff.metaflow_diff.extract_code_package")
    @patch("metaflow_diff.metaflow_diff.op_diff")
    def test_run_op(self, mock_op_diff, mock_extract_code_package, mock_rmtree):
        mock_tmp = tempfile.TemporaryDirectory()
        mock_extract_code_package.return_value = mock_tmp
        runspec = "HelloFlow/3"

        run_op(runspec, mock_op_diff, {})

        mock_extract_code_package.assert_called_once_with(runspec, EXCLUSIONS)
        mock_op_diff.assert_called_once_with(mock_tmp.name)
        mock_rmtree.assert_called_once_with(mock_tmp.name)

    @patch("metaflow_diff.metaflow_diff.perform_diff")
    def test_op_patch(self, mock_perform_diff):
        mock_perform_diff.return_value = ["diff --git a/file.txt b/file.txt\n"]

        with tempfile.TemporaryDirectory() as tmpdir:
            patch_file = os.path.join(tmpdir, "patch.patch")

            op_patch(tmpdir, patch_file)

            mock_perform_diff.assert_called_once_with(tmpdir, output=True)
            with open(patch_file, "r") as f:
                content = f.read()
            self.assertIn("diff --git a/file.txt b/file.txt\n", content)


if __name__ == "__main__":
    unittest.main()
