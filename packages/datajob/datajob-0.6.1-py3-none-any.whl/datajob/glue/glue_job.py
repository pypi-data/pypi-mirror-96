from enum import Enum
from pathlib import Path

from aws_cdk import aws_glue as glue, core, aws_s3_deployment
from aws_cdk import aws_iam as iam

from datajob import logger
from datajob.datajob_base import DataJobBase
from datajob.datajob_context import DatajobContext
from datajob.stepfunctions import stepfunctions_workflow


class GlueJobType(Enum):
    PYTHONSHELL = "pythonshell"
    GLUEETL = "glueetl"

    @staticmethod
    def get_values():
        return [e.value for e in GlueJobType]


@stepfunctions_workflow.task
class GlueJob(DataJobBase):
    def __init__(
        self,
        datajob_stack: core.Construct,
        name: str,
        job_path: str,
        job_type: str = GlueJobType.PYTHONSHELL.value,
        glue_version: str = None,
        max_capacity: int = None,
        arguments: dict = None,
        python_version: str = "3",
        role: iam.Role = None,
        *args,
        **kwargs,
    ):
        """
        :param datajob_stack: aws cdk core construct object.
        :param name: a name for this glue job (will appear on the glue console).
        :param job_path: the path to the glue job relative to the project root.
        :param job_type: choose pythonshell for plain python / glueetl for a spark cluster. pythonshell is the default.
        :param glue_version: at the time of writing choose 1.0 for pythonshell / 2.0 for spark.
        :param max_capacity: max nodes we want to run.
        :param arguments: the arguments as a dict for this glue job.
        :param python_version: 3 is the default
        :param role: you can provide a cdk iam role object as arg. if not provided this class will instantiate a role,
        :param args: any extra args for the glue.CfnJob
        :param kwargs: any extra kwargs for the glue.CfnJob
        """
        logger.info(f"creating glue job {name}")
        super().__init__(datajob_stack, name, **kwargs)
        self.job_path = GlueJob._get_job_path(self.project_root, job_path)
        self.arguments = arguments if arguments else {}
        self.job_type = GlueJob._get_job_type(job_type=job_type)
        self.python_version = python_version
        self.glue_version = GlueJob._get_glue_version(
            glue_version=glue_version, job_type=job_type
        )
        self.max_capacity = max_capacity
        self.role = self._get_role(role, self.unique_name)
        self.args = args
        self.kwargs = kwargs
        logger.info(f"glue job {name} created.")

    def create(self):
        s3_url_glue_job = self._deploy_glue_job_code(
            context=self.context,
            glue_job_name=self.unique_name,
            path_to_glue_job=self.job_path,
        )
        self._create_glue_job(
            context=self.context,
            glue_job_name=self.unique_name,
            s3_url_glue_job=s3_url_glue_job,
            arguments=self.arguments,
            job_type=self.job_type,
            python_version=self.python_version,
            glue_version=self.glue_version,
            max_capacity=self.max_capacity,
            *self.args,
            **self.kwargs,
        )

    @staticmethod
    def _get_job_path(project_root: str, job_path: str) -> str:
        """
        get the full path to a script that we want to run as a glue job.
        :param project_root: path to the root of a project.
        :param job_path: relative path to the script.
        :return: full path to the script
        """
        if project_root is not None:
            return str(Path(project_root, job_path))
        return job_path

    @staticmethod
    def _get_job_type(job_type: str) -> str:
        """
        assert if the glue job type is a valid value.
        :param job_type: the name of the type of glue job
        :return: the name of the glue job type
        """
        assert job_type in GlueJobType.get_values(), ValueError(
            f"Unknown job type {job_type}"
        )
        return job_type

    @staticmethod
    def _get_glue_version(glue_version: str, job_type: str) -> str:
        """
        Specify a default glue version, when none is given.
        :param glue_version: the version of the glue job. At the time of writing these are the possibilities: 0.9, 1.0, 2.0.
        :param job_type: the name of the type of glue job.
        :return: the version of the glue job.
        """
        if glue_version is None:
            if job_type == "pythonshell" or None:
                return "1.0"
            elif job_type == "glueetl":
                return "2.0"
        return glue_version

    def _get_role(self, role: iam.Role, unique_name: str) -> iam.Role:
        """
        If a role is not defined we get the default role for a glue job.
        :param role: role object that can be passed via init.
        :param unique_name: a unique name for our glue job.
        :return:
        """
        if role is None:
            return self.get_role(
                unique_name=unique_name, service_principal="glue.amazonaws.com"
            )
        return role

    @staticmethod
    def _create_s3_url_for_job(
        context: DatajobContext, glue_job_id: str, glue_job_file_name: str
    ) -> str:
        """
        construct the path to s3 where the code resides of the glue job..
        :param context: DatajobContext that contains the name of the deployment bucket.
        :param glue_job_id:
        :param glue_job_file_name:
        :return:
        """
        s3_url_glue_job = (
            f"s3://{context.deployment_bucket_name}/{glue_job_id}/{glue_job_file_name}"
        )
        logger.debug(f"s3 url for glue job {glue_job_id}: {s3_url_glue_job}")
        return s3_url_glue_job

    @staticmethod
    def _get_glue_job_dir_and_file_name(path_to_glue_job: str) -> tuple:
        """
        Split the full path in a dir and filename.
        :param path_to_glue_job: full path to the script
        :return: full path to the dir, name of the script.
        """
        logger.debug(f"splitting path {path_to_glue_job}")
        pathlib_path_to_glue_job = Path(path_to_glue_job)
        glue_job_dir = str(pathlib_path_to_glue_job.parent)
        glue_job_file_name = pathlib_path_to_glue_job.name
        logger.debug(f"splitted into {glue_job_dir} and {glue_job_file_name}")
        return glue_job_dir, glue_job_file_name

    def _deploy_glue_job_code(
        self, context: DatajobContext, glue_job_name: str, path_to_glue_job: str
    ) -> str:
        """deploy the code of this glue job to the deployment bucket
        (can be found in the glue context object)"""
        glue_job_dir, glue_job_file_name = GlueJob._get_glue_job_dir_and_file_name(
            path_to_glue_job=path_to_glue_job
        )
        logger.debug(f"deploying glue job folder {glue_job_dir}")
        aws_s3_deployment.BucketDeployment(
            self,
            f"{glue_job_name}-CodeDeploy",
            sources=[
                # we can either sync dirs or zip files.
                # To keep it easy for now we agreed to sync the full dir.
                # todo - sync only the glue job itself.
                aws_s3_deployment.Source.asset(glue_job_dir)
            ],
            destination_bucket=context.deployment_bucket,
            destination_key_prefix=glue_job_name,
        )

        s3_url_glue_job = GlueJob._create_s3_url_for_job(
            context=context,
            glue_job_id=glue_job_name,
            glue_job_file_name=glue_job_file_name,
        )
        return s3_url_glue_job

    def _create_glue_job(
        self,
        context: DatajobContext,
        glue_job_name: str,
        s3_url_glue_job: str = None,
        arguments: dict = None,
        job_type: str = "pythonshell",
        python_version: str = "3",
        glue_version: str = None,
        max_capacity: int = None,
        *args,
        **kwargs,
    ) -> None:
        """Create a glue job with the necessary configuration like,
        paths to wheel and business logic and arguments"""
        logger.debug(f"creating Glue Job {glue_job_name}")
        default_arguments = None
        if context.s3_url_wheel:
            extra_py_files = {
                # path to the wheel of this project
                "--extra-py-files": context.s3_url_wheel
            }
            default_arguments = {**extra_py_files, **arguments}
        glue.CfnJob(
            self,
            id=glue_job_name,
            name=glue_job_name,
            role=self.role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name=job_type,
                python_version=python_version,
                script_location=s3_url_glue_job,
            ),
            glue_version=glue_version,
            max_capacity=max_capacity,
            default_arguments=default_arguments,
            *args,
            **kwargs,
        )
