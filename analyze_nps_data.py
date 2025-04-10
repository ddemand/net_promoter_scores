import pandas as pd
from openai import OpenAI
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


# ====== Get API key
def get_api_key(api_name):
    file_path = "/Users/daviddemand/PycharmProjects/api_keys/api_creds.json"
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for api in data['api_keys']:
                if api['api_name'] == api_name:
                    return api['api_key']
            print(f"No API key found for '{api_name}'")
            return None
    except FileNotFoundError:
        print(f"Error: API keys file not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in API keys file")
        return None
    except Exception as e:
        print(f"Error reading API keys: {e}")
        return None


# ====== xAI Grok3 API setup
api_key = get_api_key("xai_api_key")
if not api_key:
    raise Exception("API key not found. Exiting.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)


# ====== Function to analyze NPS data
def analyze_nps_data(df):
    """
    Analyze NPS data and return a summary with top positive and negative insights.

    Args:
        df (pd.DataFrame): DataFrame with 'NPS Score' (1-5) and 'Customer Response' columns

    Returns:
        dict: JSON-parsed result with 'summary', 'top_positive', 'top_negative'
    """
    if 'NPS Score' not in df.columns or 'Customer Response' not in df.columns:
        raise ValueError("DataFrame must contain 'NPS Score' and 'Customer Response' columns")

    nps_summary = df['NPS Score'].value_counts().sort_index().to_dict()
    responses = df[['NPS Score', 'Customer Response']].to_dict(orient='records')

    prompt = f"""
    I have a DataFrame with customer feedback data. The 'NPS Score' column ranges from 1 (highest, most positive) to 5 (lowest, most negative). The 'Customer Response' column contains comments explaining their sentiment. Here’s the data:

    NPS Score Distribution: {json.dumps(nps_summary, indent=2)}
    Customer Responses: {json.dumps(responses, indent=2)}

    Please provide:
    1. An overall summary of the current customer sentiment based on the NPS scores and responses.
    2. The Top 3 reasons the business is doing great (based on positive feedback, NPS 1-2).
    3. The Top 3 items where the business needs to improve (based on negative feedback, NPS 4-5).
    Return your response in JSON format with keys: 'summary', 'top_positive', 'top_negative'.
    """

    try:
        completion = client.chat.completions.create(
            model="grok-3-beta",
            messages=[{"role": "user", "content": prompt}]
        )
        response_message = completion.choices[0].message.content
        result = json.loads(response_message)
        return result
    except json.JSONDecodeError as je:
        print(f"JSON Parsing Error: {je}")
        print(f"Raw response: {response_message}")
        raise
    except Exception as e:
        print(f"API Error: {e}")
        raise


# ====== Function to generate PDF report
def generate_pdf_report(result, output_path="nps_summary_report.pdf"):
    """
    Generate a PDF report from the NPS analysis results in an executive-friendly format.

    Args:
        result (dict): Dictionary with 'summary', 'top_positive', 'top_negative'
        output_path (str): Path to save the PDF file
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72,
                            bottomMargin=18)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20,
                                 textColor=colors.black)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceBefore=12,
                                   spaceAfter=10,
                                   textColor=colors.darkgray)
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=12, spaceAfter=8)

    # Build the report content
    story = []

    # Title and date
    story.append(Paragraph("Customer Sentiment Analysis Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 12))

    # Overall Summary
    story.append(Paragraph("Overall Customer Sentiment Summary", heading_style))
    summary_dict = result.get('summary', {})
    if isinstance(summary_dict, dict):
        summary_text = summary_dict.get('overall_sentiment', 'No summary provided')
    else:
        summary_text = str(summary_dict)  # Fallback if not a dict
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 12))

    # Top Positive Reasons
    story.append(Paragraph("Top 3 Reasons We Are Doing Great", heading_style))
    top_positive = result.get('top_positive', [])
    if not isinstance(top_positive, list):
        top_positive = [top_positive]
    for i, item in enumerate(top_positive[:3], 1):
        if isinstance(item, dict):
            reason = item.get('reason', 'Unknown reason')
            description = item.get('description', '')
            text = f"{i}. <b>{reason}</b>: {description}"
        else:
            text = f"{i}. {str(item)}"  # Fallback if not a dict
        story.append(Paragraph(text, body_style))
    story.append(Spacer(1, 12))

    # Top Negative Items
    story.append(Paragraph("Top 3 Items Needing Improvement", heading_style))
    top_negative = result.get('top_negative', [])
    if not isinstance(top_negative, list):
        top_negative = [top_negative]
    for i, item in enumerate(top_negative[:3], 1):
        if isinstance(item, dict):
            reason = item.get('reason', 'Unknown issue')
            description = item.get('description', '')
            text = f"{i}. <b>{reason}</b>: {description}"
        else:
            text = f"{i}. {str(item)}"  # Fallback if not a dict
        story.append(Paragraph(text, body_style))

    # Build the PDF
    try:
        doc.build(story)
        print(f"PDF report saved to: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


# ====== Example usage
try:
    df = pd.read_csv('nps_data.csv')
except FileNotFoundError:
    print("Error: 'nps_data.csv' not found. Using sample data instead.")

try:
    result = analyze_nps_data(df)
    print("Overall Customer Sentiment Summary:")
    print(result['summary'])
    print("\nTop 3 Reasons We Are Doing Great:")
    for i, reason in enumerate(result['top_positive'], 1):
        print(f"{i}. {reason}")
    print("\nTop 3 Items Needing Improvement:")
    for i, reason in enumerate(result['top_negative'], 1):
        print(f"{i}. {reason}")
    generate_pdf_report(result)
except Exception as e:
    print(f"Error during analysis or PDF generation: {e}")