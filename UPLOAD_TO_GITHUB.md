# Upload this project to the existing GitHub repository

Your repository URL is: https://github.com/premanand404/spacex-data-science-capstone

## Browser-based upload

1. Download `SpaceX_Falcon9_Capstone_GitHub_Repository.zip` and extract it.
2. Open the existing repository above and click **Add file → Upload files**.
3. Upload the project contents: `notebooks/`, `src/`, `presentation/`, `requirements.txt`, `run_all.py`, `.gitignore`, and `README.md`. If GitHub asks about overwriting `README.md`, use the project README so it describes the actual files.
4. Commit the changes to the `main` branch.
5. Refresh the repository page and confirm the notebook and source folders are visible before copying the repository URL into Coursera.

## Git commands (alternative)

Clone the repository, copy the extracted bundle's contents into the cloned folder (not an extra nested project folder), then run:

```bash
git add .
git commit -m "Add SpaceX capstone notebooks and analysis scripts"
git push origin main
```

The scripts download course CSVs on first run, so a working internet connection is required to execute the full workflow. Review the generated metrics against your own notebook outputs before presenting them as your own run results.
