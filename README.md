![License](https://img.shields.io/badge/License-MIT-blue.svg)   ![Airflow Version](https://img.shields.io/badge/Airflow-2.2.4-blue)  ![Docker Image Version](https://img.shields.io/docker/v/apache/airflow/latest)  


# The Data Observation Toolkit (DOT)
In 2019, the United Nations Statistical Commission highlighted the critical role of accurate health data, stating, _“Every misclassified or unrecorded death is a lost opportunity to ensure other mothers and babies do not die in the same way. When it comes to health, better data can be a matter of life and death.”_ In response, **DataKind** developed DOT to increase trust in public health data, which is essential for equitable, data-driven health service delivery and optimized policy responses. DOT was created in collaboration with our global network of frontline health partners, including Ministries of Health, frontline health workers, and funders, all working together to strengthen health systems worldwide.
You can read more of this initiative in the articles below:
  -	[Pathways to Increasing Trust in Public Health Data](https://chance.amstat.org/2021/09/pathways/ "Pathways to Increasing Trust in Public Health Data")
  -	[Empowering Health Worker and Community Health Systems: Data Integrity and the Future of Intelligent Community Health Systems in Uganda](https://www.datakind.org/blog/empowering-health-workers-and-community-health-systems "Empowering Health Worker and Community Health Systems: Data Integrity and the Future of Intelligent Community Health Systems in Uganda")
  -	[Harnessing the power of data science in healthcare](https://anchor.fm/medxtekafrica/episodes/Ep19---Harnessing-the-power-of-data-science-in-healthcare-e1iijkm "Harnessing the power of data science in healthcare")
  -	[How Data Empowers Health Workers—and Powers Health Systems](https://chwi.jnj.com/news-insights/how-data-empowers-health-workers-and-powers-health-systems "How Data Empowers Health Workers—and Powers Health Systems")

The **Data Observation Toolkit (DOT)** is designed to monitor data and flag potential issues related to data integrity. It can identify problems such as missing or duplicate data, inconsistencies, outliers, and even domain-specific issues like missed follow-up medical treatments after diagnosis. DOT features a user-friendly interface for easily configuring powerful tools like the **DBT** and **Great Expectations** libraries, along with a built-in database for storing and classifying monitoring results.
The primary goal of DOT is to make data monitoring more accessible, allowing users to ensure high-quality data without requiring extensive technical expertise. – Below is a high overview of the tool and how is architected:
 <figure style="text-align:center;">
   <figcaption> DOT high overview </figcaption>
   <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e650c78dc73b3842766d87d74f56701adb4019ff/images/dot.png" alt=" dot_overview " />
</figure>

<figure style="text-align:center;">
   <figcaption>DOT Architecture</figcaption>
   <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e650c78dc73b3842766d87d74f56701adb4019ff/images/dot_architecture.png" alt="dot_acrh" />
</figure>

### General Configuration Pre-requisites:
To run DOT you will need to:
1.	Install Python [3.8.9](https://www.python.org/downloads/release/python-389/)  
2.	Install the necessary python packages by running the following commands in your terminal ([Additional information Mac/Linux terminal](https://support.apple.com/guide/terminal/open-or-quit-terminal-apd5265185d-f365-44cb-8b09-71a064a42125/mac#:~:text=On%20your%20Mac%2C%20do%20one,%2C%20then%20double%2Dclick%20Terminal.), [additional information Windows terminal](https://learn.microsoft.com/en-us/windows/terminal/)):
     - `pip install gdown`
     - `pip install python-on-whales`
3.	Install [Docker desktop](https://www.docker.com/products/docker-desktop/). First make sure you have checked the [Docker prerequisites](https://github.com/datakind/medic_data_integrity/tree/main/docker#pre-requisites). We recommend using at least 4GB memory which can be set in the docker preferences, but this can vary depending on the volume of data being tested
4.	If running on a Mac M1/M2 chip, install [Rosetta](https://support.apple.com/en-us/HT211861) and set export DOCKER_DEFAULT_PLATFORM=linux/amd64 in the terminal where you will run the instructions below
5.	(Windows Users only) Need to install WSL for Linux on Windows Pcs

Alternatively, you can use the provided  [environment.yml](./environment.yml) if you have [miniconda](https://docs.conda.io/en/latest/miniconda.html)  installed.

_After completing the software prerequisites for your operating system, **download or clone the DOT repository** to your computer. **You will need this repository for all the setups listed below.**_

 ### Configuration (work in progress)
The following sections provide step-by-step instructions for configuring various components of DOT:
-	[Getting Started with DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/07a44ca01526679912a04e0f20bb6364134cdaf7/documentation_DOT/gettingstartedDOT.md)
-	[Setting Up the Docker Environment and Running DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e95231bdaf4c8410633b298ac246173b061dbe52/documentation_DOT/setuandrunDOTonDocker.md)
-	[Deploying DOT to Airflow](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/72a3bb7a36fbfc69b621180fd52034dc99d1ee86/documentation_DOT/airflowdeployment.md)
- [Configuring the DOT Database](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/b70d3e044858387443698354b0c4253a6b618b17/documentation_DOT/configuringDOTdb.md)
- [DBT for DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/3c59ddd5c284bc07dc8428e039655827cb736ad5/documentation_DOT/DBTforDOT.md)
- [Configuring DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/a22c4858caf890bd3fbb4a6d98e9aa12c38cbd4e/documentation_DOT/configuringDOT.md)
-	[Developing the Appsmith UI](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/d9845f8228bb147af7f28f7a300a68012e9b51ed/documentation_DOT/developingappsmith.md)
-	[Advanced Topics](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/cb6796d15e46c209e8d08b0d3984bfb6cb9d262d/documentation_DOT/AdavanceTopics.md#adding-more-projects-to-airflow)


### Sample data
Explore [these comprehensive datasets](https://drive.google.com/drive/folders/12tyTqYNNNpDZxQKMQqv7FVOCq18LCurQ?usp=sharing), including global COVID-19 data, U.S. childhood obesity records, and datasets ranging from 1,000 to over a million patient entries, along with a synthetic dataset demonstrating DOT's capabilities with frontline health data.

## Guidelines for adding new tests
*	Existing tests are at [the self-tests folder](dot/self_tests/unit)
*	All tests extend the [test base class](dot/self_tests/unit/base_self_test_class.py) that
    -	facilitates the import of modules under test
    -	recreates a directory in the file system for the test outputs
    -	provides a number of function for supporting tests that access the database, mocking the config files to point to the test [dot_config.yml](dot/self_tests/data/base_self_test/dot_config.yml), (re)creates a schema for DOT configuration and loads it with test data, etc.

## Code quality
We have instituted a pair of tools to ensure the code base will remain at an acceptable quality as it is shared and developed in the community.
1.	The [formulaic python formatter “black”](https://pypi.org/project/black/). As described by its authors it is deterministic and fast but can be modified. We use the default settings, most notably formatting to a character limit of 88 per line.
2.	The [code linter pylint](https://pylint.org/). This follows the [PEP8](https://peps.python.org/pep-0008/) style standard. PEP8 formatting standards are taken care of in black, with the exception that the default pylint line length is 80. Pylint is also modifiable and a standard set of exclusion to the PEP8 standard we have chosen are found [here](https://github.com/datakind/medic_data_integrity/blob/main/.pylintrc). We chose the default score of 7 as the minimum score for pylint to be shared.
The combination of black and pylint can be incorporated into the git process using a pre-commit hook by running setup_hooks.sh


_For detailed information on advanced configuration options and guidelines for contributing to the project, please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) document._

----
----