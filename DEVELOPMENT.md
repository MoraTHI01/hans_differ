# Development

In the following sections the development workflow for the project is described.

## Branches

We use 2 central branches for our development.

### main

The production branch.

The branch is production ready and protected.
It is stable during the complete development lifecycle.

### dev

The main development branch.

Feature branches are integrated into this branch.
After all tests are passed a pull request is created for integrating the latest `dev` revision into the `main` branch.


## Workflow

- Important: The main branch is always stable!

- To develope a new feature create a feature branch from the `dev` branch; prefix the branch with `feature/YYYY-MM-DD-`

  - Example:

 ```bash
git checkout -b feature/2022-06-09-your-feature origin/dev
 ```

- To work on bug- or hotfixes, prefix your branch with `{bug,hot}fix/YYYY-MM-DD-<issue-number>`;
  note: hotfixes will be rare, since they typically apply to problems on `main` and will be merged to main

- Develop your feature and commit with appropriate commit messages on your local branch

  - Example:

```bash
git add SOME-FILE.js
git commit -m "Added SOME-FILE to handle auth requests"
```

- For your first push you need to create the upstream branch on the remote repository:

  - Example:

```bash
git push -u origin feature/2022-06-09-your-feature
```

- Afterwards you can use `git push` to push the next upcoming commits without specifying the upstream until
  your feature is ready to be integrated.

- Features are integrated using pull requests into the `dev` branch on
  [HAnS GitHub repository](https://github.com/th-nuernberg/hans/pulls)

  - Important: Each pull request needs at least one successful review, without any major findings,
    feel free to add more reviewers if needed.

### Pre-commit hooks

To ensure that your code is formatted consistently, it is recommended to use
[pre-commit hooks](https://pre-commit.com/).
To install the pre-commit package manager and set up the git hook scripts, run:
```bash
pip install pre-commit
pre-commit install
```
Alternatively to pip, you can use `brew` or `conda` (see [Installation guidelines](https://pre-commit.com/#installation))
For markdownlint-cli2 you need to have the Node Package Manager (npm) installed locally.
Npm gets installed along with `Node.js`, which can be installed using e.g. `brew install node`.

If you now run `git commit`, your commited code will be checked by the pre-commit hooks.
If checks fail, your commit will be aborted.
In this case, modify your code according to the error message of the pre-commit check and commit again
(some tools like `black` perform the code formatting automatically - then just re-add and re-commit).
In case you want to skip the pre-commit checks, you can use the `--no-verify` flag with `git commit`:
`git commit -m "feat: my changes" --no-verify`.

To see which hooks are currently added, have a look at the [.pre-commit-config.yaml](.pre-commit-config.yaml)

**Integrate formatters in code editor:**
- For `black`: see [editor integration](https://black.readthedocs.io/en/stable/integrations/editors.html)
  (for PyCharm also [BlackConnect plugin](https://plugins.jetbrains.com/plugin/14321-blackconnect))
- For `prettier`: see [formatting notes in frontend/README.md](./frontend/README.md#vue)

## Testing

### Load Tests

With load tests, you can test the behavior of the HAnS deployment under heavy user load.

The directory [dev/load_test](dev/load_test) contains a basic load test,
which creates virtual users that login and open a video view.

Before performing this test, ensure the configuration fits your needs.
The default config is included in [dev/load_test/.env.template](dev/load_test/.env.template).
If you want to change some values, copy the template file to a
new file `dev/load_test/.env.config` and modify the env variable values:
- `LOCUST_HOST`: Host website of HAnS, that should be tested
- `TEST_VIDEO_UUID`: Uuid of the video to be called in test (uuid can be found in video link)
- `LOCUST_USERS`: Peak number of concurrent virtual users
- `LOCUST_SPAWN_RATE`: Number of users created per second, until peak number of users is reached
- `LOCUST_RUN_TIME`: Time how long the test will run (e.g. 30s, 5m, 1h)

Run the test:
```sh
bash dev/load_test/run_load_test.sh -u my_username -p 'my_password'
```
with the parameters
- `-u`: Username for logging in to HAnS website
- `-p`: Password for username

The test generates an html report under `dev/load_test/report`,
which is named after the date and time of the load test.
