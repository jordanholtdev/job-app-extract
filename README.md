# Job Posting Analyzer Application

## Description

This repository contains Terraform infrastructure code designed to deploy a serverless architecture for a job posting extraction and analysis application on AWS. The application enables users to upload job postings in PDF format, which are then processed through Amazon Textract and Amazon Comprehend for analysis.

### Key Features:

- **Serverless Architecture:** Utilizes AWS Lambda functions to handle the logic of the application without the need for managing servers.
- **Automated Processing:** Upon uploading a job posting, the application automatically triggers a series of processes:
    - **Keyword Extraction:** Amazon Textract extracts relevant keywords and predefined queries from the job posting.
    - **Skills Matching:** Extracted keywords are compared against user-defined and target skills, as well as job profile keywords to determine job suitability.
    - **Natural Language Processing:** Natural Language Processing: Amazon Comprehend analyzes the keywords, filtering results based on confidence thresholds.
- **HTML Reporting:** The application generates an HTML report summarizing the analysis results, which is saved to an S3 bucket for easy access.

This project originated from my desire to streamline and automate my job hunting process. I wanted to create an efficient way to analyze job postings and match them with my skills, making the application of jobs more effective and less time-consuming.

## Getting Started

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have met the following requirements:

-   **[Terraform](https://www.terraform.io/downloads.html):** Install Terraform on your local machine. 
-   **[AWS Account](https://aws.amazon.com/):** Set up an AWS Account and configure your AWS credentials. 
- **Git:** Ensure you have Git installed on your local machine

### Installation

1. Clone the repository: `git clone https://github.com/jordanholtdev/job-app-extract`
2. Change into the project directory: `cd job-app-extract`
3. **Create a `terraform.tfvars` file.** Create a terraform.tfvars file in the dev directory of the project to specify your variable values. For example:

```
region = "us-east-1"
profile = "default"
env = "dev"
source_bucket_name = "your-source-bucket-name"
processed_bucket_name = "your-processed-bucket-name"
tags = {
  project = "job-posting-analyzer"
  owner = "your-name"
}
```
4. **Initialize Terraform:** Initialize the Terraform working directory, which will download the necessary provider plugins.
`terraform init`

5. Modify the `variables.tf` file to configure the desired infrastructure settings. 

6. **Apply the Terraform Configuration:** Apply the Terraform configuration to create the infrastructure.


## Usage

1. **Upload Job Posting:**
    - Start by uploading a job posting in PDF format to the designated S3 bucket.
2. **Trigger First Lambda Function:**
    - The first Lambda function is automatically triggered upon upload. It sends the job posting to Amazon Textract.
    - Textract Process:
        - Textract extracts keywords and retrieves predefined queries from the job posting.
3. **Receive Textract Notification:**
    - Once Textract completes its processing, it sends a notification to an SNS (Simple Notification Service) topic.
4. **Trigger Second Lambda Function:**
    - The second Lambda function is triggered by the SNS notification.
    - **Processing Results:**
        - Extracted keywords are saved to a file and compared against a list of user-defined skills, job profile keywords, and target skills to assess job suitability.
        - Keywords are also sent to Amazon Comprehend for further analysis, filtered based on a high confidence threshold.
        - Comprehend results are compared with the user-defined skills, job profile keywords and target skills list.
5. **Generate HTML Report:**
    - An HTML report summarizing the results is created and saved back to the S3 bucket for easy access.

**Notes:**
- Customize the list of user-defined skills, job profile and target skills according to your needs for accurate matching.
    
