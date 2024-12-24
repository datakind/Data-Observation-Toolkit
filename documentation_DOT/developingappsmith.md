# Developing the Appsmith UI

Clicking **'Edit'** on the imported app enables you to modify the app’s design. For more details, visit the Appsmith help site.

Key points to note:

  -  Validation, defaulting, and tooltips are controlled via the Database whenever possible. For more details, refer to the Queries section.
  - The test_parameters JSON generates a form. Please be aware that regenerating it can reset many settings. This process was set up only once, so if you click "regenerate," it will remove some customizations. While I have submitted a feature request to Appsmith to create fields with default types, values, and validation functions, for now, new fields need to be added manually. However, you might be able to restore the logic in bulk by reviewing the raw Appsmith app JSON file.

## Updating to the Latest Version of Appsmith
Appsmith releases regular bug fixes and enhancements. By default, the DOT Docker build updates automatically. To manually update Appsmith, follow these steps:

1. In your terminal, run the following command to stop the container:
   ```bash
   docker-compose -f docker-compose-with-appsmith-ui.yml stop
   ```
2. Remove the current Appsmith container:
   ```bash
   docker rm appsmith
   ```
3. Download the latest version of the docker-compose.yml file into a clean directory:
   ```bash
   curl -L https://bit.ly/32jBNin -o $PWD/docker-compose.yml
   ```
4. Pull the latest Docker images, remove any previous containers, and start the new container:
   ```bash
   docker-compose pull && docker-compose rm -fsv appsmith && docker-compose up -d
   ```
5.Restart Appsmith in the directory where your Docker Compose file is located:
   ```bash
   docker-compose -f docker-compose-with-appsmith-ui.yml up -d
   ```
**Note:** These steps will remove your saved configuration and app. Make sure to back up any important data before proceeding.