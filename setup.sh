#!/bin/bash

# Create necessary directories
mkdir -p data/sessions data/performance data/preferences data/vocabulary

# Create a simple vocabulary database
cat > data/vocabulary/default_vocabulary.json << 'EOL'
{
  "prefixes": {
    "anti-": {"meaning": "against", "examples": ["antibiotic", "antisocial"], "difficulty": 2, "origin": "Greek"},
    "co-": {"meaning": "with, together", "examples": ["cooperate", "coexist"], "difficulty": 1, "origin": "Latin"},
    "de-": {"meaning": "down, away from", "examples": ["devalue", "decrease"], "difficulty": 2, "origin": "Latin"},
    "dis-": {"meaning": "not, opposite of", "examples": ["disagree", "dislike"], "difficulty": 1, "origin": "Latin"},
    "in-": {"meaning": "not, into", "examples": ["invisible", "insert"], "difficulty": 1, "origin": "Latin"},
    "inter-": {"meaning": "between", "examples": ["interact", "international"], "difficulty": 2, "origin": "Latin"},
    "mis-": {"meaning": "wrongly", "examples": ["misunderstand", "misinterpret"], "difficulty": 1, "origin": "Old English"},
    "pre-": {"meaning": "before", "examples": ["predict", "preview"], "difficulty": 1, "origin": "Latin"},
    "re-": {"meaning": "again, back", "examples": ["return", "rewrite"], "difficulty": 1, "origin": "Latin"},
    "sub-": {"meaning": "under", "examples": ["submarine", "submerge"], "difficulty": 2, "origin": "Latin"},
    "un-": {"meaning": "not", "examples": ["unhappy", "unable"], "difficulty": 1, "origin": "Old English"}
  },
  "roots": {
    "aud": {"meaning": "to hear", "examples": ["audience", "auditory"], "difficulty": 2, "origin": "Latin"},
    "bio": {"meaning": "life", "examples": ["biology", "biography"], "difficulty": 1, "origin": "Greek"},
    "chron": {"meaning": "time", "examples": ["chronology", "chronic"], "difficulty": 3, "origin": "Greek"},
    "dict": {"meaning": "to say", "examples": ["dictate", "predict"], "difficulty": 2, "origin": "Latin"},
    "geo": {"meaning": "earth", "examples": ["geography", "geology"], "difficulty": 2, "origin": "Greek"},
    "graph": {"meaning": "to write", "examples": ["biography", "photograph"], "difficulty": 2, "origin": "Greek"},
    "log": {"meaning": "word, study", "examples": ["biology", "psychology"], "difficulty": 2, "origin": "Greek"},
    "mort": {"meaning": "death", "examples": ["mortal", "immortal"], "difficulty": 3, "origin": "Latin"},
    "path": {"meaning": "feeling, disease", "examples": ["sympathy", "pathology"], "difficulty": 3, "origin": "Greek"},
    "phil": {"meaning": "love", "examples": ["philosophy", "philanthropy"], "difficulty": 2, "origin": "Greek"},
    "scrib/script": {"meaning": "to write", "examples": ["describe", "manuscript"], "difficulty": 2, "origin": "Latin"},
    "vid/vis": {"meaning": "to see", "examples": ["video", "vision"], "difficulty": 2, "origin": "Latin"}
  },
  "suffixes": {
    "-able/-ible": {"meaning": "capable of being", "examples": ["readable", "flexible"], "difficulty": 1, "origin": "Latin"},
    "-al/-ial": {"meaning": "relating to", "examples": ["natural", "partial"], "difficulty": 2, "origin": "Latin"},
    "-ance/-ence": {"meaning": "state or quality of", "examples": ["importance", "independence"], "difficulty": 2, "origin": "Latin"},
    "-ation": {"meaning": "action or process", "examples": ["exploration", "creation"], "difficulty": 2, "origin": "Latin"},
    "-ful": {"meaning": "full of", "examples": ["beautiful", "helpful"], "difficulty": 1, "origin": "Old English"},
    "-ic": {"meaning": "relating to", "examples": ["basic", "specific"], "difficulty": 2, "origin": "Latin/Greek"},
    "-ify": {"meaning": "to make", "examples": ["simplify", "clarify"], "difficulty": 2, "origin": "Latin"},
    "-ism": {"meaning": "doctrine, belief", "examples": ["optimism", "criticism"], "difficulty": 3, "origin": "Greek"},
    "-ist": {"meaning": "one who", "examples": ["artist", "scientist"], "difficulty": 2, "origin": "Greek"},
    "-ity": {"meaning": "state or quality", "examples": ["activity", "possibility"], "difficulty": 2, "origin": "Latin"},
    "-ize": {"meaning": "to make", "examples": ["organize", "memorize"], "difficulty": 2, "origin": "Greek"},
    "-ment": {"meaning": "action or process", "examples": ["development", "statement"], "difficulty": 2, "origin": "Latin"},
    "-ous": {"meaning": "full of", "examples": ["dangerous", "famous"], "difficulty": 2, "origin": "Latin"}
  },
  "words": {
    "antibiotic": {
      "definition": "substance that can destroy or inhibit the growth of bacteria",
      "parts": [{"type": "prefix", "value": "anti-"}, {"type": "root", "value": "bio"}, {"type": "suffix", "value": "-ic"}],
      "difficulty": 3,
      "context_sentence": "The doctor prescribed an antibiotic to treat the bacterial infection."
    },
    "cooperate": {
      "definition": "work together towards a common goal",
      "parts": [{"type": "prefix", "value": "co-"}, {"type": "root", "value": "oper"}],
      "difficulty": 2,
      "context_sentence": "The two companies decided to cooperate on the new project."
    },
    "devalue": {
      "definition": "reduce or underestimate the worth or importance of",
      "parts": [{"type": "prefix", "value": "de-"}, {"type": "root", "value": "value"}],
      "difficulty": 3,
      "context_sentence": "The currency began to devalue rapidly due to inflation."
    },
    "incomprehensible": {
      "definition": "not able to be understood",
      "parts": [{"type": "prefix", "value": "in-"}, {"type": "root", "value": "comprehen"}, {"type": "suffix", "value": "-ible"}],
      "difficulty": 4,
      "context_sentence": "The scientist's theory was so incomprehensible that even his colleagues couldn't understand it."
    },
    "reticent": {
      "definition": "not revealing one's thoughts or feelings readily; reserved",
      "parts": [{"type": "root", "value": "retic"}, {"type": "suffix", "value": "-ent"}],
      "difficulty": 4,
      "context_sentence": "Despite his reticent manner in casual settings, the professor was known for his eloquent lectures."
    },
    "philanthropy": {
      "definition": "the desire to promote the welfare of others, expressed by generous donations",
      "parts": [{"type": "root", "value": "phil"}, {"type": "root", "value": "anthrop"}, {"type": "suffix", "value": "-y"}],
      "difficulty": 3,
      "context_sentence": "The billionaire's philanthropy led to the construction of several new hospitals."
    }
  }
}
EOL

# Create .streamlit directory and config file for custom theme
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOL'
[theme]
primaryColor = "#1E3A8A"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOL

echo "Setup complete! Project structure initialized."
