###############
Release Process
###############

Steps that should be taken when preparing for and executing a release.


***********
Preparation
***********

1. Merge all PRs that should be included in the release.

2. Open a **draft PR**. This should have *master* as the source and *release* as the target.
   The PR should be labeled as *release*.

3. Integration tests should be triggered automatically by opening the PR.
   Wait for the tests to complete before continuing.

.. important:: Only one instance of each test should be run at a time.
               Either cancel any running test or wait for them to finish before
               committing/merging anything new to *master* which will trigger
               a new instance of each test to begin.

4. Fix any failing integration tests.

5. Close the PR.

6. Fetch updates for all branches of the **onicagroup/runway** remote.
   (e.g. ``git fetch --all``)

7. Checkout the *master* branch from the **onicagroup/runway** remote.
   This is to ensure your local *master* branch matches the correct remote.
   (e.g. ``git checkout -b master --track <remote>/master``)

8. Apply a version bump where necessary (CHANGELOG.md, etc)

9. Commit any changes to *master*.

10. Push the commits to the **onicagroup/runway** remote.
    (e.g. ``git push <remote> master``)


*********
Execution
*********

1. Fetch updates for all branches of the **onicagroup/runway** remote.
   (e.g. ``git fetch --all``)

2. Checkout the *master* branch from the **onicagroup/runway** remote.
   This is to ensure your local *master* branch matches the correct remote.
   (e.g. ``git checkout -b master --track <remote>/master``)

3. Checkout the *release* branch from the **onicagroup/runway** remote.
   (e.g. ``git checkout -b release --track <remote>/release``)

4. Execute ``git merge --ff-only master`` to fast forward the branch.

5. Push the changes to the **onicagroup/runway** remote.
   (e.g. ``git push <remote> release``)

6. Create a tag on the *release* branch for the new version.
   This can be done one of two ways:

- Navigate to the **Releases** section of the repository on GitHub.
  The should be a *Draft Release* already started that was automatically generated from PRs that were merged since the last release.
  Editing the draft will give provide the option to create a new tag for the release.

- Create a signed tag on the *release* branch for the new version and push it to the **onicagroup/runway** remote

.. code-block:: shell

  git tag --sign v0.0.0
  git push <remote> v0.0.0

7. Navigate to the **Releases** section of the repository on GitHub and edit the *Draft Release* if you have not done so already.

8. Rename the release to match the version tag and associate it with the tag that was just created.

9. Edit the description of the release as needed but, there should be little to no changes required if all PRs were properly labeled.

10. Mark the release as a *pre-release* if applicable (alpha, beta, release candidate, etc).

11. Publish the release on GitHub.


At this point, GitHub Action will begin building the deployment packages & automatically publishing them to npm, PyPi, and AWS S3.
The **Publish Release** workflow can be monitored for progress.

.. This is kind of optional since it has yet to be done but, it would be great to have this automated before 2.0 if possible

After all the publishing steps have completed:

12. Download the following artifacts from the **Publish Release** workflow:

- npm-pack
- pyinstaller-onefile-macos-10.15
- pyinstaller-onefile-ubuntu-18.04
- pyinstaller-onefile-windows-latest
- pypi-dist

13. Attach all artifacts to the release that were previously downloaded.
