.. _AWS CDK: https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html
.. _CloudFormation: https://aws.amazon.com/cloudformation/
.. _Serverless Framework: https://serverless.com/
.. _CFNgin: index.html#cloudformation-troposphere
.. _Terraform: https://www.terraform.io
.. _Troposphere: https://github.com/cloudtools/troposphere
.. _Kubernetes: https://kubernetes.io/

.. _Lookups: lookups.html
.. _env lookup: lookups.html#env
.. _var lookup: lookups.html#var

.. _runway-config:

##################
Runway Config File
##################


***********************
Top-Level Configuration
***********************

.. autoclass:: runway.config.Config


.. _runway-deployment:

**********
Deployment
**********

.. autoclass:: runway.config.DeploymentDefinition


.. _runway-future:

******
Future
******

Toggles to opt-in to future, potentially backward compatibility breaking functionality before it is made standard in the next major release.

Availability of these toggles will be removed at each major release as the functionality will then be made standard.

**strict_environments (bool)**
  When enabled, handling of ``environments`` for Deployment_ and Module_ definitions is changed to prevent processing of modules when the current environment is not defined in the Runway config file.

  If ``environments`` is defined and the current :ref:`deploy environment <term-deploy-env>` is not in the definition, the module will be skipped.
  If ``environments`` is not defined, the module will be processed. This does not mean that action will be taken but that the type of the module will then determine if action will be taken.

  .. rubric:: Example
  .. code-block:: yaml

      future:
        strict_environments: true

      deployments:
        - environments:
            prod:
              - 111111111111/us-east-1
              - 111111111111/us-west-2
            dev:
              - 222222222222
          modules:
            - path: sampleapp-01.cfn
            - path: sampleapp-02.cfn
              environments:
                dev: 222222222222/us-east-1
                feature/something-new: true
          regions: &regions
            - ca-central-1
            - us-east-1
            - us-west-2
        - modules:
            - path: sampleapp-03.cfn
            - path: sampleapp-04.cfn
              environments:
                dev-ca:
                  - ca-cental-1
          regions: *regions

  Given the above Runway configuration file, the following will occur for each module:

  **sampleapp-01.cfn**
    Processed if:

    - environment is **prod** and AWS account ID is **111111111111** and region is (**us-east-1** or **us-west-2**)
    - environment is **dev** and AWS account ID is **222222222222** and region is *anything*

    All other combinations will result in the module being skipped.

  **sampleapp-02.cfn**
    Processed if:

    - environment is **prod** and AWS account ID is **111111111111** and region is (**us-east-1** or **us-west-2**)
    - environment is **dev** and AWS account ID is **222222222222** and region is **us-east-1**
    - environment is **feature/something-new** and AWS account ID is *anything* and region is *anything*

    All other combinations will result in the module being skipped.

  **sampleapp-03.cfn**
    Processed if:

    - environment is *anything* and AWS account ID is *anything* and region is *anything*

  **sampleapp-04.cfn**
    Processed if:

    - environment is **dev-ca** and AWS account ID is *anything* and region is **ca-central-1**

    All other combinations will result in the module being skipped.

  .. versionadded:: 1.9.0


.. _runway-module:

******
Module
******

.. autoclass:: runway.config.ModuleDefinition

.. _runway-module-path:

Path
====

.. automodule:: runway.path.Path

.. _runway-module-path-git:

Git
---

Git remote resources can be used as modules for your Runway project. Below is
an example of git remote path.

.. rubric:: Example
.. code-block:: yaml

  deployments:
      - modules:
          - git::git://github.com/foo/bar.git//my/path?branch=develop

The path is broken down into the following attributes:

``git``: The type of remote resource being retrieved, in this case **git**

``::``: Logical separator of the type from the rest of the path string

``git://github.com/foo/bar.git``: The protocol and URI address of the git
repository

``//`` **(optional)**: Logical separator of the URI from the remaining path
string

``my/path`` **(optional)**: The relative path from the root of the repo
where the module is housed

``?`` **(optional)**: Logical separator of the path from the options

``branch=develop`` **(optional)**:  The options to be passed. The Git module
accepts three different types of options: `commit`, `tag`, or `branch`. These
respectively point the repository at the reference id specified.


Type
====

.. automodule:: runway.runway_module_type.RunwayModuleType


.. _runway-test:

****
Test
****

.. autoclass:: runway.config.TestDefinition


.. _runway-variables:

*********
Variables
*********

.. autoclass:: runway.config.VariablesDefinition


******
Sample
******

.. rubric:: runway.yml
.. code-block:: yaml

    ---
    # Order that tests will be run. Test execution is triggered with the
    # 'runway test' command. Testing will fail and exit if any of the
    # individual tests fail unless they are marked with 'required: false'.
    # Please see the doc section dedicated to tests for more details.

    tests:
      - name: test-names-are-optional
        type: script  # there are a few built in test types
        args:  # each test has their own set of arguments they can accept
          commands:
            - echo "Beginning a test..."
            - cd app.sls && npm test && cd ..
            - echo "Test complete!"
      - name: unimportant-test
        type: cfn-lint
        required: false  # tests will still pass if this fails
      - type: yamllint  # not all tests accept arguments

    # Order that modules will be deployed. A module will be skipped if a
    # corresponding environment file is not present or "enabled" is false.
    # E.g., for cfn modules, if
    # 1) a dev-us-west-2.env file is not in the 'app.cfn' folder when running
    #    a dev deployment of 'app' to us-west-2,
    # and
    # 2) "enabled" is false under the deployment or module
    #
    # then it will be skipped.

    deployments:
      - modules:
          - myapp.cfn
        regions:
          - us-west-2

      - name: terraformapp  # deployments can optionally have names
        modules:
          - myapp.tf
        regions:
          - us-east-1
        assume_role:  # optional
          # When running multiple deployments, post_deploy_env_revert can be used
          # to revert the AWS credentials in the environment to their previous
          # values
          # post_deploy_env_revert: true
          arn: ${var assume_role.${env DEPLOY_ENVIRONMENT}}
          # duration: 7200

        # Parameters (e.g. values for CFN .env file, TF .tfvars) can
        # be provided at the deployment level -- the options will be applied to
        # every module
        parameters:
          region: ${env AWS_REGION}
          image_id: ${var image_id.${env DEPLOY_ENVIRONMENT}}

        # AWS account alias can be provided to have Runway verify the current
        # assumed role / credentials match the necessary account
        account_alias: ${var account_alias.${env DEPLOY_ENVIRONMENT}}  # optional

        # AWS account id can be provided to have Runway verify the current
        # assumed role / credentials match the necessary account
        account_id: ${var account_id.${env DEPLOY_ENVIRONMENT}}  # optional

        # env_vars set OS environment variables for the module (not logical
        # environment values like those in a CFN .env or TF .tfvars file).
        # They should generally not be used (they are provided for use with
        # tools that absolutely require it, like Terraform's
        # TF_PLUGIN_CACHE_DIR option)
        env_vars:  # optional environment variable overrides
          AWS_PROFILE: ${var envvars.profile.${env DEPLOY_ENVIRONMENT}}
          APP_PATH: ${var envvars.app_path}
          ANOTHER_VAR: foo

      # Start of another deployment
      - modules:
          - path: myapp.cfn
            # Parameters (e.g. values for CFN .env file, TF .tfvars) can
            # be provided for a single module (replacing or supplementing the
            # use of environment/tfvars/etc files in the module)
            parameters:
              region: ${env AWS_REGION}
              image_id: ${var image_id.${env DEPLOY_ENVIRONMENT}}
            tags:  # Modules can optionally have tags.
              # This is a list of strings that can be "targeted"
              # by passing arguments to the deploy/destroy command.
              - some-string
              - app:example
              - tier:web
              - owner:onica
              # example: `runway deploy --tag app:example --tag tier:web`
              #   This would select any modules with BOTH app:example AND tier:web
        regions:
          - us-west-2

    # If using environment folders instead of git branches, git branch lookup can
    # be disabled entirely (see "Repo Structure")
    # ignore_git_branch: true

.. rubric:: runway.variables.yml
.. code-block:: yaml

  account_alias:
    dev: my_dev_account
    prod: my_dev_account
  account_id:
    dev: 123456789012
    prod: 345678901234
  assume_role:
    dev: arn:aws:iam::account-id1:role/role-name
    prod: arn:aws:iam::account-id2:role/role-name
  image_id:
    dev: ami-abc123
  envvars:
    profile:
      dev: foo
      prod: bar
    app_path:
      - myapp.tf
      - foo
