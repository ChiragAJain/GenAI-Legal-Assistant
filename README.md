# Terms and Condition Summariser
This software engineering project helps summarise a terms and condition `.pdf` and `.txt` file to `.pdf` file with simplified legal jargon with custom word limit for each paragraph such that users of any background can understand the Terms and Conditions and face no unexpected clauses.

## Models
  pre-trained [Legal Pegasus model](https://huggingface.co/nsi319/legal-pegasus)
<hr>

## Model Piperline
The text from the `.pdf` file is extracted and fed to the pegasus model with minimum and maximum word limit for each paragraph, along with heading lookups which it uses to segregate the text under respective headings while giving the summarised file.
The legal-pegasus model extracts essential clauses from the terms and conditions file and rephrases them without changing the meaning of it. <br>
This modified text is then forwarded to [KeyBert](https://pypi.org/project/keybert/) which replaces high vocabulary words with everyday used words. <br>
The text is then written into a `.pdf` file and given out as an output. The text is visible on the output page with an option to download the `.pdf` file.

## Web-Application
The web application with a modular and scalable Flask-based backend is locally hosted with a simple and static front-end with an option to provide feedback which is stored in a JSON file.

## Contribution
The application is free to use and exprementation and open to any modification required.<br>
If used for a project, the developers must appropriately credit the original developers of this web application and the fine-tuned pegasus model.

