# CVET GitHub Cloud Data

This folder is reserved for **Crane Vehicle Engineering Tool** cloud synchronization.

Default project state path:

`cloud_data/project_state.json`

The Desktop application creates/updates that file only after GitHub Cloud Sync is enabled by the user.

## Recommended setup

Use a **private GitHub repository** for project data when you do not want engineering inputs to be public.

Create a **fine-grained personal access token** restricted to the selected repository with:

- Repository access: only the CVET data repository
- Contents: Read and write

The token is **not** stored in the synced project file. On Windows, CVET encrypts the token locally with Windows DPAPI.

## Sync behavior

- Pull/check remote state when the app starts.
- Push after local Auto Save only when engineering/project content actually changed.
- Poll for newer remote data automatically.
- Use optimistic concurrency: if this PC and GitHub both changed after the last common sync, CVET reports a **CONFLICT** instead of silently overwriting data.
- A local conflict backup is saved under `Documents/CVET_Cloud_Conflicts`.

The volatile `saved_at` timestamp is excluded from the state hash so periodic Auto Save does not create meaningless GitHub commits.
