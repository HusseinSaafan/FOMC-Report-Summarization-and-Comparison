

### Preprocessing
- transform pdf docs to text stored in 1 json dict

### GenAI
    -prompts
        1)system prompt
        2) Summarization Prompt
        3) Month by month comparison
    summarization script
    comparison script

### Postprocessing
- Represent summary/findings in a single md report


### Folder/File Structure

root
    data
        raw
            jan.pdf
            mar.pdf
            may.pdf
            jun.pdf
            jul.pdf
            sep.pdf
            oct.pdf
            dec.pdf
        json
            docs.json
            summary_comparison.json
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



    