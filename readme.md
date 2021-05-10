# Simplification Interface
This contains the code used to generate the data for evaluating end-to-end lexical simplification models.

This repo is split into two sections:
- `data-collection` - A set of python scripts used to generate data, generate substitutes from the initial CWI annotations and generate diagrams. It contains three scripts:
    - `generate_data.py` - See `data-collection/readme.md` for a description. **NOTE:** The inital data for the project has already been generated and is in `annotation-interface/data/data_CWI.json`
    - `cwi_output_to_substitution.py` - Given a folder containing the `.bin` output files from the CWI annotations, it generates a `data_RANKER.json` file which can be used.
    - `generate_diagrams.py` - Uses the generated data to create plots showing statistics about the data for the technical paper.
- `annotation interface` - Used, along with GitHub Pages, to server the data to be annotated. There's no backend server, everything is done through static web pages.

**NOTE:** *When the CWI annotations are done, they MUST be run through `cwi_output_to_substitution.py` and the resulting `data_RANKER.json` file MUST be uploaded to `annotation-interface/data` so that the substitution selection annotation can work properly. This python script generates the substitutes that will then be annotated. Currently the repo has a demo `data_RANKER.json` file*