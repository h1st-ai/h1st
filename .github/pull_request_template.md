# Pull Request Checklist

Before sending your pull requests, make sure you followed this list.

- Read [contributing guidelines](CONTRIBUTING.md).
- Check if my changes are consistent with the [guidelines](TBD).
- Changes are consistent with the [Coding Style](TBD).
- Run [Unit Tests](TBD).

Checklist for Pull Request
- Describe what this PR purpose. For example, for new features describe what problem this PR solves. If there is JIRA task, please include JIRA link. 
- When there are more than one tasks in the PR, use to do list in github mark down. 
- Include unit tests. If small test files are needed for your unit tests, please include them as well. Be conservative in adding test files, try to make them small and local instead of putting it on S3 or external database.
- Assign reviewer.


# Running unit tests
Using tools and libraries installed directly on your system.
   For example, to run all tests under graphengine, do:

   ```bash
   nose2
   ```

