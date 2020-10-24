# Language-Technology-Final-Project

## Approach
Use a ```classifier``` to determine what kind of question is asked. Based on this questions type we use a ```module``` to answer that kind of question

### Classifier
The classifier searches for specific words or subtree's to determine what kind of question is being asked. And can be used by the modules to extract the entity and property from a question.
### Modules
#### X of Y
Answer a "What is the property (X) of the entity (Y)". Examples are  'What is the density of ice?',
    'What is the chemical formula for dopamine?',
    'What is the cause of Anthrax?',
    'What is the boiling point of water?',
    'What is the atomic number of silver?' and 
    'What is the field of work of CERN?'.
#### Count
e.g. How many/much property (X) of (Y)?  

#### Boolean 

#### Description 
Answers a "What is an/a/the X". Where X is an entity or property. Performs a description search on WikiData.