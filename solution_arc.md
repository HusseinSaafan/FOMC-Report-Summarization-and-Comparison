### Preprocessing
- transform pdf docs to text stored in 1 json dict

### GenAI
- create 2 prompts in prompts.py
    1) Summarization Prompt
    2) Month by month comparison

### Postprocessing
- Represent summary/findings in a single md report


### Folder/File Structure

root
    data
        raw
        json
    output
        report.md
    src
        preprocessing
            pdf_to_json.py
        genai
            summarization.py
            comparison.py
            prompts.py
        postprocessing
            generate_report.py
    .env
    .gitignore
    requirements.txt
    solution_arc.md



    