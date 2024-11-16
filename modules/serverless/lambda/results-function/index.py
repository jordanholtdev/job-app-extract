import json
import os
import logging
import boto3
import re
import trp.trp2 as t2

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS Textract and Comprehend clients
textract = boto3.client('textract')
comprehend = boto3.client('comprehend')

# Constants for file paths
TARGET_SKILLS_FILE = 'target_skills.json'
JOB_PROFILE_FILE = 'job_profile_keywords.json'
USER_SKILLS_FILE = 'user_skills.json'
REPORT_FILE_PATH = '/tmp/job_report.html'
KEYWORDS_FILE_PATH = '/tmp/keywords.json'

class DocumentProcessor:
    def __init__(self, event):
        self.event = event
        self.document = None
    
    def process_event(self):
        status = self.event.get('Status')
        if status == 'SUCCEEDED':
            logger.info('Textract job succeeded.')
            self.document = self.get_processed_document()
            return True if self.document else False
        else:
            logger.warning(f"Textract job failed: {status}")
            return False

    def get_processed_document(self):
        return textract.get_document_analysis(JobId=self.event['JobId'])

class DocumentParser:
    def __init__(self, document):
        self.doc = t2.TDocumentSchema().load(document)
        self.keyword_list = []
        
    def parse(self):
        self.keyword_list = self.clean_keywords(self.extract_keywords())
        return {
            "query_answers": self.get_query_answers(),
            "links": self.extract_links(),
            "target_skills_score": self.compare_to_target_skills(),
            "profile_score": self.calculate_job_profile_match(),
            "keywords": self.keyword_list
        }

    def extract_keywords(self):
        return [block.text for block in self.doc.get_blocks_by_type() if hasattr(block, 'text') and block.text]

    def clean_keywords(self, keywords):
        cleaned_keywords = [keyword.strip().lower() for keyword in keywords if keyword]
        logger.info(f"Cleaned Keywords: {len(cleaned_keywords)} keywords found.")
        return cleaned_keywords
    
    def get_query_answers(self):
        page = self.doc.pages[0]
        return self.doc.get_query_answers(page=page)

    def extract_links(self):
        url_pattern = re.compile(r'https?://[^\s]+')
        links = [url for keyword in self.keyword_list for url in url_pattern.findall(keyword)]
        logger.info(f"Extracted Links: {len(links)}")
        return links

    def compare_to_target_skills(self):
        with open(TARGET_SKILLS_FILE, 'r') as file:
            known_skills = json.load(file)['target_skills']
        matching_skills = [kw for kw in self.keyword_list if kw in known_skills]
        score = len(matching_skills) / len(known_skills) * 100
        return {"score": score, "matching_skills": matching_skills}
    
    def calculate_job_profile_match(self):
        with open(JOB_PROFILE_FILE, 'r') as file:
            job_profile_keywords = json.load(file)['job_profile_keywords']
        profile_matches = set(self.keyword_list).intersection(set(job_profile_keywords))
        score = len(profile_matches) / len(job_profile_keywords) * 100
        return {"score": score, "matches": list(profile_matches)}

class ReportGenerator:
    def __init__(self, parsed_data, comprehend_results):
        self.parsed_data = parsed_data
        self.comprehend_results = comprehend_results

    def save_keywords_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.parsed_data['keywords'], file)
        logger.info(f"Keywords saved to {file_path}")

    def create_html_report(self):
        extracted_query_answers = {answer[1]: answer[2] for answer in self.parsed_data['query_answers']}        

        # Set a minimum confidence threshold
        min_score_threshold = 0.88
        high_confidence_results = []
        comprehend_keyphrase_results = self.comprehend_results.get("comprehend_results", [])
        logger.info(f"Comprehend Keyphrase Results: {len(comprehend_keyphrase_results)}")
        # iterate through the comprehend_keyphrase_results 
        for result in comprehend_keyphrase_results:
            if result.get('Score') > min_score_threshold:
                logger.info(f"Result: {result.get('Text')} - {result.get('Score')}")
                high_confidence_results.append(result)
        
        comprehend_user_skills_score = self.comprehend_results.get("user_skills_score", {})
        comprehend_job_profile_score = self.comprehend_results.get("job_profile_score", {})
        comprehend_target_skills_score = self.comprehend_results.get("target_skills_score", {})

        logger.info(f"Comprehend User Skills Score: {comprehend_user_skills_score}")
        logger.info(f"Comprehend User Skills Matching Skills: {comprehend_user_skills_score.get('matching_skills')}")
        logger.info(f"Comprehend Job Profile Score: {comprehend_job_profile_score}")
        logger.info(f"Comprehend Target Skills Score: {comprehend_target_skills_score}")
        logger.info(f"Comprehend Job Profile Matching Skills: {comprehend_job_profile_score.get('matching_keywords')}")
        logger.info(f"Comprehend Target Skills Matching Skills: {comprehend_target_skills_score.get('matching_skills')}")

        # comprehend_results_html = ''.join([f"<li>{result['Text']} (Score: {result['Score']})</li>" for result in self.comprehend_results if isinstance(result, dict) and 'Text' in result and 'Score' in result])
        high_confidence_results_html = ''.join([f"<li>{result['Text']}</li>" for result in high_confidence_results])

        report_content = f"""
        <html>
        <head><title>Job Report</title></head>
        <body>
            <h1>Job Report</h1>
            <h2>Textract Query Answers</h2>
            <ul><strong>Job Title:</strong>{extracted_query_answers.get('JOB_TITLE', '')}</ul>
            <ul><strong>Location:</strong>{extracted_query_answers.get('JOB_LOCATION', '')}</ul>
            <ul><strong>Job Posting ID:</strong>{extracted_query_answers.get('JOB_POSTING_ID', '')}</ul>
            <ul><strong>Salary:</strong>{extracted_query_answers.get('SALARY_RANGE', '')}</ul>
            <ul><strong>Company:</strong>{extracted_query_answers.get('COMPANY_NAME', '')}</ul>
            <ul><strong>Job Posting ID:</strong>{extracted_query_answers.get('COMPANY_WEBSITE', '')}</ul>
            <ul><strong>Skills:</strong>{extracted_query_answers.get('SKILLS_REQUIRED', '')}</ul>
            <h3>Textract Query Answers with Context</h3>
            <ul>{"".join([f"<li>{answer[0]}<p>{answer[2]}</p></li>" for answer in self.parsed_data['query_answers'] if answer[2]])}</ul>
            <h3>Textract Profile Match Score: {self.parsed_data['profile_score']['score']}%</h3>
            <ul>{"".join([f"<li>{match}</li>" for match in self.parsed_data['profile_score']['matches'] if match])}</ul>
            <h3>Textract Target Skills Score: {self.parsed_data['target_skills_score']['score']}%</h3>
            <ul>{"".join([f"<li>{skill}</li>" for skill in self.parsed_data['target_skills_score']['matching_skills'] if skill])}</ul>
            <h3>Textract Links</h3><ul>{"".join([f"<li><a href='{link}'>{link}</a></li>" for link in self.parsed_data['links'] if link])}</ul>
            <h3>Comprehend Keyword Analysis</h3>
            <p>High Confidence Key Phrases(>{min_score_threshold}%)</p>    
            <ul>{high_confidence_results_html}</ul>
        </body>
        </html>
        """
        with open(REPORT_FILE_PATH, 'w') as file:
            file.write(report_content)
        logger.info("Report written to file.")
        logger.info(report_content)

class ComprehendAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.keywords = []
        self.comprehend_results = []

    def load_keywords(self):
        with open(self.file_path, 'r') as file:
            self.keywords = json.load(file)
        logger.info(f"Loaded {len(self.keywords)} keywords from {self.file_path}")

    def send_to_comprehend(self):
        text = ' '.join(self.keywords)
        response = comprehend.detect_key_phrases(Text=text, LanguageCode='en')
        self.comprehend_results = response.get('KeyPhrases', [])
        logger.info("Sent keywords to Comprehend for analysis")
        logger.info(f"Comprehend response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")

    def parse_comprehend_results(self):
        parsed_results = [{'Text': phrase['Text'], 'Score': phrase['Score']} for phrase in self.comprehend_results]
        logger.info(f"Parsed Comprehend results: {len(parsed_results)}")
        return {
            "comprehend_results": parsed_results,
            "target_skills_score": self.compare_to_target_skills(),
            "job_profile_score": self.compare_to_job_profile(),
            "user_skills_score": self.compare_to_user_skills()
        }
        
    
    def compare_to_target_skills(self):
        with open(TARGET_SKILLS_FILE, 'r') as file:
            target_skills = json.load(file)['target_skills']
        matching_skills = [phrase['Text'] for phrase in self.comprehend_results if phrase['Text'] in target_skills]
        score = len(matching_skills) / len(target_skills) * 100
        return {"score": score, "matching_skills": matching_skills}

    def compare_to_job_profile(self):
        with open(JOB_PROFILE_FILE, 'r') as file:
            job_profile_keywords = json.load(file)['job_profile_keywords']
        matching_keywords = [phrase['Text'] for phrase in self.comprehend_results if phrase['Text'] in job_profile_keywords]
        score = len(matching_keywords) / len(job_profile_keywords) * 100
        return {"score": score, "matching_keywords": matching_keywords}

    def compare_to_user_skills(self):
        with open(USER_SKILLS_FILE, 'r') as file:
            user_skills = json.load(file)['user_skills']
        matching_skills = [phrase['Text'] for phrase in self.comprehend_results if phrase['Text'] in user_skills]
        score = len(matching_skills) / len(user_skills) * 100
        return {"score": score, "matching_skills": matching_skills}

class S3Uploader:
    def __init__(self, bucket_name, file_path, s3_key):
        self.bucket_name = bucket_name
        self.file_path = file_path
        self.s3_key = s3_key
        self.s3_client = boto3.client('s3')

    def upload_file(self):
        try:
            self.s3_client.upload_file(self.file_path, self.bucket_name, self.s3_key)
            logger.info(f"File uploaded to S3: s3://{self.bucket_name}/{self.s3_key}")
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {e}")


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event, indent=2))
    
    # Extract the SNS message
    sns_message = event['Records'][0]['Sns']['Message']
    message = json.loads(sns_message)
    
    processor = DocumentProcessor(message)
    if processor.process_event():
        parser = DocumentParser(processor.document)
        parsed_data = parser.parse()
        report_gen = ReportGenerator(parsed_data, [])
        report_gen.save_keywords_to_file(KEYWORDS_FILE_PATH)
        analyzer = ComprehendAnalyzer(KEYWORDS_FILE_PATH)
        analyzer.load_keywords()
        analyzer.send_to_comprehend()
        comprehend_results = analyzer.parse_comprehend_results()
        report_gen = ReportGenerator(parsed_data, comprehend_results)
        report_gen.create_html_report()
        uploader = S3Uploader(os.environ['S3_BUCKET'], REPORT_FILE_PATH, 'job_report.html')
        uploader.upload_file()
        return "Textract Job Succeeded"
    return "Textract Job Failed"