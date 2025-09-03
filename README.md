# CalFire Incident Data Analysis

A comprehensive data analysis pipeline for California wildfire incidents using CalFire's public dataset. This project provides automated data collection, cleaning, storage, and exploratory data analysis (EDA) with intelligent database fallback mechanisms.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)

## Overview

California experiences some of the most severe and frequent wildfires in the United States. With the current tides of climate change, population growth, and developing land uses, understanding patterns of wildfire activity is becoming an increasingly important consideration for the residents and government of California. To better understand these patterns and support proactive decision-making, this project focuses on trend forecasting and analysis using historical incident data provided by CAL Fire as well as precipitation data provided by California Department of Water Resources.

The project integrates data analytics to explore wildfire behavior, identify risk factors, and generate insights. The workflow begins with acquiring raw incident data directly from CAL FIRE's public databases, followed by data cleaning, transformation, and storage in a relation database for efficient querying. Exploratory data analysis (EDA) highlights temporal, geographic, and environmental patterns to allow for further insights.

The end product is a data pipeline and interactive dashboard that automatically updates with new incident data, delivering actionable insights to fire management agencies, policymakers, and researchers. This allows stakeholders to track wildfire activity in realtime, monitor trends, and simulate future scenarios to improve preparedness, resource allocation, and public safety.

This notebook serves as the back-bone of this project's workflow. While all dashboards, visualizations, and metrics can be viewed by running the core Python file, this notebook keeps track of the ins-and-outs of the decision-making behind the analysis.

### Key Capabilities
- **Automated Data Collection**: Downloads latest incident data from CalFire's public CSV endpoint
- **Smart Data Storage**: Optional Google Cloud PostgreSQL integration with automatic fallback
- **Data Cleaning**: Handles outliers, missing values, and geographic coordinate validation
- **Exploratory Data Analysis**: Comprehensive statistical analysis and visualizations

## Features

### Data Management
- **Automatic Data Updates**: Fetch latest CalFire incident data on-demand
- **Dual Storage Options**: PostgreSQL database or local DataFrame
- **Intelligent Fallback**: Automatically switches to direct download if database is unavailable
- **Data Cleaning Pipeline**: Automated handling of missing values and outliers

### Analysis Capabilities
- **Statistical Analysis**: Comprehensive EDA with descriptive statistics
- **Geographic Validation**: California boundary checking for coordinates
- **Outlier Detection**: IQR-based outlier handling for numerical variables
- **Visualizations**: Before/after comparisons, distributions, and trends

## Installation

### Prerequisites
- Python
- Jupyter Notebook or JupyterLab
- (Optional) Google Cloud account with PostgreSQL instance

### Required Libraries

```bash
pip install pandas numpy matplotlib sqlalchemy pg8000 google-cloud-sql-connector
```

### Clone Repository

```bash
git clone https://github.com/yourusername/calfire-analysis.git
cd calfire-analysis
```
## 🗄️ Database Configuration

### Google Cloud PostgreSQL Setup

1. **Create Instance**: Set up a PostgreSQL instance in Google Cloud Console
2. **Get Connection String**: Format: `project:region:instance`
3. **Set Credentials**: Create user with appropriate permissions
4. **Configure Access**: Ensure your IP is whitelisted

### Connection Parameters

```python
# Example configuration
config = {
    'instance_connection_name': 'project-id:us-west1:instance-name',
    'db_user': 'postgres',
    'db_pass': 'your-secure-password',
    'db_name': 'calfire_db'  # Created automatically
}
```

## Analysis Features

### Available Data Fields
In the dataset provided by [CAL FIRE](https://www.fire.ca.gov/), detailed records of wildfire incidents across California are made publicly available. The data can be accessed directly through CAL FIRE's open data portal [here](https://incidents.fire.ca.gov/imapdata/mapdataall.csv), which is updated regularly to reflect both active and historical incidents.

This dataset includes a number of attributes, but the ones we will be focusing on are:
Variable|Description |
-----|-----|
incident_name | The official name or title of the wildfire incident.|
incident_date_created | The date and time when the incident was first reported or created in the system.|
incident_administrative_unit | The CAL FIRE administrative unit or agency responsible for managing the incident.|
incident_county | The county in California where the incident occurred.|
incident_location | A descriptive location of the incident, such as city, town, or nearby landmark.|
incident_acres_burned | The total number of acres burned during the incident.|
incident_containment | The percentage of the fire that has been contained at the time of reporting.|
incident_cooperating_agencies | Other local, state, or federal agencies assisting with the incident response.|
incident_longitude | The longitude coordinate of the incident’s location.|
incident_latitude | The latitude coordinate of the incident’s location.|
incident_id | A unique identifier assigned to each incident (string or numeric).|
incident_url | A direct link to the CAL FIRE incident webpage for more details.|
incident_date_extinguished | The date and time when the incident was declared fully extinguished.|
is_active | Status flag indicating whether the incident is still active or has been contained/closed. |
calfire_incident | Boolean value indicating whether the incident was directly managed by CAL FIRE. |

In the dataset provided by the California Department of Water Resources using Government of California's API, detailed records of monthly precipitation levels for each County across California are made publicly available. The link to the API can be found [here](https://lab.data.ca.gov/dataset/annual-precipitation-data-for-northern-california-1944-current/c66bcc83-d895-48cf-a639-a53974899b88).

This dataset includes a number of attributes, but the ones we will be focusing on are:
Variable|Description |
-----|-----|
incident_name | The official name or title of the wildfire incident.|
precip_date | The datetime in which the record comes from. |
precip_inches | The total inches of precipitation in each county, in each month. |
precip_month | Number equating to the month of the year. |
county | The county from which the record is referring to.


### Key Analyses Included

1. **Temporal Analysis**: Fire frequency and duration trends
2. **Geographic Distribution**: County-level incident mapping
3. **Severity Metrics**: Acres burned and containment analysis
4. **Outlier Detection**: Statistical anomaly identification
5. **Data Quality**: Missing value and coordinate validation


