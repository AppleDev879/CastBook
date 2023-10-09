# CastBook

## Background
Some film sets require workers to keep in contact with other workers on the set, but the process of adding users from the call sheet PDF's into an address book is manual and time-consuming. I built a Python-based PDF parser that takes a PDF as input and performs Named Entity Recognition (NER) using SpaCy to detect names, phone numbers, and email addresses of set workers and export them as JSON data which can be read through a companion mobile app. The mobile app can then do the work of adding people to address books.

## Project Details
The project was designed to run on AWS lambda, but due to the size of the language model SpaCy uses, it became necessary to deploy it using Fargate or EC2, since Lambda has a 50 MB limit for compressed source code.

## Architecture + Data Flow
1. User uploads a PDF to a S3 bucket via a temporary upload link. The temporary upload link can be gotten by GETing the lambda function in `/preprocess`.
2. User makes a POST request to the processing engine, supplying the name of the file in S3 in the request. This POST returns a JSON list of all the contacts in the PDF.
3. The user parses the JSON data on device/web browser and lets the user add each contact to their address book.

## Privacy Concerns
Towards the end of development I started asking for potential beta testers to contribute their own call sheets to the project and got considerable pushback due to NDA's they had signed with the filmmakers. As such, I'm choosing to open source the parser so that independent filmmakers and developers can use it privately without the fear that their data will be shared.
